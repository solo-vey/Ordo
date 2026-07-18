from pathlib import Path
import yaml,json,sys
root=Path(__file__).parent
errors=[]
for f in root.rglob('*.yaml'):
    try: yaml.safe_load(f.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'YAML {f}: {e}')
for f in root.rglob('*.json'):
    if f.name=='POST_UNPACK_VERIFICATION_REPORT.json': continue
    try: json.loads(f.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'JSON {f}: {e}')
p=yaml.safe_load((root/'source/program.ordo.yaml').read_text(encoding='utf-8'))
ids=[n['id'] for n in p['nodes']]
if len(ids)!=len(set(ids)): errors.append('duplicate node ids')
valid=set(ids)
for n in p['nodes']:
    for x in n.get('next_transitions',[]):
        if x not in valid: errors.append(f'unresolved transition {n["id"]}->{x}')
required=set(p['contract']['required']); state=set(p['state']['schema'])
if not required.issubset(state): errors.append('contract required fields missing from state: '+str(required-state))
source_name='CONFIDENTIAL_SOURCE_INSTRUCTIONS.md'
if any(source_name in str(f) for f in root.rglob('*')): errors.append('source instruction file included')
if p['ordo'].get('execution_mode')!='manual_analyst_guided': errors.append('execution mode must be manual_analyst_guided')
if p['state']['schema'].get('cancelled_run_resumable') is not False: errors.append('cancelled runs must be non-resumable')
if p['state']['schema'].get('post_link_second_approval_required') is not False: errors.append('second linked-package approval must not be required')
if p['state']['schema'].get('url_host_validation')!='none': errors.append('URL host validation must be none')
if 'implementation_tracking_url' in p['state']['schema']: errors.append('implementation work-tracking system must not be mandatory state')
if p['policies'].get('retention')!='Temporary runtime evidence and personal sign-off working data are retained only until process completion. The final package is durable; the external documentation system URL is retained in the work-tracking record artifact and the work-tracking record URL in README.md.': errors.append('retention policy mismatch')
if 'model cannot approve' not in p['policies'].get('approvals','').lower(): errors.append('model approval prohibition missing')
if not any(g['id']=='G_DRAFT_APPROVAL' for g in p['gates']): errors.append('explicit draft approval gate missing')
links=json.loads((root/'runtime/EXTERNAL_LINK_REGISTRY.json').read_text())
if set(links.get('retained_fields_after_completion',[])) != {'external_record_url','work_tracking_url'}: errors.append('retained lifecycle URL set mismatch')
if 'implementation_tracking_url' in links: errors.append('implementation work-tracking system URL must not be stored in final registry')
if links.get('placement',{}).get('external_record_url')!='artifacts/02_WORK_TRACKING_RECORD.md': errors.append('external documentation system URL placement mismatch')
if links.get('placement',{}).get('work_tracking_url')!='README.md': errors.append('work-tracking record URL placement mismatch')
readme=(root/'README.md').read_text(encoding='utf-8')
if '{{work_tracking_url}}' not in readme: errors.append('README work-tracking system URL placeholder missing')
program=(root/'source/program.ordo.yaml').read_text(encoding='utf-8')
if 'Insert the workflow-tracking URL into README.md only' not in program: errors.append('exact work-tracking system URL placement rule missing')
if 'Insert the external-record URL into the work-tracking artifact' not in program: errors.append('exact external documentation system URL placement rule missing')
print(json.dumps({'status':'passed' if not errors else 'failed','errors':errors,'yaml_files':len(list(root.rglob('*.yaml'))),'json_files':len(list(root.rglob('*.json'))),'node_count':len(ids),'gate_count':len(p['gates'])},indent=2))
sys.exit(1 if errors else 0)
