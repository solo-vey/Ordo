
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_logshape",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

allowed={"business_need","subject_type","jurisdictions","known_data_basis","trigger_draft","source_mapping","source_discrepancies"}

raw1='{"status":"resolved","state_patch":{"business_need":"x","subject_type":"COMPANY","jurisdictions":"Ukraine","known_data_basis":"basis","trigger_draft":"draft","source_mapping":null,"source_discrepancies":null},"next_node":"N2"}'
c1=m._semantic_recovery_candidate_from_raw(raw1,1,allowed)
assert c1["next_id"]=="N2"
assert all(op["op"]=="set" for op in c1["state_patch"]["operations"])
assert {op["path"] for op in c1["state_patch"]["operations"]}==allowed
assert any(x["kind"]=="flat_state_patch_to_set_operations" for x in c1["_ordo_normalization"])

raw2='{"status":"resolved","state_patch":{"operations":[{"path":"business_need","value":"x"},{"path":"subject_type","value":"COMPANY"}]},"next_node":"N2"}'
c2=m._semantic_recovery_candidate_from_raw(raw2,1,allowed)
assert all(op["op"]=="set" for op in c2["state_patch"]["operations"])
assert sum(1 for x in c2["_ordo_normalization"] if x["kind"]=="default_missing_op_to_set")==2

# Explicitly malformed operations container must remain invalid, not disappear.
raw3='{"status":"resolved","state_patch":{"operations":{"path":"business_need","value":"x"}}}'
c3=m._semantic_recovery_candidate_from_raw(raw3,1,allowed)
assert isinstance(c3["state_patch"]["operations"],dict)
print("PASS semantic-recovery response-shape normalization")
