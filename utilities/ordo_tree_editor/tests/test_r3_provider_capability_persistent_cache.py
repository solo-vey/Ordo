
import importlib.util, tempfile, json, shutil, copy
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_cappersist",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

old_path=m.PROVIDER_CAPABILITY_CACHE_PATH
old_cache=copy.deepcopy(m.PROVIDER_CAPABILITY_CACHE)
tmp=Path(tempfile.mkdtemp())
try:
    m.PROVIDER_CAPABILITY_CACHE_PATH=tmp/"caps.json"
    m.PROVIDER_CAPABILITY_CACHE.clear()
    profile={"provider":"custom","base_url":"http://x/v1","model":"m","api_style":"chat_completions","supports_json_schema":True}
    m._remember_provider_capability(profile)
    assert m.PROVIDER_CAPABILITY_CACHE_PATH.is_file()
    m.PROVIDER_CAPABILITY_CACHE.clear()
    m._load_provider_capability_cache()
    got=m._cached_provider_capability("custom","http://x/v1","m","chat_completions")
    assert got and got["supports_json_schema"] is True
finally:
    m.PROVIDER_CAPABILITY_CACHE_PATH=old_path
    m.PROVIDER_CAPABILITY_CACHE.clear();m.PROVIDER_CAPABILITY_CACHE.update(old_cache)
    shutil.rmtree(tmp,ignore_errors=True)
print("PASS provider capability evidence persists across process restart")
