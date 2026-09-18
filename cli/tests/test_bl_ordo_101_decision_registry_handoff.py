from __future__ import annotations

import json
from pathlib import Path

from ordo.canonical_source import validate_canonical_source
from ordo.decision_handoff import (
    export_cross_chat_handoff,
    restore_cross_chat_handoff,
    validate_decision_registry,
)


def _package(tmp_path: Path) -> Path:
    root = tmp_path / "handoff-package"
    (root / "source").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "README.md").write_text("# Handoff fixture\n", encoding="utf-8")
    (root / "ordo.yml").write_text(
        "name: demo.handoff\nversion: '1.0.0'\nsource: source/program.ordo.yaml\ntests: tests/test_cases.yaml\n",
        encoding="utf-8",
    )
    (root / "source/program.ordo.yaml").write_text(
        """ordo:
  version: '0.12'
  package: demo.handoff
  control_level: standard
  execution_mode: full_runtime
nodes:
  - id: N_START
    question: Confirm the handoff.
gates:
  - id: G_READY
    method: mechanical
    trust_class: deterministic
    condition: state.ready == true
    on_pass: END
terminals:
  - id: END
""",
        encoding="utf-8",
    )
    (root / "tests/test_cases.yaml").write_text("test_cases:\n  - id: TC_HANDOFF\n", encoding="utf-8")
    return root


def _registry(package: Path) -> Path:
    identity = validate_canonical_source(package)["source_identity"]
    payload = {
        "schema_version": "ordo.decision_registry.v1",
        "package_identity": {
            "package": identity["package"],
            "package_version": identity["package_version"],
            "source_sha256": identity["sha256"],
        },
        "decisions": [
            {
                "id": "D_ACCEPT_START",
                "node_id": "N_START",
                "lifecycle_status": "accepted",
                "rationale": "The analyst confirmed the source-bound initial route.",
                "implementing_files": ["source/program.ordo.yaml"],
                "tests": ["TC_HANDOFF"],
            },
            {
                "id": "D_PENDING_REVIEW",
                "node_id": "G_READY",
                "lifecycle_status": "pending",
                "implementing_files": ["source/program.ordo.yaml"],
                "tests": ["TC_HANDOFF"],
            },
        ],
    }
    target = package / "decision_registry.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def _context(package: Path) -> Path:
    target = package / "handoff_context.json"
    target.write_text(
        json.dumps(
            {
                "active_node": "N_START",
                "completed_artifacts": ["A_INPUT_INVENTORY"],
                "open_backlog": ["BL-ORDO-103"],
                "pending_decisions": ["D_PENDING_REVIEW"],
            }
        ),
        encoding="utf-8",
    )
    return target


def test_registry_links_accepted_decisions_to_existing_files_and_tests(tmp_path: Path) -> None:
    package = _package(tmp_path)
    report = validate_decision_registry(package, _registry(package))
    assert report["status"] == "passed", report
    assert report["accepted_decision_ids"] == ["D_ACCEPT_START"]
    assert report["pending_decision_ids"] == ["D_PENDING_REVIEW"]


def test_cross_chat_handoff_round_trip_restores_context_without_mutating_state(tmp_path: Path) -> None:
    package, registry, context = _package(tmp_path), None, None
    registry = _registry(package)
    context = _context(package)
    before = context.read_bytes()
    handoff = package / "handoff.json"
    exported = export_cross_chat_handoff(package, registry_path=registry, state_path=context, out=handoff)
    assert exported["status"] == "ready", exported
    restored = restore_cross_chat_handoff(package, registry_path=registry, handoff_path=handoff)
    assert restored["status"] == "restored", restored
    assert restored["restored_context"] == json.loads(before.decode("utf-8"))
    assert context.read_bytes() == before
    assert restored["replay_performed"] is False
    assert restored["rollback_performed"] is False


def test_stale_or_conflicting_records_are_rejected(tmp_path: Path) -> None:
    package, registry = _package(tmp_path), None
    registry = _registry(package)
    data = json.loads(registry.read_text(encoding="utf-8"))
    data["package_identity"]["source_sha256"] = "stale"
    data["decisions"].append({**data["decisions"][0], "rationale": "Conflicting rationale."})
    registry.write_text(json.dumps(data), encoding="utf-8")
    report = validate_decision_registry(package, registry)
    codes = {item["code"] for item in report["issues"]}
    assert report["status"] == "blocked"
    assert {"DECISION_REGISTRY_STALE", "DECISION_RECORD_CONFLICT"} <= codes


def test_restore_rejects_tampered_or_stale_handoff(tmp_path: Path) -> None:
    package, registry, context = _package(tmp_path), None, None
    registry, context = _registry(package), _context(package)
    handoff = package / "handoff.json"
    assert export_cross_chat_handoff(package, registry_path=registry, state_path=context, out=handoff)["status"] == "ready"
    data = json.loads(handoff.read_text(encoding="utf-8"))
    data["restoration_context"]["active_node"] = "N_NOT_CURRENT"
    handoff.write_text(json.dumps(data), encoding="utf-8")
    report = restore_cross_chat_handoff(package, registry_path=registry, handoff_path=handoff)
    codes = {item["code"] for item in report["issues"]}
    assert report["status"] == "blocked"
    assert {"HANDOFF_DIGEST_MISMATCH", "HANDOFF_ACTIVE_NODE_UNKNOWN"} <= codes
