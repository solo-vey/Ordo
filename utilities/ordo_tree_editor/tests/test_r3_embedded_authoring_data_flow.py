from utilities.ordo_tree_editor import editor_service as es


def _package():
    return {
        "resources": {
            "design/dataflow_bundle.yaml": """
schema_version: '1.0'
model_bundle_id: demo_authoring_flow
canonical_sources:
  graph: models/flow.yaml
  variable_catalog: models/variables.yaml
  variable_group_catalog: models/groups.yaml
  artifact_catalog: models/artifacts.yaml
""",
            "design/models/flow.yaml": """
schema_version: '1.0'
model_id: demo_flow
revision: r1
sections:
  - {id: intake, label: A. Intake, order: 1}
  - {id: output, label: B. Output, order: 2}
nodes:
  - {id: raw, label: RAW, type: analyst_input, section: intake}
  - {id: value_a, label: value_a, type: variable, section: intake, variable_ref: value_a}
  - {id: artifact_a, label: report.md, type: artifact, section: output, artifact_ref: ART01}
gates:
  - {id: G1, label: Validate value, fragments: [g1], checks: [value_a]}
edges:
  - {from: raw, to: value_a, type: derivation}
  - {from: value_a, to: artifact_a, type: artifact_input}
terminal: {final_package_node: artifact_a}
""",
            "design/models/variables.yaml": """
schema_version: '1.0'
variables:
  - id: value_a
    definition_status: approved
    group_id: GRP1
    provenance_required: true
""",
            "design/models/groups.yaml": """
schema_version: '1.0'
groups:
  - id: GRP1
    label: Demo group
    order: 1
    member_variables: [value_a]
""",
            "design/models/artifacts.yaml": """
schema_version: '1.0'
artifacts:
  - id: ART01
    label: Report
    media_type: text/markdown
""",
        }
    }


def test_embedded_authoring_data_flow_is_discovered_by_contract_not_filename():
    result = es._discover_embedded_authoring_data_flow(_package())
    assert result["available"] is True
    assert result["bundle"]["path"] == "design/dataflow_bundle.yaml"
    assert result["graph"]["model_id"] == "demo_flow"
    assert result["summary"]["nodes"] == 3
    assert result["summary"]["edges"] == 2
    by_id = {row["id"]: row for row in result["graph"]["nodes"]}
    assert by_id["value_a"]["variable_metadata"]["group_id"] == "GRP1"
    assert by_id["value_a"]["group_metadata"]["label"] == "Demo group"
    assert by_id["artifact_a"]["artifact_metadata"]["media_type"] == "text/markdown"


def test_embedded_authoring_data_flow_is_optional():
    result = es._discover_embedded_authoring_data_flow({"resources": {"docs/readme.yaml": "x: 1\n"}})
    assert result["available"] is False
    assert result["status"] == "not_present"


def test_candidate_bundle_with_missing_graph_is_reported_not_silently_accepted():
    package = {"resources": {"design/model.yaml": "canonical_sources:\n  graph: missing/graph.yaml\n"}}
    result = es._discover_embedded_authoring_data_flow(package)
    assert result["available"] is False
    assert result["status"] == "invalid"
    assert "graph" in result["error"].lower()


def test_embedded_authoring_model_does_not_become_execution_semantics():
    package = _package()
    source = {"entry_node": "N1", "nodes": [{"id": "N1", "next": "END"}], "gates": []}
    baseline = es._build_data_lineage({"resources": {}}, source, {})
    with_design = es._build_data_lineage(package, source, {})
    assert baseline["nodes"] == with_design["nodes"]
    assert baseline["edges"] == with_design["edges"]
