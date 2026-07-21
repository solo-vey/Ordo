from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLOSURE_PATH = ROOT / "manifests/J6_ROOT_CLEANUP_CLOSURE.json"


def load_json(path: str | Path) -> dict:
    target = path if isinstance(path, Path) else ROOT / path
    return json.loads(target.read_text(encoding="utf-8"))


def test_j6_closure_records_every_phase_and_merge() -> None:
    closure = load_json(CLOSURE_PATH)
    phases = closure["phases"]

    assert closure["schema_version"] == "ordo.repository_root_cleanup_closure.v1"
    assert closure["contour_id"] == "J.6"
    assert closure["status"] == "closed"
    assert closure["validated_main_baseline"] == "42fdf1e9b439e3d0c4c0109f8ca8061d657ee663"
    assert [phase["id"] for phase in phases] == [
        "J.6a",
        "J.6b-1",
        "J.6b-2a",
        "J.6b-2b",
        "J.6b-2c",
        "J.6b-2d",
        "J.6b-2e",
        "J.6b-3",
        "J.6b-4",
        "J.6c",
    ]
    assert all(phase["status"] == "closed" for phase in phases)
    assert [phase["pull_request"] for phase in phases[1:]] == list(range(10, 19))
    assert len({phase["merge_commit"] for phase in phases[1:]}) == 9


def test_j6_closure_root_allowlist_matches_repository() -> None:
    closure = load_json(CLOSURE_PATH)
    actual = sorted(path.name for path in ROOT.iterdir() if path.is_file())

    assert closure["root_file_count"] == len(closure["root_allowed_files"]) == 15
    assert actual == sorted(closure["root_allowed_files"])
    assert closure["historical_contours_rewritten"] is False


def test_j6_status_is_synchronized_across_backlog_and_maturity_state() -> None:
    backlog_json = load_json("manifests/CONSOLIDATED_BACKLOG.json")
    maturity_json = load_json("manifests/CURRENT_MATURITY_STATE.json")
    backlog_md = (ROOT / "backlog/CONSOLIDATED_BACKLOG.md").read_text(encoding="utf-8")
    maturity_md = (ROOT / "backlog/CURRENT_MATURITY_STATE.md").read_text(encoding="utf-8")

    contour = next(item for item in backlog_json["maintenance_contours"] if item["id"] == "J.6")
    assert contour["status"] == "closed"
    assert contour["closure_evidence"] == "manifests/J6_ROOT_CLEANUP_CLOSURE.json"
    assert maturity_json["repository_maintenance"]["J.6"]["status"] == "closed"
    assert "### J.6 — Repository root structure audit and cleanup\n\nStatus: `closed`" in backlog_md
    assert "Repository maintenance contour J.6: `closed`" in maturity_md


def test_j6_closure_documents_point_to_machine_evidence() -> None:
    status_doc = (ROOT / "docs/status/J6_REPOSITORY_ROOT_CLEANUP_CLOSURE.md").read_text(encoding="utf-8")
    relocation_doc = (ROOT / "docs/REPOSITORY_ROOT_RELOCATION_CONTRACT.md").read_text(encoding="utf-8")

    assert "../../manifests/J6_ROOT_CLEANUP_CLOSURE.json" in status_doc
    assert "../manifests/J6_ROOT_CLEANUP_CLOSURE.json" in relocation_doc
