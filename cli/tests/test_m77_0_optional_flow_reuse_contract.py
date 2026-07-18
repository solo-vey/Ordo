from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(rel):
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def test_flow_join_schema_is_optional_and_requires_two_inputs():
    schema = load("language/schemas/flow_join_schema.yaml")["FLOW.JOIN"]
    assert schema["properties"]["incoming"]["minItems"] == 2
    assert schema["properties"]["maturity"]["default"] == "experimental_optional"
    assert "target" in schema["required"]


def test_shared_tail_reference_preserves_provenance():
    schema = load("language/schemas/shared_tail_reference_schema.yaml")["SHARED.TAIL.REFERENCE"]
    assert schema["properties"]["preserve_provenance"]["default"] is True
    assert set(schema["properties"]["namespace_policy"]["enum"]) == {"inherit", "qualified", "explicit_map"}


def test_spec_keeps_explicit_duplication_valid_and_forbids_auto_rewrite():
    text = (ROOT / "language/spec/34_OPTIONAL_FLOW_REUSE_MODEL.md").read_text(encoding="utf-8")
    assert "optional authoring optimizations" in text
    assert "MUST NOT fail compilation solely" in text
    assert "Automatic extraction, replacement, or mutation" in text


def test_example_contains_join_and_reference():
    example = load("language/examples/source/optional_flow_reuse_example.ordo.yaml")
    assert len(example["flow_reuse"]["joins"][0]["incoming"]) == 2
    assert example["flow_reuse"]["references"][0]["tail_id"] == "TAIL.PACKAGE.CLOSE"
