
from pathlib import Path
src=Path("editor_service.py").read_text(encoding="utf-8")
a=src.index("def _normalize_semantic_recovery_envelope")
b=src.index("def _semantic_recovery_validate_candidate")
segment=src[a:b]
for forbidden in [
 "business_need","jurisdictions","source_mapping","source_discrepancies",
 "N_ASSIMILATE_SOURCES","N_CLASSIFY_EVENT_MECHANICS","MONITORING_BUSINESS"
]:
    assert forbidden not in segment,forbidden
print("PASS generic recovery normalization is domain-agnostic")
