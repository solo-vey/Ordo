import io
import json
import urllib.error
from unittest.mock import patch
from utilities.ordo_tree_editor import editor_service as es

class Resp:
    def __enter__(self): return self
    def __exit__(self,*a): return False
    def read(self):
        return json.dumps({"choices":[{"message":{"content":"{\"probe\":\"ok\"}"}}]}).encode()


def creds():
    return {"provider":"custom","api_key":"","model":"m","base_url":"http://example/v1","api_style":"chat_completions","structured_output_mode":"auto"}


def test_probe_records_supported_from_strict_request():
    with patch.object(es.urllib.request,'urlopen',return_value=Resp()):
        out=es._probe_provider_json_schema_capability(creds())
    assert out['status']=='recorded'
    assert out['supports_json_schema'] is True
    assert out['evidence']=='strict_schema_request_accepted'


def test_probe_records_explicit_400_as_unsupported():
    err=urllib.error.HTTPError('u',400,'bad',{},io.BytesIO(b'unsupported response_format'))
    with patch.object(es.urllib.request,'urlopen',side_effect=err):
        out=es._probe_provider_json_schema_capability(creds())
    assert out['supports_json_schema'] is False
    assert out['http_status']==400
