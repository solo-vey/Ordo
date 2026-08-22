
from pathlib import Path
src=Path("editor_service.py").read_text(encoding="utf-8")
a=src.index("def _model_chat_parse_agent_turn")
b=src.index("def _model_chat_attachment_metadata",a)
segment=src[a:b]
assert 'parsed.get("tool_call")' in segment
assert '"kind":"tool_call"' in segment
assert 'activity_callback(copy.deepcopy(activity))' in segment
assert 'return str(turn.get("message") or ""),trace,usage_total,activities' in segment
print("PASS Model Chat tool envelopes stay inside agent loop and emit activity only")
