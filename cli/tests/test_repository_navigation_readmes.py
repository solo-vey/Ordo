from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
README_PATHS = {
    "benchmarks/README.md",
    "benchmarks/ab/README.md",
    "benchmarks/datasets/README.md",
    "benchmarks/examples/README.md",
    "benchmarks/schemas/README.md",
    "benchmarks/taxonomy/README.md",
    "examples/README.md",
    "examples/template_tooling/README.md",
    "integrations/README.md",
    "integrations/apf/README.md",
    "manifests/README.md",
    "manifests/external_archives/README.md",
    "packages/README.md",
    "packages/benchmark_creation_playbook/README.md",
    "policies/README.md",
    "reports/README.md",
    "tools/README.md",
    "tools/evidence_storage/README.md",
    "empirical_evidence/benchmarks/README.md",
    "empirical_evidence/cases/README.md",
    "empirical_evidence/governance/README.md",
}


def test_navigation_readmes_exist_and_link_to_a_related_entry_point() -> None:
    for relative_path in README_PATHS:
        readme = ROOT / relative_path
        assert readme.is_file(), relative_path
        assert "](" in readme.read_text(encoding="utf-8"), relative_path


def test_repository_front_doors_link_to_navigation_indexes() -> None:
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs_readme = (ROOT / "docs/README.md").read_text(encoding="utf-8")
    for path in ("benchmarks/README.md", "integrations/README.md", "packages/README.md", "manifests/README.md"):
        assert path in root_readme or f"../{path}" in docs_readme
