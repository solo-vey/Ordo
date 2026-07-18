from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(rel):
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def test_join_requires_explicit_namespace_and_structured_endpoints():
    schema = load("language/schemas/flow_join_schema.yaml")["FLOW.JOIN"]
    assert "namespace" in schema["required"]
    incoming = schema["properties"]["incoming"]["items"]
    assert set(incoming["required"]) == {"node", "namespace"}
    assert set(schema["properties"]["target"]["required"]) == {"node", "namespace"}


def test_join_state_contract_separates_protected_and_branch_local_fields():
    schema = load("language/schemas/flow_join_schema.yaml")["FLOW.JOIN"]
    req = set(schema["properties"]["state_contract"]["required"])
    assert req == {"required_fields", "protected_fields", "optional_fields"}
    props = schema["properties"]["state_contract"]["properties"]
    assert "branch_local_fields" in props


def test_merge_rules_are_explicit_and_fail_closed():
    schema = load("language/schemas/flow_join_schema.yaml")["FLOW.JOIN"]
    defaults = set(schema["properties"]["merge_policy"]["properties"]["default"]["enum"])
    assert defaults == {"require_equal", "prefer_non_null", "reject"}
    rules = set(schema["properties"]["merge_policy"]["properties"]["fields"]["additionalProperties"]["enum"])
    assert "explicit_resolver" in rules
    assert "last_write_wins" not in rules
    assert set(schema["properties"]["conflict_policy"]["enum"]) == {"reject", "explicit_resolver"}


def test_reference_has_explicit_import_export_contracts():
    schema = load("language/schemas/shared_tail_reference_schema.yaml")["SHARED.TAIL.REFERENCE"]
    assert "namespace" in schema["required"]
    props = schema["properties"]
    assert "import_state" in props and "export_state" in props
    assert "protected_fields" in props


def test_spec_forbids_implicit_resolution_and_protected_override():
    text = (ROOT / "language/spec/34_OPTIONAL_FLOW_REUSE_MODEL.md").read_text(encoding="utf-8")
    assert "No implicit last-write-wins" in text
    assert "Protected-field conflicts always reject" in text
    assert "Namespaces MUST NOT be guessed" in text


def test_example_uses_namespace_and_resolver_contract():
    example = load("language/examples/source/optional_flow_reuse_example.ordo.yaml")
    join = example["flow_reuse"]["joins"][0]
    ref = example["flow_reuse"]["references"][0]
    assert join["namespace"] == "package.review"
    assert join["resolver_ref"] == "RESOLVER.REVIEW.OUTCOME"
    assert ref["namespace_policy"] == "explicit_map"
    assert ref["import_state"]["required"] == ["package_id", "review_status"]
