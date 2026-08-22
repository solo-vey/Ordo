
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_agent_protocol",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
a=m._model_chat_parse_agent_turn('{"type":"tool","tool":{"name":"workspace.read","arguments":{"path":"x.md"}}}')
assert a["type"]=="tool" and a["name"]=="workspace.read"
b=m._model_chat_parse_agent_turn('{"type":"final","message":"hello"}')
assert b["type"]=="final" and b["message"]=="hello"
print("PASS agent tool/final protocol parser")
