
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_modelchat_tool",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

cases=[
 '{"type":"tool","tool":{"name":"workspace.read","arguments":{"path":"a.md"}}}',
 '{"tool_call":{"name":"workspace.list","arguments":{"path":"x"}}}',
 '{"call_tool":{"name":"workspace.search","arguments":{"query":"START"}}}',
]
for raw in cases:
    turn=m._model_chat_parse_agent_turn(raw)
    assert turn["type"]=="tool",(raw,turn)
    assert turn["name"].startswith("workspace."),(raw,turn)
print("PASS Model Chat recognizes canonical and direct tool-call envelopes")
