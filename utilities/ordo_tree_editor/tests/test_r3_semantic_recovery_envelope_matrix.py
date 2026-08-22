
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_envmatrix",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

allowed={"x"}
cases=[
 ('{"status":"resolved","state_patch":{"operations":[{"op":"set","path":"x","value":1}]},"next_id":"N2"}',"resolved","N2"),
 ('{"resolved":{"base_revision":"runtime-owned","operations":[{"op":"set","path":"x","value":1}],"next_node":"N2"}}',"resolved","N2"),
 ('{"needs_analyst":{"reason":"missing","message":"Need input"}}',"needs_analyst",None),
 ('{"unsupported":{"reason":"cannot execute"}}',"unsupported",None),
]
for raw,status,next_id in cases:
    c=m._semantic_recovery_candidate_from_raw(raw,7,allowed)
    assert c["status"]==status,(raw,c)
    assert c.get("next_id")==next_id,(raw,c)
    assert c["state_patch"]["base_revision"]==7
    assert isinstance(c["state_patch"]["operations"],list)
print("PASS semantic recovery generic envelope matrix")
