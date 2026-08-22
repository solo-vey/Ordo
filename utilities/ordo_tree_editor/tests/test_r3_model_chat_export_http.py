
import importlib.util, threading, json, urllib.request, tempfile, shutil
from pathlib import Path
from http.server import ThreadingHTTPServer

spec=importlib.util.spec_from_file_location("editor_service_export_http",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=m.MODEL_CHAT_WORKSPACES
tmp=Path(tempfile.mkdtemp())
m.MODEL_CHAT_WORKSPACES=tmp
server=ThreadingHTTPServer(("127.0.0.1",0),m.EditorHandler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
try:
    url=f"http://127.0.0.1:{server.server_address[1]}/api/model-chat-export"
    body=json.dumps({"debug":False,"session_id":"x","messages":[{"role":"user","content":"hello"}]}).encode()
    req=urllib.request.Request(url,data=body,headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=5) as resp:
        data=json.loads(resp.read().decode())
    assert data["status"]=="passed" and data["filename"].endswith(".md")
finally:
    server.shutdown();server.server_close();m.MODEL_CHAT_WORKSPACES=old;shutil.rmtree(tmp,ignore_errors=True)
print("PASS /api/model-chat-export HTTP endpoint")
