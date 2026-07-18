import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "ordo_graph.py"


def load_module():
    import sys

    spec = importlib.util.spec_from_file_location("ordo_graph", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_yaml(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "module.ordo.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def run_cli(input_path: Path, *args: str):
    return subprocess.run(
        ["python3", str(SCRIPT), str(input_path), *args],
        capture_output=True,
        text=True,
    )


def test_question_text_branch_labels_are_used(tmp_path):
    module = load_module()
    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: Branch Label Test
nodes:
  - id: N1
    question: |
      Choose path.
      A — Alpha route
      B — Beta route
    answer_type: enum
    allowed_answers: [A, B]
    on_answer:
      A:
        next: STOP_ALPHA
      B:
        next: STOP_BETA
""",
    )

    data = module.load_yaml(yaml_path)
    graph = module.build_graph(data, yaml_path, artifact_mode="terminal")

    labels = [edge.label for edge in graph.edges]
    assert "A — Alpha route" in labels
    assert "B — Beta route" in labels
    assert not graph.has_errors


def test_update_state_label_fallback_is_used(tmp_path):
    module = load_module()
    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: Update State Label Test
nodes:
  - id: N1
    question: Pick one.
    answer_type: enum
    allowed_answers: [A]
    on_answer:
      A:
        update_state:
          selected_path_label: Human readable route
        next: STOP_DONE
""",
    )

    data = module.load_yaml(yaml_path)
    graph = module.build_graph(data, yaml_path, artifact_mode="terminal")

    assert any(edge.label == "A — Human readable route" for edge in graph.edges)
    assert not graph.has_errors


def test_test_coverage_level_fallback_is_used(tmp_path):
    module = load_module()
    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: Coverage Label Test
nodes:
  - id: N1
    question: Pick coverage.
    answer_type: enum
    allowed_answers: ['1']
    on_answer:
      '1':
        update_state:
          test_coverage_level: Manual + Functional
        next: STOP_DONE
""",
    )

    data = module.load_yaml(yaml_path)
    graph = module.build_graph(data, yaml_path, artifact_mode="terminal")

    assert any(edge.label == "1 — Manual + Functional" for edge in graph.edges)
    assert not graph.has_errors


def test_free_text_transition_has_no_noisy_answer_label(tmp_path):
    module = load_module()
    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: Free Text Test
nodes:
  - id: N1
    question: Describe the issue.
    answer_type: free_text
    on_answer:
      update_state:
        issue: $answer
      next: N2
  - id: N2
    question: Done.
    answer_type: free_text
    on_answer:
      update_state:
        done: true
      next: STOP_DONE
""",
    )

    data = module.load_yaml(yaml_path)
    graph = module.build_graph(data, yaml_path, artifact_mode="terminal")

    n1_edges = [edge for edge in graph.edges if edge.source == "N1"]
    assert len(n1_edges) == 1
    assert n1_edges[0].label is None
    assert not graph.has_errors


def test_unknown_target_blocks_generation(tmp_path):
    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: Broken Test
nodes:
  - id: N1
    question: Pick.
    answer_type: enum
    allowed_answers: [A]
    on_answer:
      A:
        next: N_MISSING
""",
    )

    out = tmp_path / "broken.mmd"
    result = run_cli(yaml_path, "--format", "mmd", "--out", str(out))

    assert result.returncode == 1
    assert "UNKNOWN_TARGET" in result.stdout
    assert "Graph generation blocked" in result.stderr
    assert not out.exists()


def test_gate_target_is_valid(tmp_path):
    module = load_module()
    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: Gate Target Test
nodes:
  - id: N1
    question: Approve?
    answer_type: enum
    allowed_answers: [yes]
    on_answer:
      yes:
        next: G_APPROVED
gates:
  - id: G_APPROVED
    method: human
    condition: approval received
    on_fail: block
""",
    )

    data = module.load_yaml(yaml_path)
    graph = module.build_graph(data, yaml_path, artifact_mode="terminal")

    assert "G_APPROVED" in graph.nodes
    assert any(edge.target == "G_APPROVED" for edge in graph.edges)
    assert not graph.has_errors


def test_terminal_artifacts_are_extracted_from_question_bullets(tmp_path):
    module = load_module()
    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: Artifact Extraction Test
nodes:
  - id: N1
    question: |
      Approve package?
      - 01_DOC_<ALIAS>.md
      - 02_REPORT_<ALIAS>.json
    answer_type: enum
    allowed_answers: [yes]
    on_answer:
      yes:
        next: STOP_APPROVED
