from __future__ import annotations

import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import editor_service as es

SOURCE = b"""playbook:
  id: runtime-plan-authority-fixture
  version: 0.1.0
graph_contract:
  entry_node: N_COLLECT_TITLE
  external_terminal_targets: [END_DONE]
state:
  schema:
    title: string
nodes:
  - id: N_COLLECT_TITLE
    question: \"Provide a title.\"
    answer_type: text
    on_answer:
      update_state:
        title: $answer
      next: G_TITLE_PRESENT
  - id: N_CONFIRM
    question: \"Confirm completion.\"
    answer_type: confirmation
    on_answer:
      confirmed:
        next: END_DONE
gates:
  - id: G_TITLE_PRESENT
    trust_class: deterministic
    method: mechanical
    required_inputs: [title]
    on_pass: N_CONFIRM
    on_fail: N_COLLECT_TITLE
"""

NESTED_SOURCE = SOURCE.replace(b"runtime-plan-authority-fixture", b"nested-synthetic-fixture")


def _valid_plan(source: bytes = SOURCE) -> bytes:
    plan = {
        "format": "ordo.runtime_semantic_plan",
        "format_version": "1.0",
        "source": {"sha256": hashlib.sha256(source).hexdigest()},
        "elements": {},
        "validation": {
            "structural_status": "PASS",
            "semantic_status": "PASS",
            "compilation_issues": [],
        },
    }
    return json.dumps(plan, separators=(",", ":")).encode("utf-8")


def _invalid_plan() -> bytes:
    return json.dumps({"format": "fixture.not_a_runtime_plan", "format_version": "999"}).encode("utf-8")


