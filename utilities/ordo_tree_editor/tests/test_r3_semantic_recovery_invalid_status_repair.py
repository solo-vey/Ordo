import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('editor_service_invalid_status',Path('editor_service.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old_provider=m._provider_api_call; old_context=m._package_context_for_record; old_allow=m._alpha20_write_allowlist; old_schemas=m._alpha20_value_schemas; old_variants=m._alpha20_operation_variants
try:
    calls=[]
    def fake_provider(credentials,system,context):
        calls.append(context)
        if len(calls)==1:
            return {},{},'{"status":"okay","reason":"x","assistant_message":"","next_id":null,"state_patch":{"base_revision":0,"operations":[]}}',{'total_tokens':1}
        return {},{},'{"status":"unsupported","reason":"cannot resolve safely","assistant_message":"","next_id":null,"state_patch":{"base_revision":0,"operations":[]}}',{'total_tokens':1}
    m._provider_api_call=fake_provider
    m._package_context_for_record=lambda record:{'resolved_resources':[]}
    m._alpha20_write_allowlist=lambda *a,**k:[]
    m._alpha20_value_schemas=lambda *a,**k:{}
    m._alpha20_operation_variants=lambda *a,**k:{}
    result=m._safe_semantic_model_recovery(credentials={},record={},kind='node',current_id='N1',phase='enter',state={},routes=[],semantic_element={},current_revision=0,failure_class='test',failure_detail={})
    assert result is None
    assert len(calls)==2
    assert 'validation_errors' in calls[1]
    assert any('status must be' in str(x) for x in calls[1]['validation_errors'])
finally:
    m._provider_api_call=old_provider; m._package_context_for_record=old_context; m._alpha20_write_allowlist=old_allow; m._alpha20_value_schemas=old_schemas; m._alpha20_operation_variants=old_variants
print('PASS invalid semantic recovery status enters repair')
