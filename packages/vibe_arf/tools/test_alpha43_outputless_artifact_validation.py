#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile, shutil, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'cli_embedded'/'ordo_pkg'))
from ordo.artifact_validator import validate_artifacts

checks={}
# The VIBE authoring package declares no rendered artifact requirements. Missing generated_outputs is valid.
with tempfile.TemporaryDirectory() as td:
    t=Path(td)/'outputless'
    shutil.copytree(ROOT,t)
    shutil.rmtree(t/'generated_outputs',ignore_errors=True)
    r=validate_artifacts(t)
    checks['outputless_package_without_generated_outputs_passes']=r.get('status')=='passed'
    checks['outputless_report_marks_no_active_requirements']=int((r.get('summary') or {}).get('active_artifact_requirements',-1))==0

# Safety control: once an active confirmed artifact requirement exists, the same absence must still fail closed.
with tempfile.TemporaryDirectory() as td:
    t=Path(td)/'required'
    shutil.copytree(ROOT,t)
    shutil.rmtree(t/'generated_outputs',ignore_errors=True)
    import yaml
    p=t/'source'/'program.ordo.yaml'
    d=yaml.safe_load(p.read_text(encoding='utf-8')) or {}
    d.setdefault('contracts',[]).append({'id':'C_ALPHA43_TEST','status':'confirmed','fields':{'x':{'status':'confirmed','value':'X'}}})
    d.setdefault('artifacts',[]).append({'id':'A_ALPHA43_TEST','path_pattern':'generated_outputs/alpha43-test.md'})
    d.setdefault('artifact_requirements',[]).append({'id':'AR_ALPHA43_TEST','when':{'contract':'C_ALPHA43_TEST','status':'confirmed'},'requires':[{'artifact':'A_ALPHA43_TEST','must_include_fields':['x']}]})
    p.write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True),encoding='utf-8')
    r=validate_artifacts(t)
    codes={x.get('code') for x in (r.get('issues') or [])}
    checks['required_package_without_generated_outputs_fails']=r.get('status')=='failed'
    checks['required_package_reports_missing_directory']='ORDO-COV-012' in codes

status='PASS' if all(checks.values()) else 'FAIL'
print(json.dumps({'status':status,'checks':checks},ensure_ascii=False,indent=2))
raise SystemExit(0 if status=='PASS' else 1)
