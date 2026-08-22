import editor_service as svc

def test_generic_startup_model_parameters_are_not_openai_hardcoded():
    cfg=svc._resolve_startup_runtime_config(provider='custom', model='acme/model-x', base_url='http://example.test/v1', api_key=None)
    assert cfg['provider']=='custom'
    assert cfg['model']=='acme/model-x'
    assert cfg['base_url']=='http://example.test/v1'
    assert cfg['enabled'] is True

def test_gitlab_tree_url_parser_supports_project_ref_and_subpath():
    parsed=svc._parse_gitlab_tree_url('https://gitlab.example/ML/promts/-/tree/main/analitics/lu/ordo')
    assert parsed=={
        'origin':'https://gitlab.example',
        'project':'ML/promts',
        'ref':'main',
        'path':'analitics/lu/ordo',
    }
