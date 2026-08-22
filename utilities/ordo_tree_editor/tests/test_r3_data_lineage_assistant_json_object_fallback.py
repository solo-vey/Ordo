import json
from utilities.ordo_tree_editor import editor_service as es


def test_data_lineage_assistant_accepts_analysis_alias_in_json_object_fallback(monkeypatch):
    package={"id":"lineage-json-object","source":{},"semantic_plan":{"interaction_contract":{"locale":"uk-UA","model_output_language":"uk"}}}
    es.PLAYBOOK_PACKAGES["lineage-json-object"]=package
    monkeypatch.setattr(es,"_live_credentials",lambda payload:{"provider":"custom","model":"m","base_url":"x","api_style":"chat_completions"})
    monkeypatch.setattr(es,"_provider_api_call",lambda credentials,system,context:(
        {},{},json.dumps({"analysis":"### Аналіз\nПояснення потоку даних."}),{}
    ))
    result=es._data_lineage_assistant({
        "package_id":"lineage-json-object",
        "entity":{"id":"N_X","label":"X","type":"transformation"},
        "context":{"incoming":[],"outgoing":[]},
        "messages":[]
    })
    assert result["answer_markdown"].startswith("### Аналіз")
