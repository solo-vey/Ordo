
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_runtime_retry",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

old=m._provider_api_call
calls=[]
try:
    def fake(credentials,system,context):
        calls.append((system,context))
        if len(calls)==1:
            raw='{"state_patch":{"base_revision":0,"operations":{"op":"set","path":"x","value":1}}}'
        else:
            raw='{"route_key":"next","state_patch":{"base_revision":0,"operations":[{"op":"set","path":"x","value":1,"basis":"derived","reason":"repair"}]}}'
        return {},{},raw,{"total_tokens":1}
    m._provider_api_call=fake
    result,req,api,raw,usage,attempts=m._runtime_model_call_with_guard(
        credentials={},system_text="s",context={},
        current_revision=0,state={},allowed_paths={"x"},allowed_route_keys={"next"},
        max_attempts=3,
    )
    assert len(calls)==2
    assert len(attempts)==2
    assert result["route_key"]=="next"
    assert "runtime_validation_errors" in calls[1][1]
finally:
    m._provider_api_call=old
print("PASS generic runtime guard repairs malformed model response")
