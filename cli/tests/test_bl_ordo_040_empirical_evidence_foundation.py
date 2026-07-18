import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/"empirical_evidence"
def test_foundation_structure_and_validator_pass():
 r=subprocess.run([sys.executable,str(ROOT/"tools/validate_empirical_evidence.py"),str(E)],capture_output=True,text=True); assert r.returncode==0,r.stdout+r.stderr; assert json.loads(r.stdout)["status"]=="passed"
def test_required_schemas_registered():
 reg=json.loads((E/"manifests/SCHEMA_REGISTRY.json").read_text()); kinds={x["kind"] for x in reg["schemas"]}; assert {"task_class","case","run","scorecard","finding","claim","admission","evidence_envelope"}<=kinds
def test_layer_contract_is_fail_closed_and_independent():
 c=json.loads((E/"manifests/LAYER_CONTRACT.json").read_text()); layers={x["name"]:x for x in c["layers"]}; assert layers["raw_evidence"]["mutable"] is False; assert "empirical_claim_to_CSG_status_mutation" in c["forbidden_flows"]
def test_validator_rejects_raw_checksum_drift(tmp_path):
 import shutil
 x=tmp_path/"e"; shutil.copytree(E,x); raw=x/"raw_evidence/sample.json"; raw.write_text("{}")
 run={"schema_version":"ordo.empirical_evidence.run.v1","run_id":"R1","case_id":"C1","scenario_id":"S1","implementation":"x","model":{"provider":"p","identifier":"m","configuration":{}},"versions":{"language":"l","framework":"f","playbook":None,"evaluator":"e"},"raw_evidence":{"path":"raw_evidence/sample.json","sha256":"0"*64},"contamination_status":"clean","admission_status":"pending","scorecard_id":None}
 (x/"cases").mkdir(exist_ok=True); (x/"cases/run.json").write_text(json.dumps(run)); idx=json.loads((x/"manifests/EMPIRICAL_EVIDENCE_INDEX.json").read_text()); idx["runs"]=["cases/run.json"]; (x/"manifests/EMPIRICAL_EVIDENCE_INDEX.json").write_text(json.dumps(idx))
 r=subprocess.run([sys.executable,str(ROOT/"tools/validate_empirical_evidence.py"),str(x)],capture_output=True,text=True); assert r.returncode!=0; assert "checksum mismatch" in r.stdout
