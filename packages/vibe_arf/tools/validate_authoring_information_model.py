#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict,deque
from pathlib import Path
import yaml

EDGE_TYPES={'provided_by','derived_from','validated_by','approved_by','consumed_by','materializes','invalidates','packages','depends_on'}
VALUE_STATES={'unset','value','unknown','not_applicable'}
VALIDATION_STATES={'draft','validated','approved','stale'}
NODE_KINDS={'information','validation_gate','authority_decision','artifact','source','interaction'}

def load(p:Path):
    if not p.is_file(): raise FileNotFoundError(str(p))
    return yaml.safe_load(p.read_text(encoding='utf-8')) or {}

def uniq(records,key,errors,label):
    out={}
    for r in records or []:
        if not isinstance(r,dict) or not r.get(key): errors.append(f'{label}: missing {key}'); continue
        v=str(r[key])
        if v in out: errors.append(f'{label}: duplicate {v}')
        out[v]=r
    return out

def validate(package:Path)->dict:
    package=package.resolve(); a=package/'authoring'; errors=[]; warnings=[]
    try:
        oc=load(a/'information_object_catalog.yaml'); gc=load(a/'information_group_catalog.yaml'); ac=load(a/'artifact_catalog.yaml'); fg=load(a/'information_flow_graph.yaml'); ip=load(a/'interaction_projection.yaml')
    except Exception as e:
        return {'schema_version':'1.0','validator':'VIBE_AUTHORING_INFORMATION_MODEL','status':'FAIL','errors':[f'load: {e}'],'warnings':[]}
    objs=uniq(oc.get('objects'), 'id', errors, 'information object')
    groups=uniq(gc.get('groups'), 'id', errors, 'group')
    arts=uniq(ac.get('artifacts'), 'id', errors, 'artifact')
    nodes=uniq(fg.get('nodes'), 'id', errors, 'flow node')
    # Information passports.
    for oid,o in objs.items():
        gid=o.get('group_id')
        if not gid or gid not in groups: errors.append(f'{oid}: unknown/missing group_id {gid}')
        vc=o.get('value_contract') or {}; states=set(vc.get('value_states') or [])
        if not VALUE_STATES.issubset(states): errors.append(f'{oid}: value_states must include {sorted(VALUE_STATES)}')
        if vc.get('required') not in {True,False}: errors.append(f'{oid}: value_contract.required must be boolean')
        if vc.get('cardinality') not in {'one','many'}: errors.append(f'{oid}: cardinality must be one|many')
        lc=o.get('lifecycle') or {}; vst=set(lc.get('validation_states') or [])
        if not VALIDATION_STATES.issubset(vst): errors.append(f'{oid}: validation_states must include {sorted(VALIDATION_STATES)}')
        if lc.get('invalidate_on_change') is not True: errors.append(f'{oid}: lifecycle.invalidate_on_change must be true')
        if not o.get('origins'): errors.append(f'{oid}: origins required')
    # Groups.
    memberships=defaultdict(list)
    for oid,o in objs.items(): memberships[o.get('group_id')].append(oid)
    for gid,g in groups.items():
        members=list(g.get('members') or [])
        if not members: errors.append(f'{gid}: group has no members')
        unknown=[x for x in members if x not in objs]
        if unknown: errors.append(f'{gid}: unknown members {unknown}')
        actual=sorted(memberships.get(gid,[])); declared=sorted(members)
        if actual!=declared: errors.append(f'{gid}: membership mismatch catalog={declared} object_passports={actual}')
        disp=g.get('display') or {}
        if not disp.get('title') or not disp.get('description') or not disp.get('language'): errors.append(f'{gid}: localized display language/title/description required')
    # Every catalog entity is first-class in topology.
    for oid in objs:
        if oid not in nodes: errors.append(f'{oid}: information object missing from information_flow_graph')
        elif nodes[oid].get('kind')!='information': errors.append(f'{oid}: flow node kind must be information')
    for aid in arts:
        if aid not in nodes: errors.append(f'{aid}: artifact missing from information_flow_graph')
        elif nodes[aid].get('kind')!='artifact': errors.append(f'{aid}: flow node kind must be artifact')
    for nid,n in nodes.items():
        if n.get('kind') not in NODE_KINDS: errors.append(f'{nid}: unsupported flow node kind {n.get("kind")}')
    # Edges and reachability.
    adj=defaultdict(list); rev=defaultdict(list)
    for i,e in enumerate(fg.get('edges') or []):
        if not isinstance(e,dict): errors.append(f'edge[{i}]: not object'); continue
        s,t,typ=e.get('from'),e.get('to'),e.get('type')
        if s not in nodes: errors.append(f'edge[{i}]: unknown from {s}')
        if t not in nodes: errors.append(f'edge[{i}]: unknown to {t}')
        if typ not in EDGE_TYPES: errors.append(f'edge[{i}]: unsupported type {typ}')
        if s in nodes and t in nodes: adj[s].append(t); rev[t].append(s)
    entries=list(fg.get('entry_nodes') or []); terms=list(fg.get('terminal_nodes') or [])
    if not entries: errors.append('information_flow_graph.entry_nodes required')
    if not terms: errors.append('information_flow_graph.terminal_nodes required')
    for x in entries+terms:
        if x not in nodes: errors.append(f'entry/terminal references unknown node {x}')
    seen=set(x for x in entries if x in nodes); q=deque(seen)
    while q:
        x=q.popleft()
        for y in adj.get(x,[]):
            if y not in seen: seen.add(y); q.append(y)
    for nid in nodes:
        if entries and nid not in seen: errors.append(f'{nid}: unreachable from information-flow entry')
    # Every required artifact has inputs and inbound flow.
    for aid,aobj in arts.items():
        if (aobj.get('materialization') or {}).get('required') is True and not aobj.get('inputs'): errors.append(f'{aid}: required artifact has no inputs')
        for x in aobj.get('inputs') or []:
            if x not in objs and x not in arts: errors.append(f'{aid}: unknown input {x}')
        if aid in nodes and not rev.get(aid): errors.append(f'{aid}: artifact has no inbound information-flow edge')
    # Validation gates must declare coverage and cover known information objects.
    for nid,n in nodes.items():
        if n.get('kind')=='validation_gate':
            covers=n.get('covers') or []
            if not covers: errors.append(f'{nid}: validation gate must declare covers')
            for x in covers:
                if x not in objs and x not in arts: errors.append(f'{nid}: covers unknown entity {x}')
    # Progressive interaction is a persisted projection of information needs, not a parallel source of truth.
    pol=ip.get('policy') or {}
    if pol.get('progressive_intake') is not True: errors.append('interaction_projection: policy.progressive_intake must be true')
    if pol.get('proposal_first_when_derivable') is not True: errors.append('interaction_projection: proposal_first_when_derivable must be true')
    allowed_strategies={'free_text_seed','proposal_confirm','authority_decision','clarification','presentation'}
    seen_interactions=set()
    for i,rec in enumerate(ip.get('interactions') or []):
        if not isinstance(rec,dict) or not rec.get('id'): errors.append(f'interaction[{i}]: id required'); continue
        iid=str(rec['id'])
        if iid in seen_interactions: errors.append(f'interaction_projection: duplicate interaction {iid}')
        seen_interactions.add(iid)
        st=rec.get('strategy')
        if st not in allowed_strategies: errors.append(f'{iid}: unsupported interaction strategy {st}')
        for k in ['consumes','produces']:
            for ref in rec.get(k) or []:
                if ref not in objs: errors.append(f'{iid}: {k} unknown information object {ref}')
        for gid in rec.get('group_ids') or []:
            if gid not in groups: errors.append(f'{iid}: unknown group {gid}')
        if st=='authority_decision' and not rec.get('authority_owner'): errors.append(f'{iid}: authority_decision requires authority_owner')
    # Required information should contribute to some downstream consumer/path.
    for oid,o in objs.items():
        if (o.get('value_contract') or {}).get('required') is True and not adj.get(oid): warnings.append(f'{oid}: required information has no outgoing dependency')
    return {'schema_version':'1.0','validator':'VIBE_AUTHORING_INFORMATION_MODEL','status':'PASS' if not errors else 'FAIL','counts':{'information_objects':len(objs),'groups':len(groups),'artifacts':len(arts),'flow_nodes':len(nodes),'edges':len(fg.get('edges') or []),'interactions':len(ip.get('interactions') or [])},'errors':errors,'warnings':warnings}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); r=validate(Path(a.package)); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
