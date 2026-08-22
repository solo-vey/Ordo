import base64, importlib.util, io, json, shutil, tempfile, zipfile
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_debug_attachment_history",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
old=m.MODEL_CHAT_WORKSPACES
tmp=Path(tempfile.mkdtemp())
try:
    m.MODEL_CHAT_WORKSPACES=tmp
    secret=base64.b64encode(b"ATTACHMENT-BODY-MUST-NOT-BE-IN-DEBUG").decode("ascii")
    messages=[{"role":"user","content":"source","files":[{"filename":"source.zip","media_type":"application/zip","size_bytes":32,"content_base64":secret}]}]
    out=m._model_chat_export({"debug":True,"session_id":"s","messages":messages,"attachments":[]})
    raw=base64.b64decode(out["content_base64"])
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        conv=z.read("conversation.json").decode("utf-8")
        at=json.loads(z.read("attachments.json").decode("utf-8"))
    assert secret not in conv and "ATTACHMENT-BODY-MUST-NOT-BE-IN-DEBUG" not in conv
    parsed=json.loads(conv)
    assert parsed[0]["files"][0]["filename"]=="source.zip"
    assert "content_base64" not in parsed[0]["files"][0]
    assert at and at[0]["filename"]=="source.zip" and at[0]["message_index"]==0
finally:
    m.MODEL_CHAT_WORKSPACES=old
    shutil.rmtree(tmp,ignore_errors=True)
print("PASS debug export captures historical attachment metadata without bodies")
