import importlib.util, pathlib, zipfile, json

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('editor_service', ROOT / 'editor_service.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_generic_nested_and_text_resource_discovery():
    resources = {
        'tools/validate_applied_json_content.py': 'print("ok")',
        'contracts/VALIDATION_CONTRACT.json': '{}',
    }
    record = {
        'id':'N_RUN_ROOT_VALIDATOR',
        'question':'Run python tools/validate_applied_json_content.py --contract contracts/VALIDATION_CONTRACT.json --output reports/runtime/root_validation.json',
        'node_context':{
            'allowed_tools':['tools/validate_applied_json_content.py'],
            'knowledge_refs':['contracts/VALIDATION_CONTRACT.json'],
        }
    }
    refs = mod._generic_record_resource_references(record, resources)
    paths = {r['path'] for r in refs}
    assert 'tools/validate_applied_json_content.py' in paths
    assert 'contracts/VALIDATION_CONTRACT.json' in paths
    assert 'reports/runtime/root_validation.json' not in paths

def test_payload_deduplicates_same_resource_across_origins():
    source={'nodes':[{
        'id':'N_RUN_ROOT_VALIDATOR',
        'question':'Run tools/validate_applied_json_content.py',
        'node_context':{'allowed_tools':['tools/validate_applied_json_content.py']}
    }], 'gates':[]}
    package={'resources':{'tools/validate_applied_json_content.py':'print(1)'}}
    payload=mod._template_inspector_payload(package,source,'N_RUN_ROOT_VALIDATOR')
    assert len(payload['references']) == 1
    ref=payload['references'][0]
    assert ref['available'] is True
    assert ref['resolved_path']=='tools/validate_applied_json_content.py'
    assert any('allowed_tools' in x for x in ref['roles'])
