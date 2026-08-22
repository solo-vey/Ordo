
import importlib.util, io, contextlib
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_debuglog",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    m._runtime_debug_log("test.event",{"api_key":"SECRET","nested":{"token":"TOKEN","value":"ok"},"text":"x"*13000})
out=buf.getvalue()
assert "[ORDO_RUNTIME_DEBUG] test.event" in out
assert "SECRET" not in out and "TOKEN" not in out
assert "***REDACTED***" in out and "<truncated " in out
print("PASS structured runtime console log")
