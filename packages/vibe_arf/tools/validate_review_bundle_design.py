#!/usr/bin/env python3
from pathlib import Path
import argparse
from _alpha26_validation_common import load_yaml,emit

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]; warnings=[]
 oc=load_yaml(root/'authoring/information_object_catalog.yaml') or {}; gc=load_yaml(root/'authoring/information_group_catalog.yaml') or {}; rb=load_yaml(root/'authoring/review_bundle_catalog.yaml')
 if rb is None: return emit('VIBE_REVIEW_BUNDLE_DESIGN',['review_bundle_catalog missing'])
 objs={str(x.get('id')) for x in oc.get('objects') or [] if isinstance(x,dict) and x.get('id')}; groups={str(x.get('id')) for x in gc.get('groups') or [] if isinstance(x,dict) and x.get('id')}
 seen=set()
 for i,b in enumerate(rb.get('bundles') or []):
  if not isinstance(b,dict) or not b.get('id'): errors.append(f'bundle[{i}]: id required'); continue
  bid=str(b['id']);
  if bid in seen: errors.append(f'{bid}: duplicate'); seen.add(bid)
  gids=list(b.get('group_ids') or [])
  if not gids: errors.append(f'{bid}: group_ids required')
  for g in gids:
   if g not in groups: errors.append(f'{bid}: unknown group {g}')
  classes={k:set(b.get(k) or []) for k in ['derived_fields','authority_fields','uncertain_fields','display_fields','silent_fields']}
  for k,vals in classes.items():
   for x in vals:
    if x not in objs: errors.append(f'{bid}: {k} unknown {x}')
  if classes['authority_fields'] & classes['silent_fields']: errors.append(f'{bid}: authority fields cannot be silent')
  if classes['uncertain_fields'] & classes['silent_fields']: errors.append(f'{bid}: uncertain fields cannot be silent')
  if not str(b.get('approval_mode') or ''): errors.append(f'{bid}: approval_mode required')
  if not str(b.get('review_trigger') or ''): errors.append(f'{bid}: review_trigger required')
  if len(classes['display_fields'])>20: warnings.append(f'{bid}: high cognitive load ({len(classes["display_fields"])} display fields)')
 if not (rb.get('bundles') or []): warnings.append('no review bundles: valid only when no human authority review is needed')
 return emit('VIBE_REVIEW_BUNDLE_DESIGN',errors,warnings)
if __name__=='__main__': raise SystemExit(main())
