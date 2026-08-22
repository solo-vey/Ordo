import importlib.util
import shutil
import tempfile
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("editor_service_generated_file_metadata", Path("editor_service.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

old_live = m._live_credentials
old_agent = m._model_chat_agent_loop
old_root = m.MODEL_CHAT_WORKSPACES
tmp = Path(tempfile.mkdtemp())
try:
    m.MODEL_CHAT_WORKSPACES = tmp
    m._live_credentials = lambda payload: {
        "provider": "custom",
        "model": "test",
        "api_style": "chat_completions",
    }

    def fake_agent(credentials, root, user_message, history, max_iterations=12, activity_callback=None, cancel_check=None):
        yaml_result = m._workspace_tool_execute(
            root,
            {
                "name": "workspace.write",
                "arguments": {
                    "path": "generated/demo.ordo.yaml",
                    "content": "title: Demo\nnodes: []\ngates: []\n",
                },
            },
        )
        assert yaml_result["ok"], yaml_result
        zip_result = m._workspace_tool_execute(
            root,
            {
                "name": "workspace.archive",
                "arguments": {
                    "source": "generated",
                    "output": "generated/demo.zip",
                },
            },
        )
        assert zip_result["ok"], zip_result
        return "Created.", [], {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}, []

    m._model_chat_agent_loop = fake_agent
    out = m._model_chat({
        "session_id": "generated-file-metadata",
        "messages": [{"role": "user", "content": "Create YAML and ZIP"}],
        "attachments": [],
    })

    files = {item["filename"]: item for item in out["files"]}
    assert set(files) == {"generated/demo.ordo.yaml", "generated/demo.zip"}, files
    for item in files.values():
        assert item["media_type"], item
        assert item["download_url"].startswith("/api/model-chat-workspace-file?"), item
    assert files["generated/demo.zip"]["media_type"] == "application/zip"

    archive_path = tmp / "generated-file-metadata" / "generated" / "demo.zip"
    assert archive_path.is_file() and zipfile.is_zipfile(archive_path)
finally:
    m._live_credentials = old_live
    m._model_chat_agent_loop = old_agent
    m.MODEL_CHAT_WORKSPACES = old_root
    shutil.rmtree(tmp, ignore_errors=True)

print("PASS Model Chat generated YAML/ZIP metadata uses generic media type resolution")
