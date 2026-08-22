#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import yaml

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package).resolve(); ad=root/'authoring'
    oc=yaml.safe_load((ad/'information_object_catalog.yaml').read_text(encoding='utf-8')) or {}
    gc=yaml.safe_load((ad/'information_group_catalog.yaml').read_text(encoding='utf-8')) or {}
    ip=yaml.safe_load((ad/'interaction_projection.yaml').read_text(encoding='utf-8')) or {}
    objs={str(x.get('id')):x for x in oc.get('objects') or [] if isinstance(x,dict) and x.get('id')}
    groups={str(x.get('id')):x for x in gc.get('groups') or [] if isinstance(x,dict) and x.get('id')}
    human_groups=[]
    for rec in ip.get('interactions') or []:
        if not isinstance(rec,dict): continue
        if rec.get('strategy') in {'proposal_confirm','authority_decision','clarification'}:
            human_groups.extend(str(x) for x in rec.get('group_ids') or [])
    bundles=[]
    for gid in dict.fromkeys(human_groups):
        g=groups.get(gid)
        if not g: continue
        derived=[]; authority=[]; uncertain=[]; display=[]; silent=[]
        for oid in g.get('members') or []:
            o=objs.get(str(oid),{}); origins=set(o.get('origins') or []); required=(o.get('value_contract') or {}).get('required') is True
            if 'human_input' in origins: authority.append(oid); display.append(oid)
            elif origins.intersection({'model_derivation','deterministic_derivation','source_material'}):
                derived.append(oid)
                if required: display.append(oid)
                else: silent.append(oid)
            else:
                uncertain.append(oid); display.append(oid)
        bundles.append({'id':f'RB_{gid.removeprefix("G_")}', 'group_ids':[gid], 'derived_fields':derived,
                        'authority_fields':authority,'uncertain_fields':uncertain,'display_fields':display,
                        'silent_fields':silent,'approval_mode':'field_projection','review_trigger':'authority_or_uncertainty_present'})
    out={'schema_version':'1.0','bundles':bundles,'generated_from':'AIM information groups + interaction projection',
         'rules':{'derived_from_information_groups':True,'human_review_only_for_authority_or_uncertainty':True,'max_bundle_fields_soft':12}}
    (ad/'review_bundle_catalog.yaml').write_text(yaml.safe_dump(out,sort_keys=False,allow_unicode=True),encoding='utf-8')
    print(json.dumps({'status':'PASS','bundles':len(bundles),'output':str(ad/'review_bundle_catalog.yaml')},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
