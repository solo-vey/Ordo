
import copy, json
from utilities.ordo_tree_editor import editor_service as es

def _source():
    p=es._settings_language_dir()/"examples/source/interaction_process_rail_conversation_example.ordo.yaml"
    return es.parse_yaml(p.read_text(encoding="utf-8"))

def test_language_catalog_includes_unspecified_settings():
    source=_source()
    payload=es._playbook_settings_payload({"id":"x","source_name":"x","source":source})
    assert payload["summary"]["total_settings"] >= 30
    assert payload["summary"]["not_specified"] > 0
    flat=[f for g in payload["groups"] for f in g["fields"]]
    startup=next(f for f in flat if f["path"]=="startup_package_profile.default_startup_mode")
    assert startup["specified"] is False
    assert startup["current_value"] is None

def test_registry_options_are_shown_for_unspecified_fields():
    payload=es._playbook_settings_payload({"id":"x","source_name":"x","source":_source()})
    flat=[f for g in payload["groups"] for f in g["fields"]]
    field=next(f for f in flat if f["path"]=="startup_package_profile.default_startup_mode")
    assert isinstance(field["options"],list)

def test_settings_assistant_is_read_only(monkeypatch):
    source=_source()
    before=copy.deepcopy(source)
    package={"id":"pkg","source_name":"x","source":source,"semantic_plan":{"interaction_contract":{"locale":"uk-UA","model_output_language":"uk"}}}
    es.PLAYBOOK_PACKAGES["pkg"]=package
    monkeypatch.setattr(es,"_live_credentials",lambda payload:{"provider":"test","model":"m","base_url":"x","api_style":"chat_completions","structured_output_mode":"json_object"})
    monkeypatch.setattr(es,"_provider_api_call",lambda credentials,system,context:(
        {},{},json.dumps({"answer_markdown":"Аналіз.","yaml_settings_block":"process_rail:\n  backtracking: enabled"}),{}
    ))
    out=es._playbook_settings_assistant({"package_id":"pkg","mode":"chat","message":"Зміни backtracking","messages":[]})
    assert out["yaml_settings_block"].startswith("process_rail:")
    assert source==before