def _zip(files: list[tuple[str, bytes]]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, raw in files:
            zf.writestr(name, raw)
    return buf.getvalue()


def test_red1_nested_compiled_fixture_does_not_claim_runtime_plan_authority():
    raw = _zip([
        ("program.ordo.yaml", SOURCE),
        ("tests/generated_playbook_regressions/fixtures/bad_source_only_package/compiled/runtime_semantic_plan.json", _invalid_plan()),
    ])
    parsed = es.parse_playbook_package("nested-fixture.zip", raw)
    status = parsed["semantic_plan_status"]
    assert status["valid"] is True
    assert status["generated"] is True
    assert status["reason"] == "integrated_compile_ok"
    assert parsed["ignored_non_authoritative_runtime_plan_named_resources"] == [
        "tests/generated_playbook_regressions/fixtures/bad_source_only_package/compiled/runtime_semantic_plan.json"
    ]


def test_red2_canonical_invalid_runtime_plan_remains_fail_closed():
    raw = _zip([
        ("program.ordo.yaml", SOURCE),
        ("compiled/runtime_semantic_plan.json", _invalid_plan()),
    ])
    try:
        es.parse_playbook_package("canonical-invalid.zip", raw)
    except ValueError as exc:
        text = str(exc)
        assert "unsupported_format" in text
        assert "compiled/runtime_semantic_plan.json" in text
        assert "canonical_package_path" in text
    else:
        raise AssertionError("authoritative invalid runtime plan must fail closed")


def test_red3_canonical_valid_runtime_plan_wins_over_nested_invalid_fixture():
    raw = _zip([
        ("program.ordo.yaml", SOURCE),
        ("compiled/runtime_semantic_plan.json", _valid_plan()),
        ("tests/regression/compiled/runtime_semantic_plan.json", _invalid_plan()),
    ])
    parsed = es.parse_playbook_package("canonical-wins.zip", raw)
    status = parsed["semantic_plan_status"]
    assert status["valid"] is True
    assert status.get("generated") is not True
    assert status["path"] == "compiled/runtime_semantic_plan.json"
    assert status["authority"] == "canonical_package_path"
    assert parsed["ignored_non_authoritative_runtime_plan_named_resources"] == [
        "tests/regression/compiled/runtime_semantic_plan.json"
    ]


def test_red4_single_enclosing_root_prefixed_canonical_plan_is_authoritative():
    raw = _zip([
        ("MY_PACKAGE/program.ordo.yaml", SOURCE),
        ("MY_PACKAGE/compiled/runtime_semantic_plan.json", _valid_plan()),
        ("MY_PACKAGE/tests/bad/compiled/runtime_semantic_plan.json", _invalid_plan()),
    ])
    parsed = es.parse_playbook_package("root-prefixed.zip", raw)
    status = parsed["semantic_plan_status"]
    assert status["valid"] is True
    assert status["path"] == "MY_PACKAGE/compiled/runtime_semantic_plan.json"
    assert status["authority"] == "package_root_canonical_path"
    assert parsed["ignored_non_authoritative_runtime_plan_named_resources"] == [
        "MY_PACKAGE/tests/bad/compiled/runtime_semantic_plan.json"
    ]


def test_red5_no_authoritative_compiled_plan_uses_source_first_even_with_named_resources():
    raw = _zip([
        ("program.ordo.yaml", SOURCE),
        ("docs/runtime_semantic_plan.json", _invalid_plan()),
        ("evidence/runtime_semantic_plan.json", _invalid_plan()),
        ("tests/runtime_semantic_plan.json", _invalid_plan()),
    ])
    parsed = es.parse_playbook_package("source-first.zip", raw)
    assert parsed["semantic_plan_status"]["reason"] == "integrated_compile_ok"
    assert parsed["semantic_plan_status"]["generated"] is True
    assert parsed["ignored_non_authoritative_runtime_plan_named_resources"] == [
        "docs/runtime_semantic_plan.json",
        "evidence/runtime_semantic_plan.json",
        "tests/runtime_semantic_plan.json",
    ]


def test_red6_multiple_candidate_package_roots_fail_with_explicit_authority_ambiguity():
    raw = _zip([
        ("PACKAGE_A/program.ordo.yaml", SOURCE),
        ("PACKAGE_A/compiled/runtime_semantic_plan.json", _valid_plan()),
        ("PACKAGE_B/program.ordo.yaml", NESTED_SOURCE),
        ("PACKAGE_B/compiled/runtime_semantic_plan.json", _valid_plan(NESTED_SOURCE)),
    ])
    try:
        es.parse_playbook_package("ambiguous-roots.zip", raw)
    except ValueError as exc:
        text = str(exc)
        assert "ambiguous_authoritative_runtime_plans" in text
        assert "PACKAGE_A/compiled/runtime_semantic_plan.json" in text
        assert "PACKAGE_B/compiled/runtime_semantic_plan.json" in text
    else:
        raise AssertionError("malformed multi-root package must fail with explicit authority ambiguity")


def test_red7_same_basename_outside_canonical_compiled_location_is_ordinary_resource():
    raw = _zip([
        ("program.ordo.yaml", SOURCE),
        ("developer/evidence/runtime_semantic_plan.json", _invalid_plan()),
    ])
    parsed = es.parse_playbook_package("basename-resource.zip", raw)
    assert parsed["semantic_plan_status"]["generated"] is True
    assert parsed["ignored_non_authoritative_runtime_plan_named_resources"] == [
        "developer/evidence/runtime_semantic_plan.json"
    ]


def test_red8_nested_synthetic_package_does_not_shadow_root_source_first_package():
    raw = _zip([
        ("program.ordo.yaml", SOURCE),
        ("tests/fixture_package/program.ordo.yaml", NESTED_SOURCE),
        ("tests/fixture_package/compiled/runtime_semantic_plan.json", _invalid_plan()),
    ])
    parsed = es.parse_playbook_package("nested-package.zip", raw)
    assert parsed["source_name"] == "program.ordo.yaml"
    assert parsed["source"]["playbook"]["id"] == "runtime-plan-authority-fixture"
    assert parsed["semantic_plan_status"]["generated"] is True
