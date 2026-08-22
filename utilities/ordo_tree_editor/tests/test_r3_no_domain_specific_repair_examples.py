
from pathlib import Path
src=Path("editor_service.py").read_text(encoding="utf-8")
a=src.index("def _operation_contract_summary")
b=src.index("def _call_openai_live",a)
segment=src[a:b]
for forbidden in ["business_need","jurisdictions","source_mapping","N_ASSIMILATE_SOURCES","N_CLASSIFY_EVENT_MECHANICS"]:
    assert forbidden not in segment,forbidden
print("PASS semantic recovery/repair core contains no playbook-specific examples")
