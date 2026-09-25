from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "integrated_compiler" / "compile_runtime_semantic_plan_v7.py"
SERVICE = ROOT / "editor_service.py"
APP = ROOT / "web" / "app.js"


def _load_compiler():
    spec=importlib.util.spec_from_file_location("ordo_compiler_progress_test", COMPILER)
    mod=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_compiler_progress_side_channel_is_opt_in(tmp_path, monkeypatch):
    mod=_load_compiler()
    target=tmp_path/"progress.jsonl"
    monkeypatch.delenv("ORDO_COMPILER_PROGRESS_FILE", raising=False)
    mod._emit_compile_progress("phase", 42, "Hidden")
    assert not target.exists()
    monkeypatch.setenv("ORDO_COMPILER_PROGRESS_FILE", str(target))
    mod._emit_compile_progress("analyze_elements", 42, "Analyzing", current=4, total=10)
    row=json.loads(target.read_text().strip())
    assert row["phase"]=="analyze_elements"
    assert row["percent"]==42.0
    assert row["current"]==4 and row["total"]==10


def test_editor_forwards_child_progress_and_ui_explains_it():
    service=SERVICE.read_text(encoding="utf-8")
    app=APP.read_text(encoding="utf-8")
    assert 'ORDO_COMPILER_PROGRESS_FILE' in service
    assert 'progress_span=(50, 66)' in service
    assert 'latest_child' in service
    assert 'Compiler phase:' in app
    assert 'activityMeta.phase' in app
    assert 'activityMeta.percent' in app
