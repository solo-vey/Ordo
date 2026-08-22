#!/usr/bin/env python3
from __future__ import annotations
import argparse, fnmatch, hashlib, json, zipfile
from pathlib import Path

def deterministic_info(rel, executable=False):
    zi=zipfile.ZipInfo(rel,(1980,1,1,0,0,0)); zi.compress_type=zipfile.ZIP_DEFLATED; zi.create_system=3; zi.external_attr=((0o100755 if executable else 0o100644)<<16); return zi

def zwrite_bytes(z,rel,data,executable=False): z.writestr(deterministic_info(rel,executable),data)

def match(rel, pat):
    # fnmatch handles ** sufficiently for slash-separated paths in this use.
    return fnmatch.fnmatch(rel, pat) or (pat.endswith('/**') and (rel==pat[:-3] or rel.startswith(pat[:-2])))

def load_generated_delivery_manifest(root: Path, contract: dict):
    rel=contract.get('safe_delivery_manifest','generated_outputs/PRODUCTION_DELIVERABLES.json')
    p=root/rel
    if not p.exists(): return rel, {}, None
    try:
        data=json.loads(p.read_text())
    except Exception as e:
        return rel, {}, ('GENERATED_OUTPUT_MANIFEST_INVALID', str(e))
    rows={}
    for row in data.get('deliverables',[]):
        path=row.get('path')
        if path: rows[path]=row
    return rel, rows, None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('package_root'); ap.add_argument('output_zip')
    ap.add_argument('--profile',choices=['production','debug_handoff'],default='production')
    a=ap.parse_args(); root=Path(a.package_root).resolve(); out=Path(a.output_zip).resolve()
    contract=json.loads((root/'PRODUCTION_PACKAGE_CONTRACT.json').read_text())
    rows=contract['artifact_classes']
    closure_cfg=contract.get('dependency_closure',{})
    closure_rel=closure_cfg.get('manifest','PRODUCTION_DEPENDENCY_CLOSURE.json')
    closure_data=json.loads((root/closure_rel).read_text()) if (root/closure_rel).is_file() else {'files':[]}
    closure_rows={x.get('path'):x for x in closure_data.get('files',[]) if isinstance(x,dict) and x.get('path')}
    controlled_prefixes=tuple(closure_cfg.get('controlled_prefixes',[]))
    delivery_manifest_rel, declared_outputs, manifest_error = load_generated_delivery_manifest(root, contract)
    if manifest_error:
        print(json.dumps({'status':'FAIL','code':manifest_error[0],'detail':manifest_error[1]},indent=2)); return 4
    generated_policy=contract.get('generated_output_policy',{})
    allowed_generated_roles=set(generated_policy.get('allowed_roles',['declared_delivery']))
    forbidden_generated_roles=set(generated_policy.get('forbidden_roles',['simulation','evaluator','reference','calibration','best_candidate','expected_output']))
    required=[x for x in contract['required_root_artifacts'] if not (root/x).is_file()]
    if required:
        print(json.dumps({'status':'FAIL','code':'REQUIRED_ARTIFACT_MISSING','missing':required},indent=2)); return 2
    selected=[]; excluded=[]; unknown=[]
    for p in sorted(x for x in root.rglob('*') if x.is_file()):
        if p.resolve()==out: continue
        rel=p.relative_to(root).as_posix()
        pre_matches=[r for r in rows if any(match(rel,pat) for pat in r['patterns'])]
        forbidden_pre=[r for r in pre_matches if r.get('default_inclusion')=='forbidden']
        if forbidden_pre:
            excluded.append((p,forbidden_pre[0]['class'])); continue
        if controlled_prefixes and rel.startswith(controlled_prefixes):
            crow=closure_rows.get(rel)
            if not crow:
                excluded.append((p,'not_in_dependency_closure')); continue
            actual=hashlib.sha256(p.read_bytes()).hexdigest()
            if closure_cfg.get('hash_required',True) and actual != crow.get('sha256'):
                print(json.dumps({'status':'FAIL','code':'DEPENDENCY_CLOSURE_HASH_MISMATCH','path':rel,'expected':crow.get('sha256'),'actual':actual},indent=2)); return 8
            selected.append((p,'dependency_closure')); continue
        if rel in set(contract.get('production_exact_includes',[])):
            selected.append((p,'production_exact_include')); continue
        if rel.startswith('generated_outputs/') and p.name in {'.gitkeep','.keep'}:
            excluded.append((p,'placeholder')); continue
        if rel.startswith('generated_outputs/'):
            if rel == delivery_manifest_rel:
                selected.append((p,'generated_outputs_manifest')); continue
            row=declared_outputs.get(rel)
            if not row or row.get('production_deliverable') is not True:
                print(json.dumps({'status':'FAIL','code':'UNDECLARED_GENERATED_OUTPUT','path':rel},indent=2)); return 5
            role=str(row.get('role',''))
            if role in forbidden_generated_roles or role not in allowed_generated_roles:
                print(json.dumps({'status':'FAIL','code':'UNSAFE_GENERATED_OUTPUT_ROLE','path':rel,'role':role},indent=2)); return 6
            expected=row.get('sha256')
            actual=hashlib.sha256(p.read_bytes()).hexdigest()
            if not expected or expected != actual:
                print(json.dumps({'status':'FAIL','code':'GENERATED_OUTPUT_HASH_MISMATCH','path':rel,'expected':expected,'actual':actual},indent=2)); return 7
            selected.append((p,'generated_outputs')); continue
        matches=[r for r in rows if any(match(rel,pat) for pat in r['patterns'])]
        # forbidden/debug classes take precedence over broad production classes.
        chosen=None
        # Analyst context is an explicit production authoring surface. Its own access_scope
        # controls evaluator-only visibility; broad filename heuristics such as *golden*
        # must not demote it to debug-only. Forbidden cache rules still win.
        if rel.startswith('analyst_context/'):
            forbidden=[r for r in matches if r['default_inclusion']=='forbidden']
            ctx=[r for r in matches if r.get('class')=='analyst_context']
            chosen=(forbidden or ctx or matches or [None])[0]
        else:
            for level in ('forbidden','debug_only','required','optional'):
                cand=[r for r in matches if r['default_inclusion']==level]
                if cand: chosen=cand[0]; break
        if not chosen:
            # explicitly ship package contract/policy even though not part of semantic surfaces.
            if rel in {'PRODUCTION_PACKAGE_CONTRACT.json','source/generated-playbook-production-package-policy.json'}:
                selected.append((p,'package_contract')); continue
            unknown.append(rel); continue
        inc = chosen['default_inclusion'] in {'required','optional'} or (a.profile=='debug_handoff' and chosen['default_inclusion']=='debug_only')
        if chosen['default_inclusion']=='forbidden': inc=False
        (selected if inc else excluded).append((p,chosen['class']))
    if unknown:
        print(json.dumps({'status':'FAIL','code':'UNCLASSIFIED_ARTIFACTS','count':len(unknown),'sample':unknown[:30]},indent=2)); return 3
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,allowZip64=True) as z:
        for p,cls in sorted(selected,key=lambda x:x[0].relative_to(root).as_posix()):
            rel=p.relative_to(root).as_posix(); zwrite_bytes(z,rel,p.read_bytes(),rel=='cli_embedded/ordo')
        manifest={
          'schema_version':'1.0','profile':a.profile,'file_count':len(selected),
          'files':[{'path':p.relative_to(root).as_posix(),'class':cls,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p,cls in selected],
          'excluded_count':len(excluded)
        }
        zwrite_bytes(z,'PRODUCTION_PACKAGE_MANIFEST.json',(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'status':'PASS','profile':a.profile,'output':str(out),'files':len(selected)+1,'excluded':len(excluded),'bytes':out.stat().st_size},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
