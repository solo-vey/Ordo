
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_cap_profile",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

base={"provider":"custom","api_style":"chat_completions","base_url":"http://local/v1","model":"gemma","structured_output_mode":"auto"}
mode,source=m._provider_structured_output_mode(dict(base))
assert mode=="json_object" and source=="compatibility_default_until_probe"

yes=dict(base,capability_profile={"supports_json_schema":True,"base_url":"http://local/v1","model":"gemma","api_style":"chat_completions"})
mode,source=m._provider_structured_output_mode(yes)
assert mode=="strict_json_schema" and source=="recorded_capability_probe"

no=dict(base,capability_profile={"supports_json_schema":False,"base_url":"http://local/v1","model":"gemma","api_style":"chat_completions"})
mode,source=m._provider_structured_output_mode(no)
assert mode=="json_object" and source=="recorded_capability_probe"

# Stale evidence must not be applied to another model.
stale=dict(base,capability_profile={"supports_json_schema":True,"base_url":"http://local/v1","model":"other","api_style":"chat_completions"})
mode,source=m._provider_structured_output_mode(stale)
assert mode=="json_object" and source=="compatibility_default_until_probe"
print("PASS provider capability probe evidence controls auto structured mode")
