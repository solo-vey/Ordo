
import importlib.util, copy
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_capcross",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

old_sessions=copy.deepcopy(m.LIVE_SESSIONS)
old_cache=copy.deepcopy(m.PROVIDER_CAPABILITY_CACHE)
old_runtime=copy.deepcopy(m.LIVE_RUNTIME)
try:
    m.LIVE_SESSIONS.clear()
    m.PROVIDER_CAPABILITY_CACHE.clear()
    m.LIVE_RUNTIME.update({"provider":"custom","model":"","structured_output_mode":"auto"})

    m._remember_provider_capability({
      "provider":"custom","base_url":"http://local:8555/v1","model":"gemma",
      "api_style":"chat_completions","supports_json_schema":True
    })

    m.LIVE_SESSIONS["new"]={
      "provider":"custom","base_url":"http://local:8555/v1","model":"gemma",
      "api_key":"","structured_output_mode":"auto"
    }
    creds=m._live_credentials({"session_id":"new"})
    assert creds["capability_profile"]["supports_json_schema"] is True
    mode,source=m._provider_structured_output_mode(creds)
    assert mode=="strict_json_schema",(mode,source)
    assert source=="recorded_capability_probe"

    m.LIVE_SESSIONS["other"]={
      "provider":"custom","base_url":"http://local:8555/v1","model":"other",
      "api_key":"","structured_output_mode":"auto"
    }
    creds2=m._live_credentials({"session_id":"other"})
    assert creds2.get("capability_profile") is None
finally:
    m.LIVE_SESSIONS.clear();m.LIVE_SESSIONS.update(old_sessions)
    m.PROVIDER_CAPABILITY_CACHE.clear();m.PROVIDER_CAPABILITY_CACHE.update(old_cache)
    m.LIVE_RUNTIME.clear();m.LIVE_RUNTIME.update(old_runtime)
print("PASS provider capability survives session changes and remains model-bound")
