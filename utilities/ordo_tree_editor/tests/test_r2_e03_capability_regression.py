from __future__ import annotations
import pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import editor_service as es

GOOD={"type":"object","additionalProperties":False,"required":["x"],"properties":{"x":{"type":"string"}}}
STRICT={"provider":"custom","api_style":"chat_completions","structured_output_mode":"strict_json_schema"}

def test_e03_unsupported_schema_keyword_fails_provider_strict_compatibility():
    schema=dict(GOOD); schema["if"]={"properties":{"x":{"const":"a"}}}
    ok,reason=es._runtime_strict_schema_compatible(schema,STRICT)
    assert not ok and "incompatible" in reason

def test_e03_additional_properties_must_be_false():
    schema={"type":"object","required":["x"],"properties":{"x":{"type":"string"}}}
    ok,_=es._runtime_strict_schema_compatible(schema,STRICT)
    assert not ok

def test_e03_anyof_closed_operation_variants_are_supported():
    variant=lambda op:{"type":"object","additionalProperties":False,"required":["op"],"properties":{"op":{"const":op}}}
    schema={"anyOf":[variant("set"),variant("append")]}
    assert es._runtime_strict_schema_compatible(schema,STRICT)[0]

def test_e03_enum_and_null_are_supported():
    schema={"type":"object","additionalProperties":False,"required":["v"],"properties":{"v":{"type":["string","null"],"enum":["x",None]}}}
    assert es._runtime_strict_schema_compatible(schema,STRICT)[0]

def test_e03_oversized_schema_uses_capability_limit_fail_closed():
    creds=dict(STRICT,max_json_schema_chars=60)
    ok,reason=es._runtime_strict_schema_compatible(GOOD,creds)
    assert not ok and "exceeds provider capability limit" in reason

def test_e03_invalid_schema_limit_fails_closed():
    try:
        es._runtime_strict_schema_compatible(GOOD,dict(STRICT,max_json_schema_chars="bad"))
    except ValueError as exc:
        assert "Invalid max_json_schema_chars" in str(exc)
    else:
        raise AssertionError("invalid capability must fail closed")
