from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UTILITY = ROOT / "utilities/playbook_lifecycle"


def test_playbook_lifecycle_scripts_are_consolidated_under_utilities() -> None:
    assert not (ROOT / "tools/manage_playbook_checkpoint.py").exists()
    assert not (ROOT / "tools/resolve_playbook_upgrade.py").exists()
    assert not (ROOT / "tools/resolve_upgrade_impact.py").exists()
    assert (UTILITY / "README.md").is_file()
    assert (UTILITY / "__init__.py").is_file()
    assert (UTILITY / "manage_playbook_checkpoint.py").is_file()
    assert (UTILITY / "resolve_playbook_upgrade.py").is_file()
    assert (UTILITY / "resolve_upgrade_impact.py").is_file()


def test_lifecycle_utility_entry_points_are_documented() -> None:
    readme = (UTILITY / "README.md").read_text(encoding="utf-8")
    for script in (
        "manage_playbook_checkpoint.py",
        "resolve_playbook_upgrade.py",
        "resolve_upgrade_impact.py",
    ):
        assert script in readme

    utilities_readme = (ROOT / "utilities/README.md").read_text(encoding="utf-8")
    assert "utilities/playbook_lifecycle/" in utilities_readme
