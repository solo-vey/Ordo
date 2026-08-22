from __future__ import annotations
import copy, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import editor_service as es


def _base_semantic():
    return {
        "id":"N_SCOPE","kind":"model_node","semantic_source":{"title":"scope"},
        "execution_traits":{"model_executed":True,"model_executed_phases":["enter"],"requires_analyst":True},
        "state_contract":{"writes":["scope.value"],"semantic_objects":[],"reads_hint":[],"patch_template":[]},
        "routes":[{"key":"next","target":"DONE","kind":"canonical"}],
        "output_contract":{"contract":"NodeExecutionResult","required":["assistant_message","state_patch","route_key","needs_analyst","next_intent","rationale_short","action"]}
    }


def test_kf007_missing_mechanical_fields_are_runtime_owned():
    cand={"assistant_message":"Уточніть область.","state_patch":{"base_revision":0,"operations":[]},"route_key":None,"rationale_short":"need analyst","action":"ASK"}
    out, adaptations=es._adapt_runtime_owned_node_envelope(cand, semantic_element=_base_semantic(), semantic_traits=_base_semantic()["execution_traits"], phase="enter")
    assert out["needs_analyst"] is True
    assert out["next_intent"] == "await_analyst_input"
    assert {a["kind"] for a in adaptations} >= {"derive_needs_analyst","derive_next_intent"}


def test_kf007_statepatch_envelope_misplaced_in_state_updates_is_reinterpreted_not_committed_as_state():
    cand={
      "assistant_message":"ok","route_key":"next","needs_analyst":False,"next_intent":"continue","action":"CONTINUE",
      "state_updates":{"base_revision":0,"operations":[{"op":"set","path":"scope.value","value":"x","basis":"generated","reason":"test","row_key":None,"row_match":None}]}
    }
    out, adaptations=es._adapt_runtime_owned_node_envelope(cand, semantic_element=_base_semantic(), semantic_traits=_base_semantic()["execution_traits"], phase="respond")
    assert "state_updates" not in out
    assert out["state_patch"]["operations"][0]["path"] == "scope.value"
    assert any(a["kind"]=="state_patch_envelope_from_state_updates" for a in adaptations)


def test_kf007_exact_live_failure_class_no_longer_exhausts_retries(monkeypatch):
    source={
      "graph_contract":{"entry_node":"N_SCOPE","external_terminal_targets":["DONE"]},
      "state":{"schema":{"scope":{"value":None}}},
      "nodes":[{"id":"N_SCOPE","action":"AI.DRAFT","next":"DONE"}],"gates":[]
    }
    sem=_base_semantic()
    old_pkg=copy.deepcopy(es.PLAYBOOK_PACKAGE)
    try:
      es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update({"id":"kf007","source":source,"semantic_plan":{"elements":{"N_SCOPE":sem},"resources":{}},"semantic_plan_status":{"valid":True},"resources":{}})
      monkeypatch.setattr(es,"_live_credentials",lambda payload:{"provider":"custom","base_url":"http://x","api_style":"chat_completions","model":"gemma-stub","api_key":None})
      # Mirrors the live attempt class: semantic content is usable, but Gemma omits the two mechanical NodeExecutionResult fields.
      raw=json.dumps({"assistant_message":"Уточніть область ризику.","state_patch":{"base_revision":0,"operations":[]},"route_key":None,"rationale_short":"Потрібне уточнення","action":"ASK"},ensure_ascii=False)
      monkeypatch.setattr(es,"_provider_api_call",lambda *a,**k: ({},{},raw,{"input_tokens":1,"output_tokens":1,"total_tokens":2,"cached_tokens":0,"reasoning_tokens":0}))
      r=es._call_openai_live({"package_id":"kf007","source":source,"current_id":"N_SCOPE","phase":"enter","state":{},"history":[]})
      assert r["run_status"] != "halted"
      assert r["await_analyst"] is True
      attempts=r["debug"]["semantic_model_attempts"]
      assert attempts[0]["validation"]["valid"] is True
      kinds={a["kind"] for a in attempts[0]["runtime_owned_envelope_adaptations"]}
      assert {"derive_needs_analyst","derive_next_intent"} <= kinds
    finally:
      es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update(old_pkg)
