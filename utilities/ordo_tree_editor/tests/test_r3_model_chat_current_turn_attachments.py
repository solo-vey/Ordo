import base64, importlib.util, io, json, shutil, tempfile, zipfile
from pathlib import Path

spec=importlib.util.spec_from_file_location("editor_service_current_attachments",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def zip_attachment(name, files):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        for path,content in files.items(): z.writestr(path,content)
    raw=buf.getvalue()
    return {"filename":name,"media_type":"application/zip","size_bytes":len(raw),"content_base64":base64.b64encode(raw).decode("ascii")}

old_ws=m.MODEL_CHAT_WORKSPACES
old_creds=m._live_credentials
old_call=m._provider_api_call
tmp=Path(tempfile.mkdtemp())
captured=[]
try:
    m.MODEL_CHAT_WORKSPACES=tmp
    m._live_credentials=lambda payload:{"provider":"custom","model":"test"}
    def fake_call(credentials, system, context):
        captured.append((system,json.loads(json.dumps(context))))
        raw=json.dumps({"type":"final","message":"ok"})
        return {},{},raw,{"prompt_tokens":1,"completion_tokens":1,"total_tokens":2}
    m._provider_api_call=fake_call

    first=zip_attachment("FIRST.zip",{"START_HERE.md":"first"})
    second=zip_attachment("SECOND.zip",{"00_READ_FIRST/HANDOFF_PROMPT_UA.md":"second","doc.md":"payload"})

    out1=m._model_chat({"session_id":"s","messages":[{"role":"user","content":"start","files":[first]}],"attachments":[first]})
    assert out1["workspace"]["stored_attachments"][0]["filename"]=="FIRST.zip"

    messages=[
        {"role":"user","content":"start","files":[first]},
        {"role":"assistant","content":"ready","files":[]},
        {"role":"user","content":"here are the source materials","files":[second]},
    ]
    out2=m._model_chat({"session_id":"s","messages":messages,"attachments":[second]})
    current=captured[-1][1]["current_attachments"]
    assert len(current)==1 and current[0]["filename"]=="SECOND.zip", current
    assert current[0]["workspace_path"]=="uploads/SECOND.zip"
    assert current[0]["extracted_to"]=="extracted/SECOND"
    assert "current_attachments is the authoritative list" in captured[-1][0]
    assert captured[-1][1]["conversation"][0]["files"][0]["filename"]=="FIRST.zip"
    assert "content_base64" not in captured[-1][1]["conversation"][0]["files"][0]

    # Transport fallback: a file-card preserved in the newest user message is enough
    # to ingest the attachment even if the parallel `attachments` field is absent.
    third=zip_attachment("THIRD.zip",{"input.md":"third"})
    out3=m._model_chat({"session_id":"s2","messages":[{"role":"user","content":"","files":[third]}],"attachments":[]})
    assert out3["workspace"]["stored_attachments"][0]["filename"]=="THIRD.zip"
    assert captured[-1][1]["current_attachments"][0]["filename"]=="THIRD.zip"
finally:
    m.MODEL_CHAT_WORKSPACES=old_ws
    m._live_credentials=old_creds
    m._provider_api_call=old_call
    shutil.rmtree(tmp,ignore_errors=True)
print("PASS current-turn Model Chat attachments are explicit and persistent")
