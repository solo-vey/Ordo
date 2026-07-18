from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'empirical_evidence/external_developer_adoption/EDA_001'
def test_eda_001_case_and_package_integrity():
 d=json.loads((BASE/'case.json').read_text())
 p=BASE/d['source_handling']['publication_safe_package']
 assert p.is_file()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==d['source_handling']['publication_safe_package_sha256']
 assert d['source_handling']['original_specific_source_included'] is False
 with zipfile.ZipFile(p) as z: assert z.testzip() is None
def test_eda_001_is_indexed_and_schema_registered():
 idx=json.loads((ROOT/'empirical_evidence/manifests/EMPIRICAL_EVIDENCE_INDEX.json').read_text())
 assert 'external_developer_adoption/EDA_001/case.json' in idx['external_adoption_cases']
 reg=json.loads((ROOT/'empirical_evidence/manifests/SCHEMA_REGISTRY.json').read_text())
 assert any(x['schema_id']=='ordo.empirical_evidence.external_adoption_case.v1' for x in reg['schemas'])
def test_eda_001_publication_safe_scan():
 forbidden=['Monitoring BusinessPrepare','atlassian.net','confluence','jira']
 for p in BASE.rglob('*'):
  if p.is_file() and p.suffix.lower() in {'.md','.json','.yaml','.yml','.txt'}:
   text=p.read_text(errors='ignore').lower()
   for token in forbidden: assert token.lower() not in text
