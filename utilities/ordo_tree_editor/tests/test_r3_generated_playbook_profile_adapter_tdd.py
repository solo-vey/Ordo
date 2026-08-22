from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import yaml

from utilities.ordo_tree_editor import editor_service as es


def _source(tool_ref: str = "tools/run.py"):
    return {
        "graph_contract": {"entry_node": "N_TOOL", "external_terminal_targets": ["OUT_DONE"]},
        "state": {"schema": {"input_value": "seed", "artifact_ref": None}},
        "nodes": [
            {
                "id": "N_TOOL",
                "type": "automatic",
                "action": "PACKAGE.MATERIALIZE",
                "execution_contract": {
                    "owner": "deterministic",
                    "advancement": "automatic",
                    "runtime_executor": "package_tool",
                },
                "tool_ref": tool_ref,
                "args": ["--step", "N_TOOL"],
                "writes": ["artifact_ref"],
                "template": "templates/out.md",
                "bindings": "templates/bindings.yaml",
                "output": "generated/out.md",
                "artifact": {"state_path": "artifact_ref", "expected_path": "generated/out.md"},
                "next": "OUT_DONE",
            }
        ],
        "gates": [],
    }


def _zip_bytes(tmp_path: Path, source: dict, tool_text: str) -> bytes:
    root = tmp_path / "pkg"
    (root / "tools").mkdir(parents=True)
    (root / "templates").mkdir(parents=True)
    (root / "source").mkdir(parents=True)
    (root / "source/program.ordo.yaml").write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
    (root / "templates/out.md").write_text("template", encoding="utf-8")
    (root / "templates/bindings.yaml").write_text("{}\n", encoding="utf-8")
    (root / "tools/run.py").write_text(tool_text, encoding="utf-8")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in root.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(root).as_posix())
    return buf.getvalue()


def test_profile_package_tool_materialization_compiles_to_package_tool(tmp_path):
    raw = _zip_bytes(tmp_path, _source(), 'print("{}")\n')
    parsed = es.parse_playbook_package("profile.zip", raw)
    package = es.PLAYBOOK_PACKAGES[parsed["id"]]
    sem = package["semantic_plan"]["elements"]["N_TOOL"]
    assert sem["execution_traits"]["runtime_executor"] == "package_tool"
    assert sem["execution_traits"]["deterministic"] is True
    assert sem["profile_adapter"]["status"] == "applied"
    assert sem["execution_adapter"]["package_tool"]["tool_ref"] == "tools/run.py"
    assert sem["execution_adapter"]["package_tool"]["args"] == ["--step", "N_TOOL"]
    assert sem["execution_adapter"]["package_tool"]["declared_outputs"] == ["generated/out.md"]


def test_profile_package_tool_runtime_uses_compiled_adapter_and_machine_contract(tmp_path, monkeypatch):
    tool = r'''
import argparse, json, yaml
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--step'); a=p.parse_args()
root=Path(__file__).resolve().parents[1]
state=yaml.safe_load((root/'runtime/state.yaml').read_text()) or {}
(root/'generated').mkdir(exist_ok=True)
(root/'generated/out.md').write_text('VALUE='+str(state.get('input_value')), encoding='utf-8')
print(json.dumps({'status':'PASS','route_key':'next','state_updates':{'artifact_ref':'generated/out.md'}}))
'''
    source = _source()
    raw = _zip_bytes(tmp_path, source, tool)
    parsed = es.parse_playbook_package("profile-run.zip", raw)
    pid = parsed["id"]
    monkeypatch.setattr(es, "_live_credentials", lambda payload: {"provider": "test", "model": "none", "base_url": "local"})
    out = es._call_openai_live({
        "package_id": pid,
        "session_id": "s",
        "run_id": "r",
        "source": source,
        "current_id": "N_TOOL",
        "phase": "enter",
        "state": {"input_value": "abc", "artifact_ref": None},
        "state_revision": 0,
        "history": [],
        "entry_mode": "root",
    })
    assert out["debug"]["runtime"]["runtime_executor"] == "package_tool"
    assert out["route_key"] == "next"
    assert out["next_id"] == "OUT_DONE"
    assert out["state"]["artifact_ref"] == "generated/out.md"
    assert out["debug"]["runtime"]["execution_adapter"]["status"] == "applied"
    ws = es._runtime_workspace(package_id=pid, session_id="s", run_id="r")
    assert (ws / "generated/out.md").read_text(encoding="utf-8") == "VALUE=abc"


def test_profile_package_tool_cannot_write_undeclared_state(tmp_path, monkeypatch):
    tool = "import json; print(json.dumps({'status':'PASS','route_key':'next','state_updates':{'not_allowed':1}}))\n"
    source = _source()
    raw = _zip_bytes(tmp_path, source, tool)
    parsed = es.parse_playbook_package("profile-bad-write.zip", raw)
    pid = parsed["id"]
    monkeypatch.setattr(es, "_live_credentials", lambda payload: {"provider": "test", "model": "none", "base_url": "local"})
    try:
        es._call_openai_live({
            "package_id": pid, "session_id": "s2", "run_id": "r2", "source": source,
            "current_id": "N_TOOL", "phase": "enter", "state": {"input_value": "abc", "artifact_ref": None},
            "state_revision": 0, "history": [], "entry_mode": "root",
        })
    except ValueError as exc:
        assert "unauthorized state_updates" in str(exc)
    else:
        raise AssertionError("unauthorized profile tool state write was accepted")


def test_unsupported_profile_executor_is_blocking_compiler_diagnostic(tmp_path):
    source = _source()
    source["nodes"][0]["execution_contract"]["runtime_executor"] = "mystery_executor"
    raw = _zip_bytes(tmp_path, source, 'print("{}")\n')
    try:
        es.parse_playbook_package("profile-unsupported.zip", raw)
    except Exception as exc:
        text = str(exc)
        assert "PROFILE_RUNTIME_EXECUTOR_UNSUPPORTED" in text or "semantic" in text.lower()
    else:
        package = es.PLAYBOOK_PACKAGE
        issues = ((package.get("semantic_plan_status") or {}).get("compiler") or {}).get("compilation_issues") or []
        assert any(i.get("code") == "PROFILE_RUNTIME_EXECUTOR_UNSUPPORTED" and i.get("severity") == "error" for i in issues)


def test_profile_adapter_does_not_rewrite_source(tmp_path):
    source = _source()
    raw = _zip_bytes(tmp_path, source, 'print("{}")\n')
    parsed = es.parse_playbook_package("profile-source.zip", raw)
    package = es.PLAYBOOK_PACKAGES[parsed["id"]]
    node = package["source"]["nodes"][0]
    assert node["execution_contract"]["runtime_executor"] == "package_tool"
    assert "node_context" not in node
    assert package["semantic_plan"]["elements"]["N_TOOL"]["profile_adapter"]["profile_id"] == "ordo.generated_playbook_profile/v1"
