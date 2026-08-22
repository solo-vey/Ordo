
from pathlib import Path
src=Path("editor_service.py").read_text(encoding="utf-8")
for token in [
 "provider.request","provider.response","runtime_model_guard.attempt",
 "semantic_recovery.initial_raw","semantic_recovery.initial_validation",
 "semantic_recovery.repair_raw","semantic_recovery.repair_validation","semantic_recovery.halt",
]:
    assert f'"{token}"' in src,token
print("PASS runtime debug instrumentation")
