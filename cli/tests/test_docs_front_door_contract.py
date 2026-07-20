from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def assert_relative_links_exist(document: str) -> None:
    path = ROOT / document
    for target in markdown_links(path.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        relative = target.split("#", 1)[0]
        if not relative:
            continue
        resolved = (path.parent / relative).resolve()
        assert resolved.exists(), f"{document} has a missing link target: {target}"


def test_front_door_files_and_links_exist() -> None:
    for document in (
        "README.md",
        "docs/README.md",
        "docs/QUICKSTART.md",
        "docs/FAQ.md",
        "docs/GLOSSARY.md",
        "cli/README.md",
    ):
        assert (ROOT / document).is_file()
        assert_relative_links_exist(document)


def test_root_readme_prioritizes_quickstart_and_docs() -> None:
    text = read("README.md")
    assert text.index("## Quickstart") < text.index("## What is included")
    assert "docs/README.md" in text
    assert "Latest canonical packaged baseline" in text
    assert "The `main` branch may contain" in text


def test_quickstart_has_python_preflight_and_expected_result() -> None:
    text = read("docs/QUICKSTART.md")
    assert "python3 --version" in text
    assert "Python 3.10 or newer is required" in text
    assert "## Expected result" in text
    assert "python tools/run_golden_examples.py --all" in text


def test_cli_examples_are_repository_root_relative() -> None:
    text = read("cli/README.md")
    assert "../packages/" not in text
    assert "ordo repo-check .." not in text
    assert "python scripts/run_full_suite_partitioned.py" not in text
    assert "python cli/scripts/run_full_suite_partitioned.py" in text
    assert "packages/history_event_guided_intake" in text


def test_user_facing_cli_headings_do_not_use_milestone_ids() -> None:
    headings = [
        line for line in read("cli/README.md").splitlines()
        if line.startswith("#")
    ]
    assert not any(re.search(r"\bM\d+(?:\.\d+)*\b", heading) for heading in headings)

def test_discoverability_entry_points_are_canonical_and_linked() -> None:
    root_readme = read("README.md")
    docs_readme = read("docs/README.md")
    for target in ("docs/FAQ.md", "docs/GLOSSARY.md", "CITATION.cff"):
        assert target in root_readme
    for target in ("FAQ.md", "GLOSSARY.md", "../CITATION.cff"):
        assert target in docs_readme


def test_faq_covers_project_identity_license_and_support_routes() -> None:
    text = read("docs/FAQ.md")
    required_headings = (
        "## What is Ordo?",
        "## Is Ordo a programming language, workflow format, or prompt framework?",
        "## Is Ordo open source?",
        "## Where should I report a bug or propose a change?",
    )
    for heading in required_headings:
        assert heading in text
    assert "PolyForm Noncommercial License 1.0.0" in text
    assert "../SUPPORT.md" in text
    assert "../SECURITY.md" in text


def test_glossary_contains_controlled_core_terms() -> None:
    text = read("docs/GLOSSARY.md")
    for term in (
        "## APF",
        "## Evidence",
        "## Execution graph",
        "## Gate",
        "## Ordo language",
        "## Package",
        "## Playbook",
        "## Replay",
        "## Runtime framework",
    ):
        assert term in text


def test_citation_metadata_has_required_repository_fields() -> None:
    text = read("CITATION.cff")
    for marker in (
        "cff-version: 1.2.0",
        'title: "Ordo: AI Process Language and Applied Runtime Framework"',
        "type: software",
        'repository-code: "https://github.com/solo-vey/Ordo"',
        'license: "PolyForm-Noncommercial-1.0.0"',
    ):
        assert marker in text


def test_quickstart_uses_search_oriented_scenario_headings() -> None:
    text = read("docs/QUICKSTART.md")
    for heading in (
        "## Validate an Ordo package",
        "## Find the next Process Rail step",
        "## Validate an end-to-end output gate",
        "## Run every CI-backed example",
    ):
        assert heading in text
