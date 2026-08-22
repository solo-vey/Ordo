from __future__ import annotations
import copy,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import editor_service as es


def _semantic():
    return {
      "id":"N_RISK_FACTOR_IDENTITY_DRAFT","kind":"interactive_node",
      "semantic_source":{"title":"identity"},
      "execution_traits":{"model_executed":True,"model_executed_phases":["enter"],"requires_analyst":True},
      "state_contract":{"writes":["risk_factor_identity.name_ua"],"semantic_objects":["risk_factor_candidate"],"reads_hint":["risk_factor_candidate"],"patch_template":[]},
      "routes":[{"key":"next","target":"DONE","kind":"canonical"}],
      "output_contract":{"contract":"NodeExecutionResult","required":["assistant_message","state_patch","route_key","needs_analyst","next_intent","rationale_short","action"]}
    }


def test_hallucinated_path_is_retried_not_generic_execution_error(monkeypatch):
    source={"graph_contract":{"entry_node":"N_RISK_FACTOR_IDENTITY_DRAFT","external_terminal_targets":["DONE"]},"state":{"schema":{}},"nodes":[{"id":"N_RISK_FACTOR_IDENTITY_DRAFT","action":"AI.DRAFT","next":"DONE"}],"gates":[]}
    old=copy.deepcopy(es.PLAYBOOK_PACKAGE)
    calls=[]
    bad={"assistant_message":"draft","state_patch":{"base_revision":0,"operations":[{"op":"set","path":"riskfactorproposal","value":{"x":1},"basis":"generated","reason":"hallucinated","row_key":None,"row_match":None}]},"route_key":None,"needs_analyst":True,"next_intent":"await_analyst_input","rationale_short":"draft","action":"ASK"}
    good={"assistant_message":"draft","state_patch":{"base_revision":0,"operations":[]},"route_key":None,"needs_analyst":True,"next_intent":"await_analyst_input","rationale_short":"draft","action":"ASK"}
    try:
      es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update({"id":"kf018","source":source,"semantic_plan":{"elements":{"N_RISK_FACTOR_IDENTITY_DRAFT":_semantic()},"resources":{}},"semantic_plan_status":{"valid":True},"resources":{}})
      monkeypatch.setattr(es,"_live_credentials",lambda payload:{"provider":"custom","base_url":"http://x","api_style":"chat_completions","model":"gemma-stub","api_key":None})
      def provider(*a,**k):
        i=len(calls); calls.append(i)
        obj=bad if i==0 else good
        return {},{},json.dumps(obj),{"input_tokens":10,"output_tokens":5,"total_tokens":15,"cached_tokens":0,"reasoning_tokens":0}
      monkeypatch.setattr(es,"_provider_api_call",provider)
      r=es._call_openai_live({"package_id":"kf018","source":source,"current_id":"N_RISK_FACTOR_IDENTITY_DRAFT","phase":"enter","state":{"risk_factor_candidate":"x"},"history":[]})
      assert r["run_status"] != "halted"
      assert r["await_analyst"] is True
      assert len(calls)==2
      attempts=r["debug"]["semantic_model_attempts"]
      assert attempts[0]["validation"]["valid"] is False
      assert any("outside write allowlist" in x for x in attempts[0]["validation"]["errors"])
      assert attempts[1]["validation"]["valid"] is True
    finally:
      es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update(old)
