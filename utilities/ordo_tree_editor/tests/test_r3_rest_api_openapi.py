from __future__ import annotations
import json,re
from pathlib import Path
import yaml
from utilities.ordo_tree_editor.api_reference import build_spec

ROOT=Path(__file__).resolve().parents[1]
SERVICE=(ROOT/'editor_service.py').read_text(encoding='utf-8')
APP=(ROOT/'web'/'app.js').read_text(encoding='utf-8')
DOC=ROOT/'web'/'api-docs'

def implemented_routes():
    post_block=re.search(r'if path not in \{([^}]+)\}:',SERVICE,re.S)
    assert post_block, 'POST API allowlist not found'
    post={('post',p) for p in re.findall(r'"(/api/[^"]+)"',post_block.group(1))}
    get_block=SERVICE[SERVICE.index('    def do_GET'):SERVICE.index('\ndef run_server')]
    get={('get',p) for p in re.findall(r'if path == "(/api/[^"]+)"',get_block)}
    return post|get

def spec_routes(spec):
    return {(method,path) for path,item in spec['paths'].items() for method in item if method in {'get','post','put','patch','delete'}}

def test_openapi_covers_every_implemented_http_api_route_exactly():
    spec=build_spec()
    assert spec_routes(spec)==implemented_routes()
    assert len(spec_routes(spec))==50

def test_generated_openapi_files_match_generator_and_swagger_alias():
    expected=build_spec()
    assert json.loads((DOC/'openapi.json').read_text(encoding='utf-8'))==expected
    assert yaml.safe_load((DOC/'openapi.yaml').read_text(encoding='utf-8'))==expected
    assert yaml.safe_load((DOC/'swagger.yaml').read_text(encoding='utf-8'))==expected

def test_every_operation_is_grouped_and_documents_request_shape():
    spec=build_spec(); known={x['name'] for x in spec['tags']}
    for path,item in spec['paths'].items():
        for method,op in item.items():
            assert op['tags'] and op['tags'][0] in known, (method,path)
            assert op.get('summary'), (method,path)
            assert op.get('operationId'), (method,path)
            if method=='post':
                schema=op['requestBody']['content']['application/json']['schema']
                assert schema['type']=='object' and 'properties' in schema, (method,path)

def test_help_and_local_reference_surface_openapi():
    assert 'id:"rest-api"' in APP
    for token in ['/api-docs/','/api-docs/openapi.yaml','/api-docs/openapi.json','/api-docs/swagger.yaml']:
        assert token in APP
    html=(DOC/'index.html').read_text(encoding='utf-8')
    assert 'REST API Reference' in html and 'openapi.yaml' in html and 'openapi.json' in html and 'execute-playbook.html' in html
