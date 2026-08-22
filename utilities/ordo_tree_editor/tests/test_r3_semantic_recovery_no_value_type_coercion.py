
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_nocoerce",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

allowed={"jurisdictions","source_mapping","source_discrepancies"}
schemas={
 "jurisdictions":{"type":"array"},
 "source_mapping":{"type":"object"},
 "source_discrepancies":{"type":"array"},
}
raw='{"status":"resolved","state_patch":{"jurisdictions":"Ukraine","source_mapping":null,"source_discrepancies":null},"next_node":"N2"}'
c=m._semantic_recovery_candidate_from_raw(raw,0,allowed)
ok,errs=m._semantic_recovery_validate_candidate(
 c,allowed_paths=allowed,current_revision=0,value_schemas=schemas,operation_variants={},allowed_targets=["N2"]
)
assert not ok
assert any("expected 'array'" in e for e in errs),errs
assert any("expected 'object'" in e for e in errs),errs
print("PASS normalization never coerces schema-invalid values")
