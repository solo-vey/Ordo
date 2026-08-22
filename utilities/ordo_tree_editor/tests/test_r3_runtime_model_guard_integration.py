
from pathlib import Path
src=Path("editor_service.py").read_text(encoding="utf-8")
assert "def _runtime_model_call_with_guard" in src
live=src[src.index("def _call_openai_live_impl"):src.index("def _recovery_diagnosis")]
assert "_runtime_model_call_with_guard(" in live
recovery=src[src.index("def _recovery_conversation"):src.index("VERIFICATION_RUNS")]
assert "_runtime_model_call_with_guard(" in recovery
assert "contract_unsatisfiable_by_model" in live
print("PASS main runtime and recovery conversation use guarded model pipeline")
