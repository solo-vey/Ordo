
import json
import shutil
from pathlib import Path
from utilities.ordo_tree_editor import editor_service as es
from utilities.ordo_tree_editor.integrated_compiler.ordo_yaml_semantics import classify

def _response_node():
    return {
        "id":"N_BUILD_VALID_RESPONSE",
        "question":"На основі `reports/runtime/validation_report.json` дай аналітику коротку відповідь VALID або VALID_WITH_WARNINGS, кількість errors/warnings і посилання на готовий JSON report.",
        "answer_type":"structured_record",
        "node_context":{"knowledge_refs":["reports/runtime/validation_report.json"],"allowed_tools":[]},
        "on_answer":{"update_state":{"validation_report":"$answer.validation_report","user_verdict":"$answer.user_verdict"},"next":"END_VALIDATION_COMPLETE"},
    }

def test_response_synthesis_is_model_not_human():
    node=_response_node()
    traits=classify(node,False)
    assert traits["runtime_executor"]=="semantic_model"
    assert traits["requires_analyst"] is False
    assert traits["model_executed_phases"]==["enter"]
    assert es._human_interaction_policy(node,"node")["requires_human"] is False

def test_runtime_report_is_resolved_as_model_context_and_artifact():
    package={"id":"artifactctx","resources":{}}
    pt=es._ACTIVE_PLAYBOOK_PACKAGE.set(package)
    rt=es._ACTIVE_RUN_CONTEXT.set({"package_id":"artifactctx","session_id":"s86","run_id":"r86"})
    try:
        ws=es._runtime_workspace()
        report=ws/"reports/runtime/validation_report.json"
        report.parent.mkdir(parents=True,exist_ok=True)
        report.write_text(json.dumps({"status":"VALID","errors":[],"warnings":[]}),encoding="utf-8")
        ctx=es._package_context_for_record(_response_node())
        rows=ctx["resolved_resources"]
        assert any(x["path"]=="reports/runtime/validation_report.json" and x["reason"]=="runtime_artifact" and '"VALID"' in x["content"] for x in rows)
        artifacts=es._runtime_artifacts_for_record(_response_node())
        assert artifacts and artifacts[0]["path"]=="reports/runtime/validation_report.json"
        assert artifacts[0]["size"]>0
    finally:
        es._ACTIVE_RUN_CONTEXT.reset(rt); es._ACTIVE_PLAYBOOK_PACKAGE.reset(pt)
