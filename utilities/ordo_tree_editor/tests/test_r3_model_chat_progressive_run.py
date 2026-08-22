
import importlib.util, time
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_progress",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

old=m._model_chat
try:
    def fake(payload,activity_callback=None,cancel_check=None):
        activity_callback({"kind":"tool_call","name":"workspace.read","label":"Reading workspace file"})
        time.sleep(.08)
        activity_callback({"kind":"tool_result","name":"workspace.read","ok":True,"label":"File read"})
        time.sleep(.08)
        return {"status":"passed","answer_markdown":"done","agent_trace":[],"usage":{},"files":[]}
    m._model_chat=fake
    started=m._model_chat_start({"session_id":"s"})
    rid=started["run_id"]
    deadline=time.time()+2
    saw_progress=False
    while time.time()<deadline:
        st=m._model_chat_status({"run_id":rid,"after_seq":0})
        if st["activity_events"] and not st["finished"]:
            saw_progress=True
            break
        time.sleep(.01)
    assert saw_progress,"activity must be visible before final response"
    while not st["finished"] and time.time()<deadline:
        time.sleep(.02);st=m._model_chat_status({"run_id":rid,"after_seq":0})
    assert st["finished"] and st["result"]["answer_markdown"]=="done"
finally:
    m._model_chat=old
print("PASS Model Chat exposes activity before final answer")
