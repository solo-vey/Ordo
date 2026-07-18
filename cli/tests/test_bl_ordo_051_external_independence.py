import copy, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MOD_PATH=ROOT/'empirical_evidence/tools/validate_external_independence.py'
spec=importlib.util.spec_from_file_location('independence',MOD_PATH); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CASE=ROOT/'empirical_evidence/external_developer_adoption/EDA_001/case.json'
SCHEMA=ROOT/'empirical_evidence/schemas/external_adoption_case.schema.json'
def test_eda001_conservative_migration_passes():
 r=m.validate_case(CASE,SCHEMA); assert r['status']=='passed'; assert r['declared_level']=='self_declared_independence_unverified'
def test_overclaim_is_blocked(tmp_path):
 d=json.loads(CASE.read_text()); d['bounded_claim']='This is independently verified independent work.'; p=tmp_path/'case.json'; p.write_text(json.dumps(d));
 # package relative dependency
 (tmp_path/'package').mkdir(); src=CASE.parent/'package'/d['source_handling']['publication_safe_package'].split('/')[-1]; (tmp_path/'package'/src.name).write_bytes(src.read_bytes())
 r=m.validate_case(p,SCHEMA); assert r['status']=='blocked'; assert any('overstates' in x for x in r['issues'])
def test_stronger_level_without_evidence_is_blocked(tmp_path):
 d=json.loads(CASE.read_text()); d['independence_verification']['declared_level']='timestamp_verified'; d['independence_verification']['claim_status']='evidence_supported'; p=tmp_path/'case.json'; p.write_text(json.dumps(d));
 (tmp_path/'package').mkdir(); src=CASE.parent/'package'/d['source_handling']['publication_safe_package'].split('/')[-1]; (tmp_path/'package'/src.name).write_bytes(src.read_bytes())
 r=m.validate_case(p,SCHEMA); assert r['status']=='blocked'; assert any('trusted_timestamp_proof' in x for x in r['issues'])
def test_submission_template_schema_valid():
 import jsonschema
 d=json.loads((ROOT/'empirical_evidence/external_developer_adoption/SUBMISSION_TEMPLATE.json').read_text()); s=json.loads((ROOT/'empirical_evidence/schemas/external_developer_submission.schema.json').read_text()); jsonschema.validate(d,s)
