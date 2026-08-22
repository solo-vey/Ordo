
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location("editor_service_semantic_repair",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

bad=m._semantic_recovery_candidate_from_raw(
    '{"status":"resolved","assistant_message":"","reason":"x","next_id":"N2","state_patch":{"base_revision":0,"operations":{"path":"x"}}}',
    3,
)
ok,errs=m._semantic_recovery_validate_candidate(
    bad,allowed_paths={"x"},current_revision=3,value_schemas={},operation_variants={},allowed_targets=["N2"]
)
assert not ok
assert any("operations" in e for e in errs),errs

good=m._semantic_recovery_candidate_from_raw(
    '{"status":"resolved","assistant_message":"","reason":"x","next_id":"N2","state_patch":{"base_revision":0,"operations":[]}}',
    3,
)
ok2,errs2=m._semantic_recovery_validate_candidate(
    good,allowed_paths={"x"},current_revision=3,value_schemas={},operation_variants={},allowed_targets=["N2"]
)
assert ok2,errs2
assert good["state_patch"]["base_revision"]==3
print("PASS semantic recovery malformed operations is detectable and repairable")
