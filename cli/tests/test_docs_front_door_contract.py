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
    for document in ("README.md", "docs/README.md", "docs/QUICKSTART.md", "cli/README.md"):
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
