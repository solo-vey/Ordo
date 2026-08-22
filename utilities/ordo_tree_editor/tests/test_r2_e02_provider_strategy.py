from __future__ import annotations
import pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import editor_service as es

GOOD={'type':'object','additionalProperties':False,'required':['x'],'properties':{'x':{'type':'string'}}}

def test_auto_provider_strategy_is_non_speculative():
    assert es._provider_structured_output_mode({'provider':'openai','api_style':'chat_completions'})[0]=='strict_json_schema'
    assert es._provider_structured_output_mode({'provider':'custom','api_style':'chat_completions'})[0]=='json_object'

def test_probe_can_explicitly_promote_custom_to_strict():
    c={'provider':'custom','api_style':'chat_completions','structured_output_mode':'strict_json_schema'}
    assert es._provider_structured_output_mode(c)==('strict_json_schema','explicit_capability_profile')
    assert es._runtime_strict_schema_compatible(GOOD,c)[0] is True

def test_probe_can_explicitly_demote_to_plain():
    c={'provider':'custom','api_style':'chat_completions','structured_output_mode':'plain'}
    assert es._provider_structured_output_mode(c)==('plain','explicit_capability_profile')
    ok,reason=es._runtime_strict_schema_compatible(GOOD,c)
    assert ok is False and 'plain' in reason

def test_bad_mode_fails_closed():
    try:
        es._provider_structured_output_mode({'provider':'custom','api_style':'chat_completions','structured_output_mode':'wishful'})
    except ValueError as exc:
        assert 'Unsupported structured_output_mode' in str(exc)
    else:
        raise AssertionError('bad mode must fail')
