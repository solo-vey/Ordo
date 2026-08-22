
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location("editor_service_model_chat_test",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

cases=[
    ({"choices":[{"message":{"content":"Привіт!"}}]},"Привіт!"),
    ({"choices":[{"message":{"content":[{"type":"text","text":"Hello"},{"type":"text","text":"world"}]}}]},"Hello\nworld"),
    ({"choices":[{"message":{"content":None,"text":"final answer"}}]},"final answer"),
    ({"choices":[{"text":"legacy completion"}]},"legacy completion"),
    ({"output_text":"top-level compatible"},"top-level compatible"),
    ({"choices":[{"message":{"content":{"type":"text","text":"nested text"}}}]},"nested text"),
]
for payload,want in cases:
    got=m._extract_chat_response_text(payload)
    assert got==want,(payload,got,want)

assert m._extract_chat_response_text({"choices":[{"message":{"reasoning_content":"private reasoning","content":None}}]})==""
print("PASS provider response normalization variants")
