
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_sem_schema",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

creds={
 "provider":"custom","api_style":"chat_completions","base_url":"http://local/v1","model":"gemma",
 "structured_output_mode":"auto",
 "capability_profile":{"supports_json_schema":True,"base_url":"http://local/v1","model":"gemma","api_style":"chat_completions"},
}
ok,reason=m._runtime_strict_schema_compatible(m._semantic_recovery_schema(),creds)
assert ok,reason
print("PASS semantic recovery schema uses strict JSON schema when capability probe supports it")
