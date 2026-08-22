
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_context_budget",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

detail='{"error":{"message":"This model\'s maximum context length is 35000 tokens. However, you requested 8000 output tokens and your prompt contains at least 27001 input tokens, for a total of at least 35001 tokens."}}'
assert m._context_limit_retry_tokens(detail,8000)==7743
assert m._context_limit_retry_tokens("unrelated",8000) is None
print("PASS adaptive context-window output budget")
