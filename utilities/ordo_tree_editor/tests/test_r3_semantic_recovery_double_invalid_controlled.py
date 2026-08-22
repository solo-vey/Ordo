import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('editor_service_double_invalid',Path('editor_service.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old_provider=m._provider_api_call; old_context=m._package_context_for_record; old_allow=m._alpha20_write_allowlist; old_schemas=m._alpha20_value_schemas; old_variants=m._alpha20_operation_variants
try:
    m._provider_api_call=lambda *a,**k: ({},{},'{"status":"bad","state_patch":{"base_revision":0,"operations":[]}}',{'total_tokens':1})
    m._package_context_for_record=lambda record:{'resolved_resources':[]}
    m._alpha20_write_allowlist=lambda *a,**k:[]
    m._alpha20_value_schemas=lambda *a,**k:{}
    m._alpha20_operation_variants=lambda *a,**k:{}
    result=m._safe_semantic_model_recovery(credentials={'provider':'x','model':'y'},record={},kind='node',current_id='N1',phase='enter',state={},routes=[],semantic_element={},current_revision=0,failure_class='test',failure_detail={})
    assert isinstance(result,dict)
    assert result.get('run_status')=='halted'
    assert result.get('failure_class')=='contract_unsatisfiable_by_model'
finally:
    m._provider_api_call=old_provider; m._package_context_for_record=old_context; m._alpha20_write_allowlist=old_allow; m._alpha20_value_schemas=old_schemas; m._alpha20_operation_variants=old_variants
print('PASS double invalid semantic recovery becomes controlled halt')
