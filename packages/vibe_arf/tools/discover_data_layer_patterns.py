#!/usr/bin/env python3
from pathlib import Path
import argparse,json

def load(root):
    reg=json.loads((root/'patterns/PATTERN_REGISTRY.json').read_text())
    snap=json.loads((root/'authoring/pattern_selection_input_snapshot.json').read_text())
    return reg,snap

def discover(root):
    reg,snap=load(root); out=[]
    arts=snap.get('artifacts',[]); caps=snap.get('capability_requirements',[])
    for p in reg.get('patterns',[]):
        pk=set(p.get('artifact_kinds',[])); pt=set(p.get('capability_tags',[]))
        am=[a['id'] for a in arts if a.get('required',True) and a.get('kind') in pk]
        cm=[c['id'] for c in caps if c.get('required',True) and c.get('capability_tag') in pt]
        policy=p.get('selection_match_policy','artifact_or_capability')
        eligible = bool(cm) if policy=='capability_required' else bool(am or cm)
        if eligible:
            out.append({'pattern_id':p['id'],'version':str(p['version']),'fit':'exact','artifact_matches':am,'capability_matches':cm,'action':'auto_instantiate','selection_match_policy':policy,'variant_family':p.get('variant_family'),'variant_tier':p.get('variant_tier'),'selection_input_snapshot_digest':snap.get('snapshot_digest')})
    # SIMPLE and advanced variants intentionally coexist. If more than one member of the
    # same variant family matches, discovery must not silently pick one.
    families={}
    for row in out:
        if row.get('variant_family'):
            families.setdefault(row['variant_family'],[]).append(row)
    for fam, rows in families.items():
        if len(rows)>1:
            for row in rows:
                row['fit']='variant_choice_required'
                row['action']='choose_variant_explicitly'
                row['variant_candidates']=[r['pattern_id'] for r in rows]
    return {'status':'PASS','selection_input_snapshot_digest':snap.get('snapshot_digest'),'suggestions':out}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); a=ap.parse_args(); print(json.dumps(discover(Path(a.root).resolve()),indent=2))
if __name__=='__main__': main()
