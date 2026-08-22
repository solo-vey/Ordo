
import importlib.util, threading, json, urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer

spec=importlib.util.spec_from_file_location("editor_service_http_contract",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=m._model_chat
m._model_chat=lambda payload: {"status":"passed","answer_markdown":"pong","files":[]}
server=ThreadingHTTPServer(("127.0.0.1",0),m.EditorHandler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
try:
    url=f"http://127.0.0.1:{server.server_address[1]}/api/model-chat"
    body=json.dumps({"session_id":"x","messages":[{"role":"user","content":"ping"}],"attachments":[]}).encode()
    req=urllib.request.Request(url,data=body,headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=5) as resp:
        data=json.loads(resp.read().decode())
    assert data["answer_markdown"]=="pong"
finally:
    server.shutdown();server.server_close();m._model_chat=old
print("PASS /api/model-chat HTTP browser contract")
