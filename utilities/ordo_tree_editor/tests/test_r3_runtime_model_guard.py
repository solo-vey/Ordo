
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_runtime_guard",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

state={}
bad={"state_patch":{"base_revision":99,"operations":{"op":"set","path":"x","value":1}}}
norm,errs,dbg=m._runtime_model_candidate_guard(
    bad,current_revision=0,state=state,allowed_paths={"x"},allowed_route_keys={"next"}
)
assert errs and any("operations" in e for e in errs),errs

good={"route_key":"next","state_patch":{"base_revision":99,"operations":[{"op":"set","path":"x","value":1,"basis":"derived","reason":"test"}]}}
norm2,errs2,dbg2=m._runtime_model_candidate_guard(
    good,current_revision=0,state=state,allowed_paths={"x"},allowed_route_keys={"next"}
)
assert not errs2,errs2
assert norm2["state_patch"]["base_revision"]==0
assert dbg2["dry_run_commit"]["committed"]

wrong_route={"route_key":"bad","state_patch":{"base_revision":0,"operations":[]}}
_,errs3,_=m._runtime_model_candidate_guard(
    wrong_route,current_revision=0,state=state,allowed_paths=set(),allowed_route_keys={"next"}
)
assert any("route_key" in e for e in errs3)
print("PASS generic runtime model candidate guard")
