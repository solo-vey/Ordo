#!/usr/bin/env python3
from pathlib import Path
import argparse, json, yaml, hashlib, sys
from derive_pattern_execution_projection import derive as derive_current_projection

def _successors(element):
    out=[]
    oa=element.get('on_answer') or {}
    nxt=oa.get('next') or element.get('next')
    if isinstance(nxt,str): out.append(nxt)
    for k in ('on_pass','on_fail'):
        v=element.get(k)
        if isinstance(v,str) and v not in ('STOP','END'): out.append(v)
    return out

def assess(root, source_rel='source/program.ordo.yaml'):
    root=Path(root).resolve()
    pp=root/'authoring/pattern_execution_projection.yaml'
    sp=root/source_rel
    if not pp.exists():
        return {'schema_version':'1.0','status':'FAIL','code':'MISSING_PATTERN_EXECUTION_PROJECTION','instances':[]}
    if not sp.exists():
        return {'schema_version':'1.0','status':'FAIL','code':'MISSING_SOURCE','source':source_rel,'instances':[]}
    proj=yaml.safe_load(pp.read_text()) or {}
    try:
        expected_projection=derive_current_projection(root)
    except Exception as e:
        return {'schema_version':'1.0','status':'FAIL','code':'PATTERN_PROJECTION_REDERIVATION_FAILED','detail':str(e),'instances':[]}
    if proj != expected_projection:
        return {'schema_version':'1.0','status':'FAIL','code':'STALE_PATTERN_EXECUTION_PROJECTION','pattern_projection_digest':proj.get('projection_digest'),'expected_pattern_projection_digest':expected_projection.get('projection_digest'),'instances':[]}
    src=yaml.safe_load(sp.read_text()) or {}
    node_rows=[x for x in src.get('nodes',[]) if x.get('id')]
    gate_rows=[x for x in src.get('gates',[]) if x.get('id')]
    nodes={x.get('id'):x for x in node_rows}
    gates={x.get('id'):x for x in gate_rows}
    all_elements={**nodes,**gates}
    from collections import Counter
    id_counts=Counter([x.get('id') for x in node_rows+gate_rows])
    reports=[]
    for f in proj.get('fragments',[]):
        missing=[]; kind_mismatch=[]; edge_fail=[]; duplicate_components=[]
        for c in f.get('components',[]):
            cid=c.get('component_id'); kind=c.get('kind')
            if id_counts.get(cid,0)>1:
                duplicate_components.append({'component_id':cid,'count':id_counts.get(cid,0)})
            if cid not in all_elements:
                missing.append(cid); continue
            actual_kind='gate' if cid in gates else 'node'
            if actual_kind!=kind: kind_mismatch.append({'component_id':cid,'expected':kind,'actual':actual_kind})
        for e in f.get('edges',[]):
            a=e.get('from'); b=e.get('to')
            if a not in all_elements or b not in all_elements:
                edge_fail.append({'from':a,'to':b,'reason':'missing_component'}); continue
            succ=_successors(all_elements[a])
            if b not in succ:
                edge_fail.append({'from':a,'to':b,'reason':'forward_edge_missing'})
                continue
            allowed=(all_elements[b].get('allowed_from') or [])
            if a not in allowed:
                edge_fail.append({'from':a,'to':b,'reason':'reverse_allowed_from_missing'})
        ok=not missing and not kind_mismatch and not edge_fail and not duplicate_components
        reports.append({
            'pattern_instance_id':f.get('pattern_instance_id'),
            'pattern_id':f.get('pattern_id'),
            'pattern_version':f.get('pattern_version'),
            'instance_digest':f.get('instance_digest'),
            'status':'PASS' if ok else 'MISSING_REALIZATION',
            'missing_components':missing,
            'kind_mismatches':kind_mismatch,
            'duplicate_components':duplicate_components,
            'edge_failures':edge_fail,
            'component_count':len(f.get('components',[])),
            'edge_count':len(f.get('edges',[])),
        })
    source_hash=hashlib.sha256(sp.read_bytes()).hexdigest()
    ok=all(x['status']=='PASS' for x in reports)
    return {
        'schema_version':'1.0',
        'status':'PASS' if ok else 'FAIL',
        'producer':'tools/validate_pattern_graph_realization.py',
        'source':source_rel,
        'source_sha256':source_hash,
        'pattern_projection_digest':proj.get('projection_digest'),
        'instances':reports,
        'realized_instances':sum(x['status']=='PASS' for x in reports),
        'required_instances':len(reports),
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--source',default='source/program.ordo.yaml'); ap.add_argument('--out')
    a=ap.parse_args(); r=assess(a.root,a.source); txt=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if a.out: Path(a.out).write_text(txt,encoding='utf-8')
    else: print(txt,end='')
    sys.exit(0 if r.get('status')=='PASS' else 1)
if __name__=='__main__': main()
