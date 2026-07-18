#!/usr/bin/env python3
from pathlib import Path
import argparse, yaml, json, hashlib
TRANSITION_KEYS={'next','on_pass','on_fail','on_complete','on_aligned','on_misaligned','on_regenerate','on_no_go','fail_route','pass_route'}
def target_from(v):
    if isinstance(v,str): return [v]
    if isinstance(v,dict):
        out=[]
        if isinstance(v.get('next'),str): out.append(v['next'])
        for k,x in v.items():
            if k.startswith('on_') or k in ('pass_route','fail_route'):
                out += target_from(x)
        return out
    if isinstance(v,list):
        out=[]
        for x in v: out+=target_from(x)
        return out
    return []
def edges_for(obj):
    out=[]
    for k,v in obj.items():
        if k=='next' or k.startswith('on_') or k in ('pass_route','fail_route'):
            out += target_from(v)
    # gates field is a routing reference only when no explicit next to that gate exists
    if isinstance(obj.get('gates'),list):
        for g in obj['gates']:
            if isinstance(g,str) and g not in out: out.append(g)
    return out
def validate(path):
    raw=Path(path).read_bytes(); d=yaml.safe_load(raw)
    nodes={x['id']:x for x in d.get('nodes',[])}; gates={x['id']:x for x in d.get('gates',[])}; terms={x['id']:x for x in d.get('terminals',[])}
    all_ids=set(nodes)|set(gates)|set(terms)
    contract=d.get('execution_graph_contract',{}); entry=contract.get('entrypoint') or d.get('process_rail',{}).get('entrypoint')
    auth_nodes=set(contract.get('route_authorized_node_ids',nodes)); auth_gates=set(contract.get('route_authorized_gate_ids',gates))
    adjacency={}
    dangling=[]
    for sid,obj in list(nodes.items())+list(gates.items()):
        ts=edges_for(obj); adjacency[sid]=ts
        for t in ts:
            if t not in all_ids: dangling.append({'source':sid,'target':t})
    seen=set(); stack=[entry] if entry in all_ids else []
    while stack:
        x=stack.pop()
        if x in seen: continue
        seen.add(x)
        stack.extend([t for t in adjacency.get(x,[]) if t in all_ids])
    unreachable_nodes=sorted(auth_nodes-seen); unreachable_gates=sorted(auth_gates-seen)
    accidental=[]
    for nid in sorted(auth_nodes):
        if nid in nodes and not adjacency.get(nid): accidental.append(nid)
    # gates must route both pass/fail or explicit declared single condition; in this package all route gates need outputs
    for gid in sorted(auth_gates):
        if gid in gates and not adjacency.get(gid): accidental.append(gid)
    incoming={x:0 for x in all_ids}
    for ts in adjacency.values():
        for t in ts:
            if t in incoming: incoming[t]+=1
    orphans=sorted([x for x in auth_nodes|auth_gates if x!=entry and incoming.get(x,0)==0])
    completion=contract.get('completion_terminal') or d.get('process_rail',{}).get('completion_terminal')
    errors=[]
    if entry not in nodes: errors.append('MISSING_ENTRYPOINT')
    if completion not in terms: errors.append('MISSING_COMPLETION_TERMINAL')
    if dangling: errors.append('DANGLING_TARGETS')
    if unreachable_nodes: errors.append('UNREACHABLE_NODES')
    if unreachable_gates: errors.append('UNREACHABLE_GATES')
    if accidental: errors.append('ACCIDENTAL_DEAD_ENDS')
    if orphans: errors.append('ORPHANS')
    if completion in terms and completion not in seen: errors.append('COMPLETION_UNREACHABLE')
    return {
      'schema_version':'ordo.execution_graph_connectivity.report.v1','status':'PASS' if not errors else 'FAIL',
      'source':str(path),'source_sha256':hashlib.sha256(raw).hexdigest(),'entrypoint':entry,'completion_terminal':completion,
      'counts':{'nodes':len(nodes),'gates':len(gates),'terminals':len(terms),'edges':sum(len(v) for v in adjacency.values()),'reachable_objects':len(seen)},
      'unreachable_nodes':unreachable_nodes,'unreachable_gates':unreachable_gates,'dangling_targets':dangling,
      'accidental_dead_ends':sorted(set(accidental)),'orphan_objects':orphans,'errors':errors,'adjacency':adjacency
    }
def main():
 p=argparse.ArgumentParser(); p.add_argument('program'); p.add_argument('--out'); a=p.parse_args(); r=validate(a.program); s=json.dumps(r,ensure_ascii=False,indent=2)+'\n';
 if a.out: Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(s,encoding='utf-8')
 print(s,end=''); raise SystemExit(0 if r['status']=='PASS' else 2)
if __name__=='__main__': main()
