#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, zipfile
REQ_DESIGN={'design/MODEL_BUNDLE.yaml','design/variable_catalog.yaml','design/variable_group_catalog.yaml','design/information_dependency_graph.yaml','design/artifact_catalog.yaml','design/playbook_projection.yaml','design/DATA_FLOW_PACKAGE.zip'}
REQ_NESTED={'MODEL_BUNDLE.yaml','variable_catalog.yaml','variable_group_catalog.yaml','information_dependency_graph.yaml','artifact_catalog.yaml','playbook_projection.yaml'}
def issue(code,**kw): return {'code':code,**kw}
def j(z,n):
    try:return json.loads(z.read(n))
    except Exception:return {}
def continuity(z,profile):
    f=[]; names=set(z.namelist()); cm=j(z,'PACKAGE_CONTINUITY_MANIFEST.json'); dm=j(z,'DISTRIBUTION_MANIFEST.json')
    if not cm: return [issue('CONTINUITY_MANIFEST_MISSING')]
    for k in ['profile','version','canonical_source_identity','source_identity_files','dependency_closure_sha256','member_set_sha256','startup_files','rebuild_recipe','packaging_policy_sha256','validator_applicability_policy_sha256']:
        if k not in cm:f.append(issue('CONTINUITY_FIELD_MISSING',field=k))
    if cm.get('profile')!=profile:f.append(issue('CONTINUITY_PROFILE',expected=profile,actual=cm.get('profile')))
    if cm.get('canonical_source_identity')!=dm.get('source_identity_sha256'):f.append(issue('CONTINUITY_SOURCE_IDENTITY'))
    if cm.get('version')!=dm.get('version'):f.append(issue('CONTINUITY_VERSION'))
    for x in cm.get('startup_files',[]):
        p=x.get('path'); exp=x.get('sha256')
        if p not in names:f.append(issue('CONTINUITY_STARTUP_MISSING',path=p))
        elif hashlib.sha256(z.read(p)).hexdigest()!=exp:f.append(issue('CONTINUITY_STARTUP_HASH',path=p))
    return f
def validate_edit(path):
    f=[]
    with zipfile.ZipFile(path) as z:
        names=set(z.namelist()); bad=z.testzip(); m=j(z,'DISTRIBUTION_MANIFEST.json')
        if bad:f.append(issue('ZIP_INTEGRITY',member=bad))
        miss=sorted(REQ_DESIGN-names)
        if miss:f.append(issue('EDIT_EDITOR_DATAFLOW_SURFACE_MISSING',missing=miss))
        if 'design/DATA_FLOW_PACKAGE.zip' in names:
            import io
            with zipfile.ZipFile(io.BytesIO(z.read('design/DATA_FLOW_PACKAGE.zip'))) as nz:
                nm=sorted(REQ_NESTED-set(nz.namelist()))
                if nm:f.append(issue('EDIT_DATA_FLOW_PACKAGE_INCOMPLETE',missing=nm))
        if m and m.get('distribution')!='EDIT':f.append(issue('DISTRIBUTION_ID',expected='EDIT',actual=m.get('distribution')))
        f+=continuity(z,'EDIT')
    return f
def validate_exec(path,profile):
    f=[]
    with zipfile.ZipFile(path) as z:
        names=set(z.namelist()); bad=z.testzip(); m=j(z,'DISTRIBUTION_MANIFEST.json')
        if bad:f.append(issue('ZIP_INTEGRITY',member=bad))
        c=j(z,'DISTRIBUTION_PACKAGE_CONTRACT.json'); pc=c.get('profiles',{}).get(profile,{})
        badp=sorted(n for n in names if any(n.startswith(p) for p in pc.get('forbidden_prefixes',[])) or any(t.lower() in n.lower() for t in pc.get('forbidden_name_tokens',[])))
        if badp:f.append(issue(profile+'_FORBIDDEN_BAGGAGE',paths=badp[:30]))
        if m and m.get('distribution')!=profile:f.append(issue('DISTRIBUTION_ID',expected=profile,actual=m.get('distribution')))
        starts=set(pc.get('start_files',[])); miss=sorted(starts-names)
        if miss:f.append(issue(profile+'_START_SURFACE_MISSING',missing=miss))
        closure_name=profile+'_PACKAGE_DEPENDENCY_CLOSURE.json'
        if closure_name not in names:f.append(issue(profile+'_CLOSURE_MISSING'))
        f+=continuity(z,profile)
    return f
def sid(path):
    with zipfile.ZipFile(path) as z:return j(z,'DISTRIBUTION_MANIFEST.json').get('source_identity_sha256')
def ver(path):
    with zipfile.ZipFile(path) as z:return j(z,'DISTRIBUTION_MANIFEST.json').get('version')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package',nargs='?'); ap.add_argument('--mode',required=True,choices=['edit','cli_run','model_run','release','dev','debug','run','pair']); ap.add_argument('--edit'); ap.add_argument('--cli-run'); ap.add_argument('--model-run'); ap.add_argument('--dev'); ap.add_argument('--run'); a=ap.parse_args(); mode={'dev':'edit','debug':'edit','run':'cli_run','pair':'release'}.get(a.mode,a.mode); f=[]
    if mode=='edit': f+=validate_edit(a.package) if a.package else [issue('PACKAGE_REQUIRED')]
    elif mode=='cli_run': f+=validate_exec(a.package,'CLI_RUN') if a.package else [issue('PACKAGE_REQUIRED')]
    elif mode=='model_run': f+=validate_exec(a.package,'MODEL_RUN') if a.package else [issue('PACKAGE_REQUIRED')]
    else:
        ep=a.edit or a.dev; cp=a.cli_run or a.run; mp=a.model_run
        if not ep or not cp or not mp:f.append(issue('RELEASE_PACKAGES_REQUIRED'))
        else:
            f+=validate_edit(ep)+validate_exec(cp,'CLI_RUN')+validate_exec(mp,'MODEL_RUN'); ids=[sid(ep),sid(cp),sid(mp)]; versions=[ver(ep),ver(cp),ver(mp)]
            if not ids[0] or len(set(ids))!=1:f.append(issue('RELEASE_SOURCE_PARITY',source_ids=ids))
            if not versions[0] or len(set(versions))!=1:f.append(issue('RELEASE_VERSION_PARITY',versions=versions))
    print(json.dumps({'status':'PASS' if not f else 'FAIL','mode':mode,'findings':f},ensure_ascii=False,indent=2)); raise SystemExit(0 if not f else 1)
if __name__=='__main__': main()
