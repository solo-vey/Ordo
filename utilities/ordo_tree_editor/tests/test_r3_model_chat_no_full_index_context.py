
from pathlib import Path
src=Path("editor_service.py").read_text(encoding="utf-8")
a=src.index("def _model_chat_agent_loop")
b=src.index("def _model_chat(",a)
body=src[a:b]
assert '"workspace_head":_workspace_head(root)' in body
assert '"workspace_index":_workspace_index(root)' not in body
print("PASS agent loop does not serialize full workspace index")
