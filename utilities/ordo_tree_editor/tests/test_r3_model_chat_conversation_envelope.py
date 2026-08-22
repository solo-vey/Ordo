
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_model_chat_envelope",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
cases=[
 ({"conversation":[{"role":"assistant","content":"Привіт! Чим я можу вам допомогти сьогодні?"}]},"Привіт! Чим я можу вам допомогти сьогодні?"),
 ({"messages":[{"role":"user","content":"hi"},{"role":"assistant","content":"hello"}]},"hello"),
 ({"history":[{"role":"model","text":"answer"}]},"answer"),
 ({"final":{"message":"done"}},"done"),
]
for payload,want in cases:
    got=m._extract_structured_chat_answer(payload)
    assert got==want,(got,want)
print("PASS structured conversation envelope extraction")
