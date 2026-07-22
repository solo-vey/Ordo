from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_pathwalk_is_consolidated_under_utilities() -> None:
    assert not (ROOT / "ordo_pathwalk").exists()
    assert (ROOT / "utilities/__init__.py").is_file()
    assert (ROOT / "utilities/ordo_pathwalk/cli.py").is_file()
    assert (ROOT / "utilities/ordo_visual_graph_generator/ordo_graph.py").is_file()


def test_active_utility_entry_points_use_the_canonical_pathwalk_location() -> None:
    required_paths = {
        ".github/workflows/ordo-delivery-gate.yml": "utilities/ordo_pathwalk/requirements.txt",
        "utilities/README.md": "utilities/ordo_pathwalk/",
        "utilities/COMPANION_UTILITY_WORKFLOW.md": "utilities.ordo_pathwalk.cli",
        "repo_hygiene.yml": "path: utilities",
    }
    for path, expected in required_paths.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        assert expected in text, path
        assert "\n      path: ordo_pathwalk\n" not in text, path


def test_pathwalk_module_can_be_imported_from_its_canonical_package() -> None:
    from utilities.ordo_pathwalk import cli

    assert callable(cli.main)
