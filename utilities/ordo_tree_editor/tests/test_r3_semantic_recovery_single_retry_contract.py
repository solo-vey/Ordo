
from pathlib import Path
src=Path("editor_service.py").read_text(encoding="utf-8")
a=src.index("def _safe_semantic_model_recovery")
b=src.index("def _call_openai_live",a)
body=src[a:b]
assert "previous_candidate" in body
assert "validation_errors" in body
assert "one schema-repair retry" in body
assert body.count("_provider_api_call(")>=2
print("PASS semantic recovery has one bounded schema-repair retry")
