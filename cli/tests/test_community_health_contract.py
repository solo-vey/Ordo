from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = (
    "SECURITY.md",
    "SUPPORT.md",
    "GOVERNANCE.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/docs_issue.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/pull_request_template.md",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def assert_relative_links_exist(document: str) -> None:
    path = ROOT / document
    for target in markdown_links(read(document)):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        relative = target.split("#", 1)[0]
        if not relative:
            continue
        assert (path.parent / relative).resolve().exists(), (
            f"{document} has a missing link target: {target}"
        )


def test_required_community_health_files_exist() -> None:
    for path in REQUIRED_FILES:
        assert (ROOT / path).is_file(), path


def test_security_policy_uses_private_reporting_without_fake_email() -> None:
    text = read("SECURITY.md")
    assert "GitHub private vulnerability reporting" in text
    assert "Do not disclose" in text
    assert "Current `main`" in text
    assert "@" not in text


def test_code_of_conduct_has_real_private_route_and_no_draft_placeholder() -> None:
    text = read("CODE_OF_CONDUCT.md")
    assert "GitHub private vulnerability reporting" in text
    assert "Conduct concern:" in text
    assert "replace this draft instruction" not in text


def test_support_routes_separate_public_and_private_reports() -> None:
    text = read("SUPPORT.md")
    assert "Security vulnerabilities" in text
    assert "Bugs" in text
    assert "Documentation problems" in text
    assert "Feature proposals" in text
    assert "Conduct concerns" in text
    assert "Do not create a public issue" in text


def test_governance_declares_final_authority_and_elevated_review() -> None:
    text = read("GOVERNANCE.md")
    assert "maintainer-led governance model" in text
    assert "repository owner is the final decision authority" in text
    assert "Elevated-review changes" in text
    assert "Governance changes" in text


def test_issue_forms_and_config_are_valid_yaml() -> None:
    paths = (
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/docs_issue.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
    )
    for path in paths:
        data = yaml.safe_load(read(path))
        assert isinstance(data, dict), path
    config = yaml.safe_load(read(paths[0]))
    assert config["blank_issues_enabled"] is False
    urls = [item["url"] for item in config["contact_links"]]
    assert "https://github.com/solo-vey/Ordo/security/advisories/new" in urls


def test_issue_forms_redirect_security_and_require_sanitization() -> None:
    bug = read(".github/ISSUE_TEMPLATE/bug_report.yml")
    assert "private vulnerability reporting" in bug
    assert "This is not a security vulnerability." in bug
    assert "I removed secrets and sensitive data." in bug


def test_pull_request_template_covers_required_contract() -> None:
    text = read(".github/pull_request_template.md")
    for heading in (
        "## Summary",
        "## Changed artifacts",
        "## Validation",
        "## Version impact",
        "## Security, privacy, and evidence impact",
        "## Migration and rollback",
        "## Release and checksum impact",
    ):
        assert heading in text


def test_front_door_documents_link_to_community_health_files() -> None:
    readme = read("README.md")
    docs = read("docs/README.md")
    for target in ("SECURITY.md", "SUPPORT.md", "GOVERNANCE.md", "CODE_OF_CONDUCT.md"):
        assert target in readme
        assert f"../{target}" in docs


def test_relative_links_exist_in_changed_markdown() -> None:
    for document in (
        "README.md",
        "docs/README.md",
        "SECURITY.md",
        "SUPPORT.md",
        "GOVERNANCE.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
    ):
        assert_relative_links_exist(document)
