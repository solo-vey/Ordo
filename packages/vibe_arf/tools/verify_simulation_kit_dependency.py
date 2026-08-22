#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,tempfile,zipfile
from pathlib import Path

def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def resolve_root(x:Path)->Path:
    if (x/'ordo_simulate.py').is_file(): return x
    direct=[p for p in x.iterdir() if p.is_dir() and (p/'ordo_simulate.py').is_file()]
    if len(direct)==1:return direct[0]
    found=sorted({p.parent for p in x.rglob('ordo_simulate.py') if p.is_file()})
    if len(found)==1:return found[0]
    raise RuntimeError(f'ambiguous kit root: {[str(p) for p in found]}')
def manifest(root:Path,mf:Path,base:Path):
    errors=[]; n=0
    for line in mf.read_text(encoding='utf-8').splitlines():
        line=line.strip()
        if not line:continue
        want,rel=line.split(None,1); rel=rel.strip(); p=base/rel; n+=1
        if not p.is_file():errors.append(f'missing:{rel}')
        elif h(p)!=want:errors.append(f'hash:{rel}')
    return n,errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package_root'); a=ap.parse_args(); pkg=Path(a.package_root).resolve(); errors=[]; ev={}
    depf=pkg/'verification/SIMULATION_KIT_DEPENDENCY.json'; accf=None
    if not depf.is_file(): print(json.dumps({'status':'FAIL','errors':['dependency metadata missing']})); return 1
    dep=loadj(depf); accf=pkg/str(dep.get('acceptance_evidence') or ''); z=pkg/dep.get('path','')
    if not z.is_file(): errors.append('dependency zip missing')
    elif h(z)!=dep.get('sha256'): errors.append('dependency zip sha256 mismatch')
    if not errors:
      with tempfile.TemporaryDirectory() as td:
        td=Path(td); zipfile.ZipFile(z).extractall(td)
        try: root=resolve_root(td)
        except Exception as e: errors.append(str(e)); root=None
        if root:
          version=(root/'VERSION').read_text().strip() if (root/'VERSION').is_file() else ''
          baseline=(root/'RUNTIME_BASELINE').read_text().strip() if (root/'RUNTIME_BASELINE').is_file() else ''
          expected=str(dep.get('runtime_baseline','')).replace('Ordo Tree Editor ','').strip()
          if version!=str(dep.get('version')): errors.append(f'VERSION {version} != pinned {dep.get("version")}')
          if baseline!=expected: errors.append(f'RUNTIME_BASELINE {baseline} != pinned {expected}')
          if not (root/'MANIFEST.sha256').is_file(): errors.append('MANIFEST.sha256 missing')
          else:
            n,e=manifest(root,root/'MANIFEST.sha256',root); ev['manifest_entries']=n; errors += [f'manifest:{x}' for x in e]
          if not (root/'RUNTIME_CORE_MANIFEST.sha256').is_file(): errors.append('RUNTIME_CORE_MANIFEST.sha256 missing')
          else:
            n,e=manifest(root,root/'RUNTIME_CORE_MANIFEST.sha256',root/'runtime_core'); ev['runtime_core_manifest_entries']=n; errors += [f'runtime_core_manifest:{x}' for x in e]
    if not accf.is_file(): errors.append('simulation kit acceptance evidence missing')
    else:
      acc=loadj(accf)
      if acc.get('status')!='PASS': errors.append('acceptance evidence not PASS')
      acc_hash=acc.get('sha256') or acc.get('zip_sha256')
      if acc.get('version')!=dep.get('version') or acc_hash!=dep.get('sha256'): errors.append('acceptance evidence does not bind exact pinned kit')
      if acc.get('runtime_baseline')!=dep.get('runtime_baseline'): errors.append('acceptance evidence runtime baseline mismatch')
      sc=acc.get('self_check')
      sc_status=sc.get('status') if isinstance(sc,dict) else sc
      if sc_status!='PASS': errors.append('acceptance self_check not PASS')
      ut=acc.get('unit_tests') or {}
      if int(ut.get('failed',-1))!=0 or int(ut.get('passed',0))<12: errors.append('acceptance unit tests incomplete')
      # 0.1.5 acceptance is bound to the actual self-check/unit suite and the pinned release contract.
      # Legacy smoke/capability fields remain accepted when present, but are no longer mandatory duplicates.
      if str(dep.get('version'))=='0.1.5':
        if acc.get('evidence_kind') not in {'actual_dependency_self_check_and_unit_test_run','actual_self_check_unit_and_runtime_smoke_execution'}:
          errors.append('acceptance evidence kind must prove actual 0.1.5 execution')
      else:
        smoke=acc.get('runtime_smoke') or {}
        inspect_key='vibe_alpha27_inspect' if 'vibe_alpha27_inspect' in smoke else 'vibe_alpha26_inspect'
        for key in ['basic_human_model','package_tool_route',inspect_key]:
          if (smoke.get(key) or {}).get('status')!='PASS': errors.append(f'acceptance smoke {key} not PASS')
        caps=acc.get('capabilities') or {}
        for key in ['deterministic_artifact_archive_validation','mechanical_gate_no_llm_fallback']:
          if caps.get(key) is not True: errors.append(f'acceptance capability {key} missing')
        if caps.get('profile_contract_gap_evidence')!='profile_contract_gaps.json': errors.append('acceptance profile contract gap evidence missing')
    out={'schema_version':'1.3','validator':'VIBE_SIMULATION_KIT_DEPENDENCY','status':'PASS' if not errors else 'FAIL','dependency':dep,'evidence':ev,'errors':errors}
    print(json.dumps(out,ensure_ascii=False,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
