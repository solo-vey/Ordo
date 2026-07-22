from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from utilities.ordo_pathwalk.generator.real_module import summarize_real_module_source, write_real_module_graph_summary


def _write_sample_source(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """
ordo:
  version: '0.12'
  package: sample.real_module
  control_level: standard
  execution_mode: chat_internal
nodes:
  - id: N_START
    question: Start?
    answer_type: enum
    allowed_answers: [A, B]
    on_answer:
      A:
        update_state:
          selected: A
        next: N_A
      B:
        update_state:
          selected: B
        next: STOP_B
    on_unmatched_input:
      action: CLARIFY.REQUEST
      strategy: show_allowed_answers
      max_attempts: 2
      on_exhausted:
        action: escalate_to_human
        reason: no match
  - id: N_A
    question: Explain A
    answer_type: free_text
    on_answer:
      update_state:
        note: $answer
      next: G_DONE
gates:
  - id: G_DONE
    method: mechanical
    trust_class: deterministic
    condition: state.note is not null
    on_fail: block
outputs:
  - id: OUT_PACKAGE
    type: archive
    allowed_after: [G_DONE]
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_summarize_real_module_source_extracts_nodes_edges_and_readiness(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    _write_sample_source(source)

    summary = summarize_real_module_source(source)

    assert summary["schema_version"] == "ordo.pathwalk.real_module_graph_summary.v1"
    assert summary["package"] == "sample.real_module"
    assert summary["start_node"] == "N_START"
    assert summary["counts"]["nodes"] == 2
    assert summary["counts"]["edges"] == 3
    assert summary["counts"]["branching_nodes"] == 1
    assert summary["counts"]["unmatched_handlers"] == 1
    assert summary["edge_target_counts"]["node"] == 1
    assert summary["edge_target_counts"]["gate"] == 1
    assert summary["edge_target_counts"]["terminal"] == 1
    assert summary["unresolved_targets"] == []
    assert summary["readiness"]["graph_summary_ready"] is True
    assert summary["readiness"]["testcase_generation_ready"] is False


def test_write_real_module_graph_summary_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    out = tmp_path / "graph"
    _write_sample_source(source)

    result = write_real_module_graph_summary(source, out)

    assert result["status"] == "passed"
    assert (out / "REAL_MODULE_GRAPH_SUMMARY.json").exists()
    assert (out / "REAL_MODULE_GRAPH_SUMMARY.md").exists()
    validation = json.loads((out / "VALIDATION_REPORT.json").read_text(encoding="utf-8"))
    assert validation["status"] == "passed"
    assert {item["check"] for item in validation["checks"]} >= {
        "source_yaml_loaded",
        "compiled_artifacts_not_read",
        "testcase_generation_not_claimed",
    }


def test_real_module_graph_cli_on_sample_source(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    out = tmp_path / "graph"
    _write_sample_source(source)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "utilities.ordo_pathwalk.cli",
            "real-module-graph",
            "--source",
            str(source),
            "--out",
            str(out),
        ],
        cwd=Path(__file__).resolve().parents[3],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout
    payload = json.loads(completed.stdout)
    assert payload["status"] == "passed"
    assert (out / "REAL_MODULE_GRAPH_SUMMARY.json").exists()

from utilities.ordo_pathwalk.generator.real_module import enumerate_terminal_paths_from_summary, write_real_module_terminal_paths


def test_enumerate_terminal_paths_from_graph_summary(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    _write_sample_source(source)
    summary = summarize_real_module_source(source)

    paths = enumerate_terminal_paths_from_summary(summary)

    assert paths["schema_version"] == "ordo.pathwalk.real_module_terminal_paths.v1"
    assert paths["milestone"] == "M60.7.2"
    assert paths["counts"]["terminal_paths"] == 2
    signatures = {item["branch_signature"] for item in paths["terminal_paths"]}
    assert "N_START=A -> N_A=* -> G_DONE" in signatures
    assert "N_START=B -> STOP_B" in signatures
    gate_path = next(item for item in paths["terminal_paths"] if item["terminal_target"] == "G_DONE")
    assert gate_path["outputs_allowed_after_terminal"] == ["OUT_PACKAGE"]
    assert gate_path["state_updates"] == ["selected", "note"]
    assert paths["readiness"]["terminal_path_enumeration_ready"] is True
    assert paths["readiness"]["testcase_generation_ready"] is False


def test_write_real_module_terminal_paths_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    graph_out = tmp_path / "graph"
    paths_out = tmp_path / "paths"
    _write_sample_source(source)
    write_real_module_graph_summary(source, graph_out)

    result = write_real_module_terminal_paths(graph_out / "REAL_MODULE_GRAPH_SUMMARY.json", paths_out)

    assert result["status"] == "passed"
    assert (paths_out / "REAL_MODULE_TERMINAL_PATHS.json").exists()
    assert (paths_out / "REAL_MODULE_TERMINAL_PATHS.md").exists()
    validation = json.loads((paths_out / "VALIDATION_REPORT.json").read_text(encoding="utf-8"))
    assert validation["status"] == "passed"
    assert {item["check"] for item in validation["checks"]} >= {
        "graph_summary_loaded",
        "terminal_paths_present",
        "compiled_artifacts_not_read",
        "testcase_generation_not_claimed",
    }


def test_real_module_paths_cli_on_graph_summary(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    graph_out = tmp_path / "graph"
    paths_out = tmp_path / "paths"
    _write_sample_source(source)
    write_real_module_graph_summary(source, graph_out)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "utilities.ordo_pathwalk.cli",
            "real-module-paths",
            "--summary",
            str(graph_out / "REAL_MODULE_GRAPH_SUMMARY.json"),
            "--out",
            str(paths_out),
        ],
        cwd=Path(__file__).resolve().parents[3],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout
    payload = json.loads(completed.stdout)
    assert payload["status"] == "passed"
    assert payload["counts"]["terminal_paths"] == 2
    assert (paths_out / "REAL_MODULE_TERMINAL_PATHS.json").exists()

from utilities.ordo_pathwalk.generator.real_module import generate_clean_path_cases_from_terminal_paths, write_real_module_clean_path_cases


def test_generate_clean_path_cases_from_terminal_paths(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    _write_sample_source(source)
    summary = summarize_real_module_source(source)
    paths = enumerate_terminal_paths_from_summary(summary)

    clean_cases = generate_clean_path_cases_from_terminal_paths(paths)

    assert clean_cases["schema_version"] == "ordo.pathwalk.real_module_clean_path_cases.v1"
    assert clean_cases["milestone"] == "M60.7.3"
    assert clean_cases["counts"]["clean_path_cases"] == 2
    assert clean_cases["counts"]["terminal_paths_input"] == 2
    assert clean_cases["readiness"]["clean_path_cases_ready"] is True
    assert clean_cases["readiness"]["runtime_execution_ready"] is False
    first = clean_cases["cases"][0]
    assert first["case_type"] == "clean_path"
    assert first["noise_pattern"] == "none"
    assert first["readiness"]["case_artifact_ready"] is True
    assert first["readiness"]["runtime_execution_ready"] is False
    assert first["answer_steps"][0]["node"] == "N_START"


def test_write_real_module_clean_path_case_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    graph_out = tmp_path / "graph"
    paths_out = tmp_path / "paths"
    cases_out = tmp_path / "cases_out"
    _write_sample_source(source)
    write_real_module_graph_summary(source, graph_out)
    write_real_module_terminal_paths(graph_out / "REAL_MODULE_GRAPH_SUMMARY.json", paths_out)

    result = write_real_module_clean_path_cases(paths_out / "REAL_MODULE_TERMINAL_PATHS.json", cases_out)

    assert result["status"] == "passed"
    assert (cases_out / "SUMMARY.json").exists()
    assert (cases_out / "SUMMARY.md").exists()
    assert (cases_out / "RAW_TESTCASE_MATRIX.csv").exists()
    assert (cases_out / "cases" / "CLEAN_TP_001.json").exists()
    assert (cases_out / "cases" / "CLEAN_TP_001.md").exists()
    validation = json.loads((cases_out / "VALIDATION_REPORT.json").read_text(encoding="utf-8"))
    assert validation["status"] == "passed"
    assert {item["check"] for item in validation["checks"]} >= {
        "terminal_paths_loaded",
        "one_case_per_terminal_path",
        "runtime_execution_not_claimed",
        "noise_generation_not_claimed",
    }


def test_real_module_clean_cases_cli_on_terminal_paths(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    graph_out = tmp_path / "graph"
    paths_out = tmp_path / "paths"
    cases_out = tmp_path / "cases_out"
    _write_sample_source(source)
    write_real_module_graph_summary(source, graph_out)
    write_real_module_terminal_paths(graph_out / "REAL_MODULE_GRAPH_SUMMARY.json", paths_out)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "utilities.ordo_pathwalk.cli",
            "real-module-clean-cases",
            "--paths",
            str(paths_out / "REAL_MODULE_TERMINAL_PATHS.json"),
            "--out",
            str(cases_out),
        ],
        cwd=Path(__file__).resolve().parents[3],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout
    payload = json.loads(completed.stdout)
    assert payload["status"] == "passed"
    assert payload["counts"]["clean_path_cases"] == 2
    assert (cases_out / "RAW_TESTCASE_MATRIX.csv").exists()


from utilities.ordo_pathwalk.generator.real_module import generate_noise_cases_from_terminal_paths, write_real_module_noise_cases


def test_generate_noise_cases_from_terminal_paths_first_patterns(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    _write_sample_source(source)
    summary = summarize_real_module_source(source)
    paths = enumerate_terminal_paths_from_summary(summary)

    noise_cases = generate_noise_cases_from_terminal_paths(paths)

    assert noise_cases["schema_version"] == "ordo.pathwalk.real_module_noise_cases.v1"
    assert noise_cases["milestone"] == "M60.7.5"
    assert noise_cases["counts"]["terminal_paths_input"] == 2
    assert noise_cases["counts"]["patterns"] == 4
    assert noise_cases["counts"]["noise_cases"] == 8
    assert noise_cases["pattern_counts"] == {
        "distraction": 2,
        "invalid_branch": 2,
        "clarification_without_submit": 2,
        "skip_ahead": 2,
    }
    assert noise_cases["readiness"]["noise_cases_ready"] is True
    assert noise_cases["readiness"]["runtime_execution_ready"] is False
    first = noise_cases["cases"][0]
    assert first["case_type"] == "noise_path"
    assert first["noise_pattern"] == "distraction"
    assert first["scripted_steps"][0]["input_kind"] == "distraction"
    invalid = next(case for case in noise_cases["cases"] if case["noise_pattern"] == "invalid_branch")
    assert invalid["scripted_steps"][0]["answer"] == "__INVALID_BRANCH_SENTINEL__"
    assert invalid["readiness"]["runtime_execution_ready"] is False
    clarification = next(case for case in noise_cases["cases"] if case["noise_pattern"] == "clarification_without_submit")
    assert clarification["scripted_steps"][0]["input_kind"] == "clarification_without_submit"
    skip = next(case for case in noise_cases["cases"] if case["noise_pattern"] == "skip_ahead")
    assert skip["scripted_steps"][0]["input_kind"] == "skip_ahead"


def test_write_real_module_noise_case_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    graph_out = tmp_path / "graph"
    paths_out = tmp_path / "paths"
    noise_out = tmp_path / "noise_out"
    _write_sample_source(source)
    write_real_module_graph_summary(source, graph_out)
    write_real_module_terminal_paths(graph_out / "REAL_MODULE_GRAPH_SUMMARY.json", paths_out)

    result = write_real_module_noise_cases(paths_out / "REAL_MODULE_TERMINAL_PATHS.json", noise_out)

    assert result["status"] == "passed"
    assert result["counts"]["noise_cases"] == 8
    assert (noise_out / "SUMMARY.json").exists()
    assert (noise_out / "SUMMARY.md").exists()
    assert (noise_out / "RAW_NOISE_TESTCASE_MATRIX.csv").exists()
    assert (noise_out / "cases" / "NOISE_TP_001_DISTRACTION.json").exists()
    assert (noise_out / "cases" / "NOISE_TP_001_INVALID_BRANCH.md").exists()
    assert (noise_out / "cases" / "NOISE_TP_001_CLARIFICATION_WITHOUT_SUBMIT.json").exists()
    assert (noise_out / "cases" / "NOISE_TP_001_SKIP_AHEAD.md").exists()
    validation = json.loads((noise_out / "VALIDATION_REPORT.json").read_text(encoding="utf-8"))
    assert validation["status"] == "passed"
    assert {item["check"] for item in validation["checks"]} >= {
        "terminal_paths_loaded",
        "one_case_per_terminal_path_per_pattern",
        "runtime_execution_not_claimed",
        "scoring_not_claimed",
        "calibration_not_claimed",
    }


def test_real_module_noise_cases_cli_on_terminal_paths(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    graph_out = tmp_path / "graph"
    paths_out = tmp_path / "paths"
    noise_out = tmp_path / "noise_out"
    _write_sample_source(source)
    write_real_module_graph_summary(source, graph_out)
    write_real_module_terminal_paths(graph_out / "REAL_MODULE_GRAPH_SUMMARY.json", paths_out)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "utilities.ordo_pathwalk.cli",
            "real-module-noise-cases",
            "--paths",
            str(paths_out / "REAL_MODULE_TERMINAL_PATHS.json"),
            "--out",
            str(noise_out),
            "--pattern",
            "distraction",
            "--pattern",
            "invalid_branch",
            "--pattern",
            "clarification_without_submit",
            "--pattern",
            "skip_ahead",
        ],
        cwd=Path(__file__).resolve().parents[3],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout
    payload = json.loads(completed.stdout)
    assert payload["status"] == "passed"
    assert payload["counts"]["noise_cases"] == 8
    assert (noise_out / "RAW_NOISE_TESTCASE_MATRIX.csv").exists()

from utilities.ordo_pathwalk.generator.real_module import generate_review_cards_from_case_summaries, write_real_module_review_cards


def test_generate_review_cards_from_clean_and_noise_summaries(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    _write_sample_source(source)
    summary = summarize_real_module_source(source)
    paths = enumerate_terminal_paths_from_summary(summary)
    clean = generate_clean_path_cases_from_terminal_paths(paths)
    noise = generate_noise_cases_from_terminal_paths(paths, patterns=["distraction", "invalid_branch"])

    review = generate_review_cards_from_case_summaries([clean, noise])

    assert review["schema_version"] == "ordo.pathwalk.real_module_review_cards.v1"
    assert review["milestone"] == "M61.0"
    assert review["counts"]["review_cards"] == 6
    assert review["counts"]["ready_cards"] == 6
    assert review["counts"]["runtime_executions"] == 0
    assert review["counts"]["scores"] == 0
    assert review["noise_pattern_counts"] == {"none": 2, "distraction": 2, "invalid_branch": 2}
    first = review["cards"][0]
    assert first["readiness"]["review_card_ready"] is True
    assert first["readiness"]["runtime_execution_ready"] is False
    noise_card = next(card for card in review["cards"] if card["noise_pattern"] == "distraction")
    assert noise_card["scripted_steps"][0]["submit_expected"] is False
    assert any("Runtime execution" in item["item"] or "runtime execution" in item["item"] for item in noise_card["checklist"])


def test_write_real_module_review_cards_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    graph_out = tmp_path / "graph"
    paths_out = tmp_path / "paths"
    clean_out = tmp_path / "clean"
    noise_out = tmp_path / "noise"
    cards_out = tmp_path / "cards"
    _write_sample_source(source)
    write_real_module_graph_summary(source, graph_out)
    write_real_module_terminal_paths(graph_out / "REAL_MODULE_GRAPH_SUMMARY.json", paths_out)
    write_real_module_clean_path_cases(paths_out / "REAL_MODULE_TERMINAL_PATHS.json", clean_out)
    write_real_module_noise_cases(paths_out / "REAL_MODULE_TERMINAL_PATHS.json", noise_out, patterns=["distraction", "invalid_branch"])

    result = write_real_module_review_cards([clean_out / "SUMMARY.json", noise_out / "SUMMARY.json"], cards_out)

    assert result["status"] == "passed"
    assert result["counts"]["review_cards"] == 6
    assert (cards_out / "REVIEW_CARDS.json").exists()
    assert (cards_out / "REVIEW_CARDS.md").exists()
    assert (cards_out / "RAW_REVIEW_CARD_MATRIX.csv").exists()
    assert (cards_out / "cards" / "CARD_001_CLEAN_TP_001.md").exists()
    validation = json.loads((cards_out / "VALIDATION_REPORT.json").read_text(encoding="utf-8"))
    assert validation["status"] == "passed"
    assert {item["check"] for item in validation["checks"]} >= {
        "case_summaries_loaded",
        "one_card_per_input_case",
        "runtime_execution_not_claimed",
        "scoring_not_claimed",
        "calibration_not_claimed",
    }


def test_real_module_review_cards_cli_on_case_summaries(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    graph_out = tmp_path / "graph"
    paths_out = tmp_path / "paths"
    clean_out = tmp_path / "clean"
    noise_out = tmp_path / "noise"
    cards_out = tmp_path / "cards"
    _write_sample_source(source)
    write_real_module_graph_summary(source, graph_out)
    write_real_module_terminal_paths(graph_out / "REAL_MODULE_GRAPH_SUMMARY.json", paths_out)
    write_real_module_clean_path_cases(paths_out / "REAL_MODULE_TERMINAL_PATHS.json", clean_out)
    write_real_module_noise_cases(paths_out / "REAL_MODULE_TERMINAL_PATHS.json", noise_out, patterns=["distraction"])

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "utilities.ordo_pathwalk.cli",
            "real-module-review-cards",
            "--summary",
            str(clean_out / "SUMMARY.json"),
            "--summary",
            str(noise_out / "SUMMARY.json"),
            "--out",
            str(cards_out),
        ],
        cwd=Path(__file__).resolve().parents[3],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout
    payload = json.loads(completed.stdout)
    assert payload["status"] == "passed"
    assert payload["counts"]["review_cards"] == 4
    assert (cards_out / "RAW_REVIEW_CARD_MATRIX.csv").exists()


def test_graph_contract_prunes_declared_review_loop_and_keeps_terminal_path(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        """
ordo:
  version: '0.12'
  package: sample.cyclic
nodes:
  - id: N_START
    on_answer:
      next: N_REVIEW
  - id: N_REVIEW
    on_answer:
      retry:
        next: N_START
      done:
        next: END_DONE
  - id: END_DONE
    terminal: true
graph_contract:
  entry_node: N_START
  terminal_node_ids: [END_DONE]
  allowed_cycle_regions:
    - id: LOOP_REVIEW
      nodes: [N_START, N_REVIEW]
      rationale: intentional review loop
""".strip() + "\n",
        encoding="utf-8",
    )
    summary = summarize_real_module_source(source)
    paths = enumerate_terminal_paths_from_summary(summary)
    assert summary["start_node"] == "N_START"
    assert summary["counts"]["dead_end_nodes"] == 0
    assert paths["readiness"]["terminal_path_enumeration_ready"] is True
    assert paths["counts"]["cycle_edges"] == 0
    assert paths["counts"]["dead_end_paths"] == 0
    assert paths["counts"]["terminal_paths"] == 1
    assert paths["terminal_paths"][0]["terminal_type"] == "node_terminal"


def test_graph_contract_uses_canonical_shortest_routes_for_cyclic_graph(tmp_path: Path) -> None:
    source = tmp_path / "source" / "program.ordo.yaml"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        """
ordo:
  version: '0.12'
  package: sample.canonical_paths
nodes:
  - id: N_START
    on_answer:
      left: {next: N_A}
      right: {next: N_B}
  - id: N_A
    on_answer:
      next: N_B
  - id: N_B
    on_answer:
      back: {next: N_A}
      finish: {next: STOP_DONE}
graph_contract:
  entry_node: N_START
  external_terminal_targets: [STOP_DONE]
  allowed_cycle_regions:
    - id: LOOP_AB
      nodes: [N_A, N_B]
      rationale: correction loop
""".strip() + "\n",
        encoding="utf-8",
    )
    paths = enumerate_terminal_paths_from_summary(summarize_real_module_source(source))
    assert paths["counts"]["terminal_paths"] == 1
    assert paths["counts"]["cycle_edges"] == 0
    assert paths["counts"]["intentional_loop_edges_pruned"] >= 1
    assert paths["readiness"]["clean_path_case_generation_ready"] is True
