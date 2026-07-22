from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "packages" / "ordo_applied_project_factory"


def test_arf_playbook_laws_are_canonical_and_required_for_generated_playbooks() -> None:
    laws = " ".join((PACKAGE / "PLAYBOOK_LAWS.md").read_text(encoding="utf-8").split())
    source = yaml.safe_load((PACKAGE / "source" / "program.ordo.yaml").read_text(encoding="utf-8"))

    contract = source["playbook_laws"]
    assert contract["canonical_artifact"] == "PLAYBOOK_LAWS.md"
    assert contract["applies_to"] == ["arf_master_playbook", "generated_working_playbooks"]
    assert contract["propagation"] == {
        "mode": "required_verbatim_artifact",
        "generated_path": "PLAYBOOK_LAWS.md",
        "release_blocked_when_absent": True,
    }
    assert contract["precedence"][:2] == ["repository_safety_and_platform_constraints", "human_owner_authority"]
    assert len(contract["laws"]) == 4
    for law in contract["laws"]:
        assert " ".join(law["text"].split()) in laws


def test_arf_declares_playbook_laws_as_a_required_artifact() -> None:
    source = yaml.safe_load((PACKAGE / "source" / "program.ordo.yaml").read_text(encoding="utf-8"))
    artifact = next(item for item in source["artifacts"] if item["id"] == "PLAYBOOK_LAWS")

    assert artifact["path_pattern"] == "PLAYBOOK_LAWS.md"
    assert artifact["required"] is True
    assert "generated working playbook" in artifact["description"]
