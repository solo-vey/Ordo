
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_nexttarget",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
raw='{"resolved":{"base_revision":"runtime-owned","operations":[],"next_target":"N2"}}'
c=m._semantic_recovery_candidate_from_raw(raw,4,set())
assert c["status"]=="resolved"
assert c["next_id"]=="N2"
print("PASS next_target generic alias normalizes to next_id")