""",
    )

    data = module.load_yaml(yaml_path)
    graph = module.build_graph(data, yaml_path, artifact_mode="terminal")

    artifact_labels = [node.label for node in graph.nodes.values() if node.type == "artifact"]
    assert any("01_DOC_<ALIAS>.md" in label for label in artifact_labels)
    assert any("02_REPORT_<ALIAS>.json" in label for label in artifact_labels)
    assert not graph.has_errors


def test_artifact_mode_none_suppresses_artifacts(tmp_path):
    module = load_module()
    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: Artifact None Test
nodes:
  - id: N1
    question: |
      Approve package?
      - 01_DOC_<ALIAS>.md
    answer_type: enum
    allowed_answers: [yes]
    on_answer:
      yes:
        next: STOP_APPROVED
""",
    )

    data = module.load_yaml(yaml_path)
    graph = module.build_graph(data, yaml_path, artifact_mode="none")

    assert not any(node.type == "artifact" for node in graph.nodes.values())
    assert not graph.has_errors


def test_artifact_mode_package_renders_outputs_as_package_nodes(tmp_path):
    module = load_module()
    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: Package Mode Test
nodes:
  - id: N1
    question: Finish?
    answer_type: enum
    allowed_answers: [yes]
    on_answer:
      yes:
        next: STOP_DONE
outputs:
  - id: OUT_PACKAGE
    type: archive
""",
    )

    data = module.load_yaml(yaml_path)
    graph = module.build_graph(data, yaml_path, artifact_mode="package")

    assert "output_OUT_PACKAGE" in graph.nodes
    assert graph.nodes["output_OUT_PACKAGE"].type == "output"
    assert not graph.has_errors


def test_subtree_focus_excludes_sibling_branch(tmp_path):
    module = load_module()
    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: Focus Test
nodes:
  - id: N1
    question: Pick.
    answer_type: enum
    allowed_answers: [A, B]
    on_answer:
      A:
        next: N2_A
      B:
        next: N2_B
  - id: N2_A
    question: A branch.
    answer_type: free_text
    on_answer:
      update_state:
        a: $answer
      next: STOP_A
  - id: N2_B
    question: B branch.
    answer_type: free_text
    on_answer:
      update_state:
        b: $answer
      next: STOP_B
""",
    )

    data = module.load_yaml(yaml_path)
    graph = module.build_graph(data, yaml_path, artifact_mode="terminal")
    focused = module.focus_graph(graph, start="N2_A", focus=None, mode="subtree", depth=None)

    assert "N2_A" in focused.nodes
    assert "terminal_STOP_A" in focused.nodes
    assert "N2_B" not in focused.nodes
    assert "terminal_STOP_B" not in focused.nodes


def test_context_focus_includes_path_and_descendants(tmp_path):
    module = load_module()
    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: Context Test
nodes:
  - id: N1
    question: Pick.
    answer_type: enum
    allowed_answers: [A, B]
    on_answer:
      A:
        next: N2_A
      B:
        next: N2_B
  - id: N2_A
    question: A branch.
    answer_type: free_text
    on_answer:
      update_state:
        a: $answer
      next: N3_A
  - id: N3_A
    question: A detail.
    answer_type: enum
    allowed_answers: [yes]
    on_answer:
      yes:
        next: STOP_A
  - id: N2_B
    question: B branch.
    answer_type: free_text
    on_answer:
      update_state:
        b: $answer
      next: STOP_B
""",
    )

    data = module.load_yaml(yaml_path)
    graph = module.build_graph(data, yaml_path, artifact_mode="terminal")
    focused = module.focus_graph(graph, start=None, focus="N3_A", mode="context", depth=None)

    assert "N1" in focused.nodes
    assert "N2_A" in focused.nodes
    assert "N3_A" in focused.nodes
    assert "terminal_STOP_A" in focused.nodes
    assert "N2_B" not in focused.nodes


def test_svg_generation_has_real_line_breaks_when_graphviz_available(tmp_path):
    if shutil.which("dot") is None:
        pytest.skip("Graphviz dot is not installed")

    yaml_path = write_yaml(
        tmp_path,
        """
agent:
  name: SVG Test
nodes:
  - id: N1
    question: Pick.
    answer_type: enum
    allowed_answers: [A]
    on_answer:
      A:
        next: STOP_DONE
""",
    )
    out = tmp_path / "graph.svg"

    result = run_cli(yaml_path, "--format", "svg", "--out", str(out))

    assert result.returncode == 0
    svg = out.read_text(encoding="utf-8")
    assert ">ENTRY\\n" not in svg
    assert ">N1\\n" not in svg
