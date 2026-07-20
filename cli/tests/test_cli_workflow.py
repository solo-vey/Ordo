from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from ordo.cli import main
from ordo.ci_release_evidence import source_tree_sha256


WORKSPACE = Path(__file__).resolve().parents[2]
CLI_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = WORKSPACE / "packages" / "ordo_project_builder"


def _write_ci_evidence(package: Path) -> Path:
    evidence = package / "reports" / "ci_release_evidence.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "ordo.ci_release_evidence.v1",
        "status": "passed",
        "revision": "test-revision",
        "run_id": "test-run",
        "issued_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_tree_sha256": source_tree_sha256(package),
        "test_matrix": [{"id": "full-required-matrix", "status": "passed"}],
    }
    evidence.write_text(json.dumps(payload), encoding="utf-8")
    return evidence


class OrdoCliWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_cli_test_"))
        self.package = self.tmp / "ordo_project_builder"
        shutil.copytree(EXAMPLE, self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_core_package_checks_and_helpers(self) -> None:
        self.assertEqual(main(["lint", str(self.package)]), 0)
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["test", str(self.package)]), 0)
        self.assertEqual(main(["coverage", str(self.package)]), 0)
        self.assertEqual(main(["validate-state", str(self.package), "--answers", str(self.package / "run_inputs" / "authoring_success.yaml")]), 0)
        self.assertEqual(main(["next-step", str(self.package), "--answers", str(self.package / "run_inputs" / "authoring_success.yaml")]), 0)
        self.assertEqual(main(["check-conflicts", str(self.package)]), 0)
        self.assertTrue((self.package / "compiled" / "program.ir.json").exists())
        self.assertTrue((self.package / "reports" / "state_validation_report.json").exists())

    def test_init_creates_lintable_package(self) -> None:
        target = self.tmp / "new_package"
        self.assertEqual(main(["init", str(target), "--package", "example.new_package"]), 0)
        self.assertTrue((target / "ordo.yml").exists())
        self.assertEqual(main(["lint", str(target)]), 0)

    def test_current_help_excludes_removed_registry_commands(self) -> None:
        result = subprocess.run([sys.executable, "-m", "ordo.cli", "--help"], cwd=CLI_ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("validate-state", result.stdout)
        self.assertIn("check-gate", result.stdout)
        self.assertIn("next-step", result.stdout)
        self.assertNotIn("generate-registry-site", result.stdout)
        self.assertNotIn("index-published-releases", result.stdout)
        self.assertNotIn("promote-release", result.stdout)
        self.assertNotIn("list-template-sets", result.stdout)


class TestDependencyLock(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_dependency_lock_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_lock_and_validate_lock_history_event_package(self):
        result = subprocess.run([sys.executable, "-m", "ordo.cli", "lock", str(self.package)], cwd=CLI_ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue((self.package / "ordo.lock.json").exists())
        result = subprocess.run([sys.executable, "-m", "ordo.cli", "validate-lock", str(self.package)], cwd=CLI_ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue((self.package / "reports" / "lock_report.json").exists())
        self.assertTrue((self.package / "reports" / "lock_validation_report.json").exists())


class ReleaseQualityChecksTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_release_quality_test_"))
        self.repo_check_report = WORKSPACE / "reports" / "repo_check_report.json"
        self.repo_check_report_existed = self.repo_check_report.is_file()
        self.repo_check_report_bytes = (
            self.repo_check_report.read_bytes()
            if self.repo_check_report_existed
            else None
        )

    def tearDown(self) -> None:
        if self.repo_check_report_existed:
            self.repo_check_report.parent.mkdir(parents=True, exist_ok=True)
            self.repo_check_report.write_bytes(self.repo_check_report_bytes or b"")
        else:
            self.repo_check_report.unlink(missing_ok=True)
        shutil.rmtree(self.tmp, ignore_errors=True)
    def _clean_transient_workspace_artifacts(self) -> None:
        # The source archive must not contain generated metadata or package helper outputs.
        # Editable installs and earlier tests can create these locally, so remove them
        # before validating source-archive hygiene.
        for path in list(WORKSPACE.rglob("*.egg-info")) + list(WORKSPACE.rglob("__pycache__")):
            shutil.rmtree(path, ignore_errors=True)
        for path in WORKSPACE.rglob("*.pyc"):
            path.unlink(missing_ok=True)
        for package in (WORKSPACE / "packages").iterdir():
            if not package.is_dir():
                continue
            for generated_name in ("compiled", "reports", "runtime", "generated_outputs"):
                generated_dir = package / generated_name
                if not generated_dir.exists():
                    continue
                for item in generated_dir.rglob("*"):
                    if item.is_file() and item.name not in {".gitkeep", "CLI_VALIDATION_SUMMARY.md", "PACKAGE_PROFILE_SUMMARY.md"}:
                        item.unlink()

    def test_repo_check_passes_current_workspace(self) -> None:
        self._clean_transient_workspace_artifacts()
        self.assertEqual(main(["repo-check", str(WORKSPACE)]), 0)

    def test_repo_check_detects_stale_package_generated_artifacts(self) -> None:
        self._clean_transient_workspace_artifacts()
        stale = WORKSPACE / "packages" / "ordo_project_builder" / "reports" / "stale_report.json"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text("{}\n", encoding="utf-8")
        try:
            self.assertEqual(main(["repo-check", str(WORKSPACE)]), 1)
            report = WORKSPACE / "reports" / "repo_check_report.json"
            self.assertIn("package_generated_artifacts_absent", report.read_text(encoding="utf-8"))
            self.assertIn("stale_report.json", report.read_text(encoding="utf-8"))
        finally:
            stale.unlink(missing_ok=True)

    def test_self_consistency_requires_repeated_model_judgment(self) -> None:
        package = self.tmp / "ordo_hybrid_executor"
        shutil.copytree(WORKSPACE / "packages" / "ordo_hybrid_executor", package)
        source = package / "source" / "program.ordo.yaml"
        text = source.read_text(encoding="utf-8")
        # Indentation-agnostic negative-fixture mutation. Always prove that
        # the source changed so this test cannot silently become a no-op.
        mutated = re.sub(
            r"(method:\s*self_consistency\n\s*trust_class:\s*)repeated_model_judgment",
            r"\1model_judgment",
            text,
            count=1,
        )
        self.assertNotEqual(
            mutated, text,
            "expected to inject a trust_class mismatch but source pattern was not found",
        )
        text = mutated
        source.write_text(text, encoding="utf-8")
        self.assertEqual(main(["lint", str(package)]), 0)
        report = package / "reports" / "lint_report.json"
        self.assertIn("SELF_CONSISTENCY_TRUST_MISMATCH", report.read_text(encoding="utf-8"))

    def test_compile_checks_ir_opcodes_against_registry(self) -> None:
        package = self.tmp / "ordo_project_builder"
        shutil.copytree(WORKSPACE / "packages" / "ordo_project_builder", package)
        self.assertEqual(main(["compile", str(package)]), 0)
        report = package / "reports" / "compile_report.json"
        self.assertIn('"opcode_registry_check"', report.read_text(encoding="utf-8"))

    def test_cli_test_output_declares_static_mode(self) -> None:
        result = subprocess.run([sys.executable, "-m", "ordo.cli", "test", str(EXAMPLE)], cwd=CLI_ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("[static mode", result.stdout)


if __name__ == "__main__":
    unittest.main()


class ContractArtifactCoverageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_contract_coverage_test_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_compile_fails_unknown_artifact_requirement_field(self) -> None:
        package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", package)
        source = package / "source" / "program.ordo.yaml"
        import yaml
        data = yaml.safe_load(source.read_text(encoding="utf-8"))
        data["artifact_requirements"][0]["requires"][0]["must_include_fields"].append("unknown_identity_field")
        source.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        self.assertEqual(main(["compile", str(package)]), 1)
        report = package / "reports" / "compile_report.json"
        self.assertIn("ORDO-COV-REF-003", report.read_text(encoding="utf-8"))

    def test_coverage_fails_confirmed_contract_without_artifact_mapping(self) -> None:
        package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", package)
        source = package / "source" / "program.ordo.yaml"
        text = source.read_text(encoding="utf-8").replace("artifact_requirements:", "artifact_requirements_disabled:", 1)
        source.write_text(text, encoding="utf-8")
        self.assertEqual(main(["coverage", str(package)]), 1)
        report = package / "reports" / "coverage_report.json"
        self.assertIn("ORDO-COV-001", report.read_text(encoding="utf-8"))

    def test_history_event_contract_artifact_coverage_passes(self) -> None:
        package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", package)
        self.assertEqual(main(["compile", str(package)]), 0)
        self.assertEqual(main(["coverage", str(package)]), 0)
        report = package / "reports" / "coverage_report.json"
        self.assertIn('"contract_artifact_coverage"', report.read_text(encoding="utf-8"))


class RenderedArtifactValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_artifact_validation_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _generate(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["lock", str(self.package)]), 0)
        self.assertEqual(main(["validate-lock", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--answers", str(self.package / "run_inputs" / "intake_success.yaml"), "--non-interactive"]), 0)
        self.assertEqual(main(["validate-state", str(self.package), "--answers", str(self.package / "run_inputs" / "intake_success.yaml")]), 0)
        self.assertEqual(main(["generate-output", str(self.package)]), 0)

    def test_validate_artifacts_passes_generated_history_event_outputs(self) -> None:
        self._generate()
        self.assertEqual(main(["validate-artifacts", str(self.package)]), 0)
        report = self.package / "reports" / "artifact_validation_report.json"
        self.assertIn('"mode": "rendered_artifact_validation"', report.read_text(encoding="utf-8"))

    def test_validate_artifacts_fails_when_confirmed_alias_missing_from_jira(self) -> None:
        self._generate()
        jira = next((self.package / "generated_outputs").glob("02_JIRA_TASK_*.md"))
        jira.write_text(jira.read_text(encoding="utf-8").replace("LU_CHANGE_STATUS", "REMOVED_ALIAS"), encoding="utf-8")
        self.assertEqual(main(["validate-artifacts", str(self.package)]), 1)
        report = self.package / "reports" / "artifact_validation_report.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn("ORDO-COV-002", text)
        self.assertIn("event_alias", text)

class CrossArtifactConsistencyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_consistency_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _generate(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["lock", str(self.package)]), 0)
        self.assertEqual(main(["validate-lock", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--answers", str(self.package / "run_inputs" / "intake_success.yaml"), "--non-interactive"]), 0)
        self.assertEqual(main(["validate-state", str(self.package), "--answers", str(self.package / "run_inputs" / "intake_success.yaml")]), 0)
        self.assertEqual(main(["generate-output", str(self.package)]), 0)

    def test_consistency_passes_generated_history_event_outputs(self) -> None:
        self._generate()
        self.assertEqual(main(["consistency", str(self.package)]), 0)
        report = self.package / "reports" / "CONSISTENCY_CHECK_REPORT.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn('"mode": "cross_artifact_consistency"', text)
        self.assertIn('"go_no_go": "go"', text)

    def test_consistency_fails_when_alias_differs_across_artifacts(self) -> None:
        self._generate()
        jira = next((self.package / "generated_outputs").glob("02_JIRA_TASK_*.md"))
        jira.write_text(jira.read_text(encoding="utf-8").replace("LU_CHANGE_STATUS", "LU_WRONG_STATUS"), encoding="utf-8")
        self.assertEqual(main(["consistency", str(self.package)]), 1)
        report = self.package / "reports" / "CONSISTENCY_CHECK_REPORT.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn("ORDO-COV-004", text)
        self.assertIn("G_EVENT_IDENTITY_CONTRACT.event_alias", text)

class GoNoGoPipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_go_no_go_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_go_no_go_passes_generated_history_event_outputs(self) -> None:
        self.assertEqual(main([
            "go-no-go",
            str(self.package),
            "--run-intake",
            "--answers", str(self.package / "run_inputs" / "intake_success.yaml"),
            "--generate-output",
        ]), 0)
        report = self.package / "reports" / "GO_NO_GO_REPORT.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn('"status": "go"', text)
        self.assertIn('"validate-artifacts"', text)
        self.assertIn('"consistency"', text)

    def test_go_no_go_reuses_latest_intake_state_when_answers_omitted(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--answers", str(self.package / "run_inputs" / "intake_success.yaml"), "--non-interactive"]), 0)
        self.assertEqual(main(["validate-state", str(self.package), "--answers", str(self.package / "run_inputs" / "intake_success.yaml")]), 0)
        self.assertEqual(main(["generate-output", str(self.package)]), 0)
        self.assertEqual(main(["go-no-go", str(self.package)]), 0)
        report = self.package / "reports" / "GO_NO_GO_REPORT.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn('"status": "go"', text)

    def test_go_no_go_fails_when_generated_artifacts_are_inconsistent(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--answers", str(self.package / "run_inputs" / "intake_success.yaml"), "--non-interactive"]), 0)
        self.assertEqual(main(["validate-state", str(self.package), "--answers", str(self.package / "run_inputs" / "intake_success.yaml")]), 0)
        self.assertEqual(main(["generate-output", str(self.package)]), 0)
        jira = next((self.package / "generated_outputs").glob("02_JIRA_TASK_*.md"))
        jira.write_text(jira.read_text(encoding="utf-8").replace("LU_CHANGE_STATUS", "LU_BROKEN_STATUS"), encoding="utf-8")
        self.assertEqual(main(["go-no-go", str(self.package), "--answers", str(self.package / "run_inputs" / "intake_success.yaml")]), 1)
        report = self.package / "reports" / "GO_NO_GO_REPORT.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn("no_go_requires_artifact_fix", text)
        self.assertIn("ORDO-COV-004", text)

class TwoTierRenderingModelTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_two_tier_rendering_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)
        self.catalog = self.package / "output_templates" / "history_event" / "guided_intake_outputs" / "0.1.1" / "output_templates.yaml"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _prepare_outputs(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["lock", str(self.package)]), 0)
        self.assertEqual(main(["validate-lock", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--answers", str(self.package / "run_inputs" / "intake_success.yaml"), "--non-interactive"]), 0)
        self.assertEqual(main(["validate-state", str(self.package), "--answers", str(self.package / "run_inputs" / "intake_success.yaml")]), 0)
        self.assertEqual(main(["generate-output", str(self.package)]), 0)

    def test_deterministic_template_with_for_block_fails_lint(self) -> None:
        template = self.catalog.parent / "templates" / "01_history_event_passport.md"
        template.write_text(template.read_text(encoding="utf-8") + "\n{% for x in state.items %}{{ x }}{% endfor %}\n", encoding="utf-8")
        self.assertEqual(main(["lint", str(self.package)]), 1)
        report = self.package / "reports" / "lint_report.json"
        self.assertIn("ORDO-RENDER-001", report.read_text(encoding="utf-8"))

    def test_model_assisted_template_cannot_use_simple_renderer(self) -> None:
        text = self.catalog.read_text(encoding="utf-8").replace("renderer: ai.yaml", "renderer: ordo.simple")
        self.catalog.write_text(text, encoding="utf-8")
        self.assertEqual(main(["lint", str(self.package)]), 1)
        report = self.package / "reports" / "lint_report.json"
        self.assertIn("ORDO-RENDER-002", report.read_text(encoding="utf-8"))

    def test_generate_output_routes_model_assisted_to_handoff(self) -> None:
        self._prepare_outputs()
        handoff = self.package / "runtime" / "model_assisted_render_handoff" / "QA_AUTOMATION_SPEC_MODEL_ASSISTED.json"
        self.assertTrue(handoff.exists())
        self.assertFalse(any((self.package / "generated_outputs").glob("08_QA_AUTOMATION_SPEC_*.yaml")))
        report = self.package / "reports" / "output_generation_report.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn('"model_assisted_handoffs_created": 1', text)
        self.assertIn('"deterministic_templates_generated": 4', text)

    def test_model_assisted_output_invented_provider_class_fails(self) -> None:
        self._prepare_outputs()
        rendered = self.package / "generated_outputs" / "08_QA_AUTOMATION_SPEC_LU_CHANGE_STATUS.yaml"
        rendered.write_text("automation_spec:\n  alias: LU_CHANGE_STATUS\n  provider_class: InventedProviderClass\n  cases: []\n", encoding="utf-8")
        self.assertEqual(main(["validate-artifacts", str(self.package)]), 1)
        report = self.package / "reports" / "artifact_validation_report.json"
        self.assertIn("ORDO-RENDER-003", report.read_text(encoding="utf-8"))

    def test_tbd_removed_without_confirmed_state_fails(self) -> None:
        self._prepare_outputs()
        rendered = self.package / "generated_outputs" / "08_QA_AUTOMATION_SPEC_LU_CHANGE_STATUS.yaml"
        rendered.write_text("automation_spec:\n  provider_class: CapitalProvider\n  cases: []\n", encoding="utf-8")
        self.assertEqual(main(["validate-artifacts", str(self.package)]), 1)
        report = self.package / "reports" / "artifact_validation_report.json"
        self.assertIn("ORDO-RENDER-004", report.read_text(encoding="utf-8"))

    def test_model_assisted_yaml_must_parse_after_rendering(self) -> None:
        self._prepare_outputs()
        rendered = self.package / "generated_outputs" / "08_QA_AUTOMATION_SPEC_LU_CHANGE_STATUS.yaml"
        rendered.write_text("automation_spec:\n  alias: LU_CHANGE_STATUS\n  broken: [\n", encoding="utf-8")
        self.assertEqual(main(["validate-artifacts", str(self.package)]), 1)
        report = self.package / "reports" / "artifact_validation_report.json"
        self.assertIn("ORDO-RENDER-005", report.read_text(encoding="utf-8"))

    def test_confirmed_values_in_rendered_artifacts_match_state(self) -> None:
        self._prepare_outputs()
        self.assertEqual(main(["validate-artifacts", str(self.package)]), 0)
        report = self.package / "reports" / "artifact_validation_report.json"
        self.assertIn('"status": "passed"', report.read_text(encoding="utf-8"))


class RuntimeSourceOfTruthTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_runtime_test_"))
        self.package = self.tmp / "ordo_project_builder"
        shutil.copytree(WORKSPACE / "packages" / "ordo_project_builder", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_next_step_fails_when_ir_is_stale(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        source = self.package / "source" / "program.ordo.yaml"
        source.write_text(source.read_text(encoding="utf-8") + "\n# touched after compile\n", encoding="utf-8")
        self.assertEqual(main(["next-step", str(self.package)]), 1)
        report = self.package / "reports" / "next_step_report.json"
        self.assertIn("ORDO-RUNTIME-004", report.read_text(encoding="utf-8"))

    def test_next_step_uses_compiled_ir_first_node(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["next-step", str(self.package)]), 0)
        report = self.package / "reports" / "next_step_report.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn('"runtime_source": "compiled_ir"', text)
        self.assertIn('"suggested_next_node": "N_PROJECT_GOAL"', text)

    def test_generate_output_requires_validate_state_passed(self) -> None:
        package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", package)
        self.assertEqual(main(["compile", str(package)]), 0)
        self.assertEqual(main(["intake", str(package), "--answers", str(package / "run_inputs" / "intake_success.yaml"), "--non-interactive"]), 0)
        self.assertEqual(main(["generate-output", str(package)]), 1)
        report = package / "reports" / "output_generation_report.json"
        self.assertIn("ORDO-COV-005", report.read_text(encoding="utf-8"))

    def test_validate_cli_status_fails_false_passed_claim(self) -> None:
        report = self.tmp / "handoff_report.json"
        report.write_text('{"cli_status":"executed_cli_passed"}', encoding="utf-8")
        self.assertEqual(main(["validate-cli-status", str(report)]), 1)
        truth = self.tmp / "handoff_report_cli_truthfulness_report.json"
        self.assertIn("ORDO-RUNTIME-TRUTH-003", truth.read_text(encoding="utf-8"))

class RuntimeGuidedIntakeEntryProtocolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_runtime_entry_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_runtime_entry_requires_start_here_and_returns_first_ir_node(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["runtime-entry", str(self.package)]), 0)
        report = self.package / "reports" / "runtime_entry_report.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn('"mode": "runtime_guided_intake_entry_protocol"', text)
        self.assertIn('"node_id": "N_EVENT_GOAL"', text)
        self.assertIn('"must_not_invent_question_order": true', text)

    def test_runtime_entry_fails_without_start_here_file(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        (self.package / "START_HERE_RUNTIME_MODE.md").unlink()
        self.assertEqual(main(["runtime-entry", str(self.package)]), 1)
        report = self.package / "reports" / "runtime_entry_report.json"
        self.assertIn("ORDO-RUNTIME-007", report.read_text(encoding="utf-8"))

    def test_history_event_path_a_has_no_a1_a5_subquestions(self) -> None:
        import yaml
        data = yaml.safe_load((self.package / "source" / "program.ordo.yaml").read_text(encoding="utf-8"))
        node = next(n for n in data["nodes"] if n["id"] == "N_PATH_SELECT")
        self.assertEqual(node["allowed_answers"], ["A", "B", "C", "D"])
        question = node["question"]
        for forbidden in ["A1", "A2", "A3", "A4", "A5"]:
            self.assertNotIn(forbidden, question)

    def test_next_step_after_path_a_uses_runtime_a_flow(self) -> None:
        answers = self.tmp / "answers_a.yaml"
        answers.write_text('N_EVENT_GOAL: "Зміна статутного капіталу"\nN_PATH_SELECT: A\n', encoding="utf-8")
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["next-step", str(self.package), "--answers", str(answers)]), 0)
        report = self.package / "reports" / "next_step_report.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn('"runtime_source": "compiled_ir"', text)
        self.assertIn('"suggested_next_node": "N_EVENT_ALIAS"', text)

class RuntimeModeStartFilesStandardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_runtime_start_files_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_minimal_prompt_exists_and_does_not_duplicate_protocol(self) -> None:
        prompt = self.package / "START_PROMPT_RUNTIME_MODE.md"
        self.assertTrue(prompt.exists())
        text = prompt.read_text(encoding="utf-8")
        self.assertIn("START_HERE_RUNTIME_MODE.md", text)
        self.assertLessEqual(len(text.split()), 256)
        self.assertNotIn("Artifact validation discipline", text)
        self.assertNotIn("Gate discipline", text)

    def test_runtime_rules_live_inside_package(self) -> None:
        start = self.package / "START_HERE_RUNTIME_MODE.md"
        self.assertTrue(start.exists())
        text = start.read_text(encoding="utf-8")
        for expected in [
            "Runtime loading protocol",
            "Source of truth model",
            "CLI truthfulness",
            "Fallback mode",
            "Gate discipline",
            "Artifact validation discipline",
        ]:
            self.assertIn(expected, text)

    def test_no_memory_mode_is_explicit(self) -> None:
        text = (self.package / "START_HERE_RUNTIME_MODE.md").read_text(encoding="utf-8")
        self.assertIn("Do not conduct guided intake", text)
        self.assertIn("from memory", text)
        self.assertIn("compiled IR", text)

    def test_lint_requires_runtime_start_files_standard(self) -> None:
        (self.package / "START_PROMPT_RUNTIME_MODE.md").write_text(
            "# Bad prompt\n\n" + "Gate discipline " * 120,
            encoding="utf-8",
        )
        self.assertEqual(main(["lint", str(self.package)]), 1)
        report = self.package / "reports" / "lint_report.json"
        self.assertIn("ORDO-RUNTIME-014", report.read_text(encoding="utf-8"))

    def test_release_report_has_cli_status_and_summary_template(self) -> None:
        self.assertEqual(main(["validate-release", str(self.package)]), 0)
        report = self.package / "reports" / "release_validation_report.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn('"cli_status": "executed_cli_passed"', text)
        self.assertEqual(main(["validate-cli-status", str(report)]), 0)
        summary = self.package / "reports" / "CLI_VALIDATION_SUMMARY.md"
        self.assertTrue(summary.exists())
        self.assertIn("CLI status: executed_cli_passed", summary.read_text(encoding="utf-8"))

    def test_cli_status_required(self) -> None:
        report = self.tmp / "report_without_cli_status.json"
        report.write_text('{"status":"passed"}', encoding="utf-8")
        self.assertEqual(main(["validate-cli-status", str(report)]), 1)
        truth = self.tmp / "report_without_cli_status_cli_truthfulness_report.json"
        self.assertIn("ORDO-RUNTIME-TRUTH-001", truth.read_text(encoding="utf-8"))

    def test_init_template_includes_runtime_start_files(self) -> None:
        target = self.tmp / "new_runtime_pkg"
        self.assertEqual(main(["init", str(target), "--package", "example.runtime_pkg"]), 0)
        self.assertTrue((target / "START_HERE_RUNTIME_MODE.md").exists())
        self.assertTrue((target / "START_PROMPT_RUNTIME_MODE.md").exists())
        self.assertTrue((target / "reports" / "CLI_VALIDATION_SUMMARY.md").exists())
        self.assertEqual(main(["lint", str(target)]), 0)

    def test_runtime_entry_auto_compiles_missing_or_stale_ir(self) -> None:
        compiled = self.package / "compiled" / "program.ir.json"
        compiled.unlink(missing_ok=True)
        self.assertEqual(main(["runtime-entry", str(self.package)]), 0)
        self.assertTrue(compiled.exists())
        report = self.package / "reports" / "runtime_entry_report.json"
        self.assertIn('"auto_compiled_ir": true', report.read_text(encoding="utf-8"))

class PackageProfilesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_package_profiles_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _prepare_validated_package(self) -> None:
        self.assertEqual(main(["validate-release", str(self.package)]), 0)

    def _zip_names(self, path: Path) -> set[str]:
        import zipfile
        with zipfile.ZipFile(path) as zf:
            return set(zf.namelist())

    def test_runtime_package_excludes_source_and_contains_runtime_contract(self) -> None:
        self._prepare_validated_package()
        out = self.tmp / "runtime.zip"
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--out", str(out), "--ci-evidence", str(_write_ci_evidence(self.package))]), 0)
        names = self._zip_names(out)
        prefix = self.package.name + "/"
        self.assertNotIn(prefix + "source/program.ordo.yaml", names)
        self.assertFalse(any(n.startswith(prefix + "tests/") for n in names))
        self.assertFalse(any(n.startswith(prefix + "run_inputs/") for n in names))
        self.assertIn(prefix + "compiled/program.ir.json", names)
        self.assertIn(prefix + "START_HERE_RUNTIME_MODE.md", names)
        self.assertIn(prefix + "START_PROMPT_RUNTIME_MODE.md", names)
        self.assertTrue(any(n.startswith(prefix + "output_templates/") for n in names))
        self.assertIn(prefix + "ordo.runtime.json", names)
        self.assertIn(prefix + "reports/BUILD_MANIFEST.json", names)
        self.assertIn(prefix + "reports/SHA256SUMS.txt", names)
        self.assertIn(prefix + "cli_embedded/ordo", names)
        self.assertIn(prefix + "cli_embedded/README.md", names)
        self.assertTrue(any(n.startswith(prefix + "cli_embedded/ordo_pkg/ordo/") for n in names))

    def test_runtime_embedded_cli_blocks_authoring_commands(self) -> None:
        self._prepare_validated_package()
        out = self.tmp / "runtime.zip"
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--out", str(out), "--ci-evidence", str(_write_ci_evidence(self.package))]), 0)
        import zipfile
        extract_dir = self.tmp / "runtime_extract"
        with zipfile.ZipFile(out) as zf:
            zf.extractall(extract_dir)
        embedded = extract_dir / self.package.name / "cli_embedded" / "ordo"
        self.assertTrue(embedded.exists())
        import subprocess, sys
        result = subprocess.run([sys.executable, str(embedded), "package", str(extract_dir / self.package.name)], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("blocks non-runtime command", result.stderr)

    def test_runtime_manifest_declares_embedded_cli_trust_level(self) -> None:
        self._prepare_validated_package()
        out = self.tmp / "runtime.zip"
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--out", str(out), "--ci-evidence", str(_write_ci_evidence(self.package))]), 0)
        text = (self.package / "ordo.runtime.json").read_text(encoding="utf-8")
        self.assertIn('"embedded_cli_included": true', text)
        self.assertIn('"embedded_cli_path": "cli_embedded/ordo"', text)
        self.assertIn('"trust_level": "level_1_cli_in_package_hard_stop"', text)

    def test_evidence_package_excludes_editable_source(self) -> None:
        self._prepare_validated_package()
        out = self.tmp / "evidence.zip"
        self.assertEqual(main(["package", str(self.package), "--profile", "evidence", "--out", str(out), "--allow-unvalidated-output"]), 0)
        names = self._zip_names(out)
        prefix = self.package.name + "/"
        self.assertFalse(any(n.startswith(prefix + "source/") for n in names))
        self.assertFalse(any(n.startswith(prefix + "tests/") for n in names))
        self.assertFalse(any(n.startswith(prefix + "run_inputs/") for n in names))
        self.assertTrue(any(n.startswith(prefix + "reports/") for n in names))

    def test_dev_package_contains_source_and_tests(self) -> None:
        self._prepare_validated_package()
        out = self.tmp / "dev.zip"
        self.assertEqual(main(["package", str(self.package), "--profile", "dev", "--out", str(out), "--ci-evidence", str(_write_ci_evidence(self.package))]), 0)
        names = self._zip_names(out)
        prefix = self.package.name + "/"
        self.assertIn(prefix + "source/program.ordo.yaml", names)
        self.assertIn(prefix + "tests/test_cases.yaml", names)

    def test_runtime_package_fails_when_ir_missing(self) -> None:
        (self.package / "compiled" / "program.ir.json").unlink(missing_ok=True)
        out = self.tmp / "runtime_missing_ir.zip"
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--out", str(out), "--allow-unvalidated-output", "--ci-evidence", str(_write_ci_evidence(self.package))]), 1)
        report = self.package / "reports" / "package_report.json"
        self.assertIn("ORDO-PACKAGE-003", report.read_text(encoding="utf-8"))

    def test_runtime_package_fails_when_ir_stale(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        source = self.package / "source" / "program.ordo.yaml"
        source.write_text(source.read_text(encoding="utf-8") + "\n# stale after compile\n", encoding="utf-8")
        out = self.tmp / "runtime_stale_ir.zip"
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--out", str(out), "--allow-unvalidated-output", "--ci-evidence", str(_write_ci_evidence(self.package))]), 1)
        report = self.package / "reports" / "package_report.json"
        self.assertIn("ORDO-RUNTIME-004", report.read_text(encoding="utf-8"))

    def test_runtime_package_fails_false_executed_cli_passed_claim(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        fake = self.package / "reports" / "release_validation_report.json"
        fake.parent.mkdir(parents=True, exist_ok=True)
        fake.write_text('{"cli_status":"executed_cli_passed"}', encoding="utf-8")
        out = self.tmp / "runtime_false_cli.zip"
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--out", str(out), "--allow-unvalidated-output", "--ci-evidence", str(_write_ci_evidence(self.package))]), 1)
        report = self.package / "reports" / "package_report.json"
        self.assertIn("ORDO-PACKAGE-010", report.read_text(encoding="utf-8"))

class RuntimeCheckpointDisciplineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_checkpoint_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_next_step_returns_earliest_incomplete_node_not_latest_requested(self) -> None:
        state = self.tmp / "state.yaml"
        state.write_text(
            "event_goal: Зміна статутного капіталу\n"
            "selected_path: A\n"
            "current_node: N_QA_SCOPE\n",
            encoding="utf-8",
        )
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["next-step", str(self.package), "--state", str(state)]), 0)
        report = self.package / "reports" / "next_step_report.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn('"earliest_incomplete_node": "N_EVENT_ALIAS"', text)
        self.assertIn('"suggested_next_node": "N_EVENT_ALIAS"', text)
        self.assertIn('"forward_allowed": false', text)

    def test_alias_without_display_names_leaves_display_name_checkpoint_open(self) -> None:
        answers = self.tmp / "answers_alias_only.yaml"
        answers.write_text(
            'N_EVENT_GOAL: "Зміна статутного капіталу"\n'
            'N_PATH_SELECT: A\n'
            'N_EVENT_ALIAS: LU_CHANGE_CAPITAL\n',
            encoding="utf-8",
        )
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["next-step", str(self.package), "--answers", str(answers)]), 0)
        report = self.package / "reports" / "next_step_report.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn('"earliest_incomplete_node": "N_DISPLAY_NAME_UK"', text)
        self.assertIn('"open_required_fields": [\n    "display_name_uk"', text)

    def test_node_merge_attempt_detected_without_batch_permission_fails(self) -> None:
        state = self.tmp / "state_merge.yaml"
        state.write_text(
            "requires_checkpoint_table: true\n"
            "conversation_step_node_ids:\n"
            "  - N_SOURCE_FIELD\n"
            "  - N_VALUE_SEMANTICS\n"
            "event_goal: goal\n"
            "selected_path: A\n"
            "event_alias: LU_CHANGE_CAPITAL\n"
            "display_name_uk: Зміна капіталу\n"
            "display_name_en: Capital changed\n",
            encoding="utf-8",
        )
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["validate-state", str(self.package), "--state", str(state)]), 1)
        report = self.package / "reports" / "state_validation_report.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn("ORDO-CHECKPOINT-003", text)
        self.assertIn('"node_merge_attempt_detected": true', text)

    def test_generate_output_blocked_while_checkpoint_gaps_remain(self) -> None:
        answers = self.tmp / "answers_partial.yaml"
        answers.write_text('N_EVENT_GOAL: "goal"\nN_PATH_SELECT: A\n', encoding="utf-8")
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["validate-state", str(self.package), "--answers", str(answers)]), 1)
        self.assertEqual(main(["generate-output", str(self.package)]), 1)
        report = self.package / "reports" / "output_generation_report.json"
        self.assertIn("ORDO-CHECKPOINT-006", report.read_text(encoding="utf-8"))

    def test_start_here_contains_one_question_checkpoint_protocol(self) -> None:
        text = (self.package / "START_HERE_RUNTIME_MODE.md").read_text(encoding="utf-8")
        self.assertIn("Runtime checkpoint discipline", text)
        self.assertIn("one node at a time", text)
        self.assertIn("One question:", text)
        self.assertIn("Hard-stop fallback mode", text)
        self.assertIn("cli_embedded/ordo", text)
        self.assertIn("DETERMINISM_NOT_ENFORCED", text)

class RuntimeIncrementalIntakeEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_m59_2_intake_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_intake_submit_writes_per_node_evidence_and_digest(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        report = self.package / "reports" / "intake_submit_report.json"
        data = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(data["mode"], "runtime_incremental_intake_submit")
        self.assertEqual(data["runtime_source"], "compiled_ir")
        self.assertEqual(data["next_node"], "N_PATH_SELECT")
        self.assertIn("report_digest", data)
        evidence = self.package / data["evidence_report"]
        self.assertTrue(evidence.exists())
        evidence_data = json.loads(evidence.read_text(encoding="utf-8"))
        self.assertEqual(evidence_data["mode"], "runtime_incremental_intake_evidence")
        self.assertEqual(evidence_data["node_id"], "N_EVENT_GOAL")
        self.assertIn("evidence_digest", evidence_data)
        self.assertEqual(data["evidence_digest"]["value"], evidence_data["evidence_digest"]["value"])

    def test_intake_submit_blocks_skipping_earliest_incomplete_node(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_PATH_SELECT", "--answer", "A"]), 1)
        report = self.package / "reports" / "intake_submit_report.json"
        text = report.read_text(encoding="utf-8")
        self.assertIn("ORDO-INTAKE-002", text)
        self.assertIn('"expected_node": "N_EVENT_GOAL"', text)

    def test_embedded_runtime_cli_can_submit_from_compiled_ir_without_source_yaml(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        out = self.tmp / "runtime.zip"
        self.assertEqual(main(["validate-release", str(self.package)]), 0)
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--out", str(out), "--ci-evidence", str(_write_ci_evidence(self.package))]), 0)
        extract_dir = self.tmp / "runtime_extract"
        import zipfile, subprocess, sys
        with zipfile.ZipFile(out) as zf:
            zf.extractall(extract_dir)
        runtime_pkg = extract_dir / self.package.name
        self.assertFalse((runtime_pkg / "source" / "program.ordo.yaml").exists())
        embedded = runtime_pkg / "cli_embedded" / "ordo"
        result = subprocess.run(
            [sys.executable, str(embedded), "intake", str(runtime_pkg), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("evidence:", result.stdout)
        self.assertIn("sha256=", result.stdout)
        submit_report = runtime_pkg / "reports" / "intake_submit_report.json"
        self.assertIn('"runtime_source": "compiled_ir"', submit_report.read_text(encoding="utf-8"))

    def test_intake_submit_accepts_answer_file_and_writes_live_session_state(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        answer_file = self.tmp / "answer.yaml"
        answer_file.write_text('answer: "Зміна капіталу"\n', encoding="utf-8")
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer-file", str(answer_file)]), 0)
        report = json.loads((self.package / "reports" / "intake_submit_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["next_node"], "N_PATH_SELECT")
        self.assertEqual(report["live_session_state"], "runtime/live_session_state.json")
        live = json.loads((self.package / "runtime" / "live_session_state.json").read_text(encoding="utf-8"))
        self.assertEqual(live["current_node"], "N_PATH_SELECT")
        self.assertEqual(live["state"]["event_goal"], "Зміна капіталу")

    def test_next_step_uses_live_session_state_when_state_omitted(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        self.assertEqual(main(["next-step", str(self.package)]), 0)
        report = json.loads((self.package / "reports" / "next_step_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["suggested_next_node"], "N_PATH_SELECT")
        self.assertTrue(str(report.get("state_source", "")).endswith("runtime/live_session_state.json"))

    def test_second_submit_resumes_from_live_session_without_state_arg(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_PATH_SELECT", "--answer", "A"]), 0)
        report = json.loads((self.package / "reports" / "intake_submit_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["input"]["state_file"], "runtime/live_session_state.json")
        self.assertEqual(report["state"]["selected_path"], "A")

class RuntimeSessionChainM59_3Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_m59_3_chain_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_verify_session_passes_after_incremental_submit(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        self.assertEqual(main(["verify-session", str(self.package)]), 0)
        report = json.loads((self.package / "reports" / "session_verification_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["terminal_line"], "session-chain: intact")
        self.assertEqual(report["snapshots_checked"], 2)
        self.assertTrue(report["canary_present"])
        snapshot = json.loads((self.package / "runtime" / "state_snapshots" / "SESSION-001_N_EVENT_GOAL.json").read_text(encoding="utf-8"))
        self.assertIn("session_chain", snapshot)
        self.assertIn("state", snapshot)
        self.assertNotIn("session_chain", snapshot["state"])

    def test_verify_session_detects_broken_chain_when_snapshot_missing(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        initial = self.package / "runtime" / "state_snapshots" / "SESSION-000_000_initial.json"
        initial.unlink()
        self.assertEqual(main(["verify-session", str(self.package)]), 1)
        text = (self.package / "reports" / "session_verification_report.json").read_text(encoding="utf-8")
        self.assertIn("session-chain: broken at seq 0", text)
        self.assertIn("ORDO-CHAIN-002", text)

    def test_verify_session_detects_canary_leak(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        ir = json.loads((self.package / "compiled" / "program.ir.json").read_text(encoding="utf-8"))
        canary = ir["security"]["canary_secret"]
        output = self.package / "generated_outputs" / "leak.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(canary, encoding="utf-8")
        self.assertEqual(main(["verify-session", str(self.package)]), 1)
        text = (self.package / "reports" / "session_verification_report.json").read_text(encoding="utf-8")
        self.assertIn("CANARY LEAK", text)
        self.assertIn("ORDO-CANARY-001", text)

    def test_compiled_ir_canary_is_not_exposed_as_runtime_node(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        ir = json.loads((self.package / "compiled" / "program.ir.json").read_text(encoding="utf-8"))
        self.assertTrue(any(op.get("canary") for op in ir.get("ops", [])))
        self.assertEqual(main(["next-step", str(self.package)]), 0)
        report = (self.package / "reports" / "next_step_report.json").read_text(encoding="utf-8")
        self.assertNotIn("N99_CANARY_DO_NOT_EMIT", report)
        self.assertNotIn(ir["security"]["canary_secret"], report)


class MultiTargetRuntimeCompilationM60_1Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_m60_1_targets_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_compile_writes_targets_manifest_and_ordo_code_view(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        manifest = json.loads((self.package / "compiled" / "targets.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["canonical_target"], "json-ir")
        self.assertIn("json-ir", manifest["targets"])
        self.assertIn("ordo-code-view", manifest["targets"])
        view = (self.package / "compiled" / "program.ordo.view").read_text(encoding="utf-8")
        self.assertIn("node N_PATH_SELECT", view)
        self.assertIn("reject unless answer in [A, B, C, D]", view)
        ir = json.loads((self.package / "compiled" / "program.ir.json").read_text(encoding="utf-8"))
        self.assertNotIn(ir["security"]["canary_secret"], view)
        self.assertNotIn("N99_CANARY_DO_NOT_EMIT", view)

    def test_verify_targets_detects_tampered_ordo_code_view(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["verify-targets", str(self.package)]), 0)
        view_path = self.package / "compiled" / "program.ordo.view"
        view_path.write_text(view_path.read_text(encoding="utf-8") + "\n# tampered\n", encoding="utf-8")
        self.assertEqual(main(["verify-targets", str(self.package)]), 1)
        report = (self.package / "reports" / "target_verification_report.json").read_text(encoding="utf-8")
        self.assertIn("ORDO-TARGET-007", report)
        self.assertIn("target-set: inconsistent", report)

    def test_next_step_format_ordo_code_adds_current_contract_fragment(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["next-step", str(self.package), "--format", "ordo-code"]), 0)
        report = json.loads((self.package / "reports" / "next_step_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["runtime_view"]["format"], "ordo-code")
        self.assertIn("node N_EVENT_GOAL", report["runtime_view"]["current_contract"])
        self.assertTrue((self.package / "reports" / "runtime_view_report.json").exists())

    def test_runtime_package_includes_targets_and_embedded_cli_verifies_them(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        runtime_zip = self.tmp / "runtime.zip"
        self.assertEqual(main(["validate-release", str(self.package)]), 0)
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--out", str(runtime_zip), "--ci-evidence", str(_write_ci_evidence(self.package))]), 0)
        runtime_pkg = self.tmp / "runtime_pkg"
        shutil.unpack_archive(str(runtime_zip), runtime_pkg)
        root = next(runtime_pkg.iterdir())
        self.assertTrue((root / "compiled" / "program.ir.json").exists())
        self.assertTrue((root / "compiled" / "program.ordo.view").exists())
        self.assertTrue((root / "compiled" / "targets.manifest.json").exists())
        result = subprocess.run([sys.executable, str(root / "cli_embedded" / "ordo"), "verify-targets", str(root)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("target-set: consistent", result.stdout)
        result = subprocess.run([sys.executable, str(root / "cli_embedded" / "ordo"), "render-runtime-view", str(root), "--format", "ordo-code", "--node", "N_PATH_SELECT"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("node N_PATH_SELECT", result.stdout)
        self.assertIn("reject unless answer in [A, B, C, D]", result.stdout)
        result = subprocess.run([sys.executable, str(root / "cli_embedded" / "ordo"), "package", str(root)], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("blocks non-runtime command", result.stderr)


class SessionTraceProofM60_2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_m60_2_trace_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_compile_registers_mutable_session_trace_target(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        trace = self.package / "runtime" / "session.ordo.trace"
        self.assertTrue(trace.exists())
        text = trace.read_text(encoding="utf-8")
        self.assertIn("trace_format: ordo-session-trace.v1", text)
        manifest = json.loads((self.package / "compiled" / "targets.manifest.json").read_text(encoding="utf-8"))
        self.assertIn("session-trace", manifest["targets"])
        self.assertTrue(manifest["targets"]["session-trace"]["mutable"])
        self.assertEqual(main(["verify-targets", str(self.package)]), 0)

    def test_intake_submit_appends_trace_and_links_evidence(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        report = json.loads((self.package / "reports" / "intake_submit_report.json").read_text(encoding="utf-8"))
        trace_meta = report["session_trace"]
        self.assertEqual(trace_meta["path"], "runtime/session.ordo.trace")
        self.assertEqual(trace_meta["step_index"], 1)
        self.assertIn("step 001", trace_meta["trace_fragment"])
        trace_text = (self.package / "runtime" / "session.ordo.trace").read_text(encoding="utf-8")
        self.assertIn("step 001", trace_text)
        self.assertIn("node: N_EVENT_GOAL", trace_text)
        evidence = json.loads((self.package / report["evidence_report"]).read_text(encoding="utf-8"))
        self.assertEqual(evidence["session_trace"]["path"], "runtime/session.ordo.trace")
        self.assertEqual(evidence["session_trace"]["trace_digest"], trace_meta["trace_digest"])

    def test_verify_session_detects_trace_tamper(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        trace = self.package / "runtime" / "session.ordo.trace"
        trace.write_text(trace.read_text(encoding="utf-8").replace("node: N_EVENT_GOAL", "node: N_TAMPERED"), encoding="utf-8")
        self.assertEqual(main(["verify-session", str(self.package)]), 1)
        text = (self.package / "reports" / "session_verification_report.json").read_text(encoding="utf-8")
        self.assertIn("session-trace: broken", text)
        self.assertIn("ORDO-TRACE", text)

    def test_runtime_package_includes_trace_and_embedded_verify_session_checks_it(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        runtime_zip = self.tmp / "runtime.zip"
        self.assertEqual(main(["validate-release", str(self.package)]), 0)
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--out", str(runtime_zip), "--ci-evidence", str(_write_ci_evidence(self.package))]), 0)
        extract = self.tmp / "runtime_extract"
        shutil.unpack_archive(str(runtime_zip), extract)
        root = next(extract.iterdir())
        self.assertTrue((root / "runtime" / "session.ordo.trace").exists())
        result = subprocess.run([sys.executable, str(root / "cli_embedded" / "ordo"), "intake", str(root), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("session-trace:", result.stdout)
        result = subprocess.run([sys.executable, str(root / "cli_embedded" / "ordo"), "verify-session", str(root)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        report = json.loads((root / "reports" / "session_verification_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["session_trace_terminal_line"], "session-trace: intact")
        self.assertEqual(report["session_trace_steps_checked"], 1)

class RuntimePackagingModesM60_3Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_m60_3_modes_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _build_runtime(self, runtime_view: str) -> Path:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        runtime_zip = self.tmp / f"runtime_{runtime_view.replace(',', '_')}.zip"
        self.assertEqual(main(["validate-release", str(self.package)]), 0)
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--runtime-view", runtime_view, "--out", str(runtime_zip), "--ci-evidence", str(_write_ci_evidence(self.package))]), 0)
        extract = self.tmp / f"extract_{runtime_view.replace(',', '_')}"
        shutil.unpack_archive(str(runtime_zip), extract)
        return next(extract.iterdir())

    def test_runtime_view_json_excludes_stale_ordo_code_projection(self) -> None:
        root = self._build_runtime("json")
        self.assertTrue((root / "compiled" / "program.ir.json").exists())
        self.assertTrue((root / "compiled" / "targets.manifest.json").exists())
        self.assertFalse((root / "compiled" / "program.ordo.view").exists())
        manifest = json.loads((root / "compiled" / "targets.manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["runtime_view"], "json")
        self.assertIn("json-ir", manifest["targets"])
        self.assertIn("session-trace", manifest["targets"])
        self.assertNotIn("ordo-code-view", manifest["targets"])
        runtime_manifest = json.loads((root / "ordo.runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(runtime_manifest["runtime_view_behavior"]["default_next_step_format"], "json")
        result = subprocess.run([sys.executable, str(root / "cli_embedded" / "ordo"), "next-step", str(root)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("format=json", result.stdout)
        self.assertNotIn("current_contract:", result.stdout)
        result = subprocess.run([sys.executable, str(root / "cli_embedded" / "ordo"), "render-runtime-view", str(root), "--format", "ordo-code", "--node", "N_EVENT_GOAL"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("render-runtime-view: blocked", result.stdout)

    def test_runtime_view_ordo_code_auto_renders_contract_fragment(self) -> None:
        root = self._build_runtime("ordo-code")
        self.assertTrue((root / "compiled" / "program.ordo.view").exists())
        runtime_manifest = json.loads((root / "ordo.runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(runtime_manifest["runtime_view_behavior"]["default_next_step_format"], "ordo-code")
        result = subprocess.run([sys.executable, str(root / "cli_embedded" / "ordo"), "next-step", str(root)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("format=ordo-code", result.stdout)
        self.assertIn("current_contract:", result.stdout)
        self.assertIn("node N_EVENT_GOAL", result.stdout)
        report = json.loads((root / "reports" / "next_step_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["effective_format"], "ordo-code")
        self.assertEqual(report["runtime_view"]["status"], "generated")

    def test_runtime_view_json_ordo_code_contains_both_modes(self) -> None:
        root = self._build_runtime("json,ordo-code")
        self.assertTrue((root / "compiled" / "program.ir.json").exists())
        self.assertTrue((root / "compiled" / "program.ordo.view").exists())
        runtime_manifest = json.loads((root / "ordo.runtime.json").read_text(encoding="utf-8"))
        self.assertEqual(runtime_manifest["runtime_view"], "json,ordo-code")
        self.assertEqual(runtime_manifest["runtime_view_behavior"]["allowed_cli_formats"], ["json", "ordo-code"])
        result = subprocess.run([sys.executable, str(root / "cli_embedded" / "ordo"), "next-step", str(root), "--format", "json"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("format=json", result.stdout)
        result = subprocess.run([sys.executable, str(root / "cli_embedded" / "ordo"), "next-step", str(root), "--format", "ordo-code"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("format=ordo-code", result.stdout)
        self.assertIn("current_contract:", result.stdout)

class RuntimeCliSafetyM60_3_2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_m60_3_2_safety_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_bare_intake_fails_fast_without_tty_or_answers(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "ordo.cli", "intake", str(self.package)],
            cwd=CLI_ROOT,
            stdin=subprocess.DEVNULL,
            text=True,
            capture_output=True,
            timeout=5,
        )
        self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
        self.assertIn("no_answers_and_not_interactive_and_no_tty", result.stdout)
        report = json.loads((self.package / "reports" / "intake_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["reason"], "no_answers_and_not_interactive_and_no_tty")
        self.assertIn("ORDO-INTAKE-004", (self.package / "reports" / "intake_report.json").read_text(encoding="utf-8"))

    def test_next_step_stdout_keeps_checkpoint_details_in_report_not_stdout(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        result = subprocess.run(
            [sys.executable, "-m", "ordo.cli", "next-step", str(self.package), "--format", "json"],
            cwd=CLI_ROOT,
            text=True,
            capture_output=True,
            timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("next-step:", result.stdout)
        self.assertIn("sha256=", result.stdout)
        self.assertNotIn('"checkpoint"', result.stdout)
        report_text = (self.package / "reports" / "next_step_report.json").read_text(encoding="utf-8")
        self.assertIn('"checkpoint"', report_text)


class RuntimeRestoreSessionM60_4Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_m60_4_restore_test_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_restore_session_appends_proof_without_truncating_history(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_PATH_SELECT", "--answer", "A"]), 0)
        before = sorted((self.package / "runtime" / "state_snapshots").glob("SESSION-*.json"))
        self.assertEqual(len(before), 3)
        self.assertEqual(main(["restore-session", str(self.package), "--to-seq", "1", "--reason", "change path choice"]), 0)
        after = sorted((self.package / "runtime" / "state_snapshots").glob("SESSION-*.json"))
        self.assertEqual(len(after), 4)
        report = json.loads((self.package / "reports" / "restore_session_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["mode"], "m60_4_append_only_restore_session")
        self.assertEqual(report["restore"]["to_seq"], 1)
        self.assertFalse(report["restore"]["history_truncated"])
        self.assertIn("RESTORE_TO_SEQ_001", report["snapshot"])
        self.assertEqual(report["next_node"], "N_PATH_SELECT")
        live = json.loads((self.package / "runtime" / "live_session_state.json").read_text(encoding="utf-8"))
        self.assertEqual(live["current_node"], "N_PATH_SELECT")
        self.assertIn("restore", live)
        trace = (self.package / "runtime" / "session.ordo.trace").read_text(encoding="utf-8")
        self.assertIn("action: restore_session", trace)
        self.assertIn("node: RESTORE_TO_SEQ_001", trace)
        self.assertEqual(main(["verify-session", str(self.package)]), 0)
        verify = json.loads((self.package / "reports" / "session_verification_report.json").read_text(encoding="utf-8"))
        self.assertEqual(verify["session_trace_terminal_line"], "session-trace: intact")
        self.assertEqual(verify["session_trace_steps_checked"], 3)

    def test_restore_session_blocks_unknown_sequence(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        self.assertEqual(main(["restore-session", str(self.package), "--to-seq", "99"]), 1)
        report = json.loads((self.package / "reports" / "restore_session_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "blocked")
        self.assertIn("ORDO-RESTORE-002", (self.package / "reports" / "restore_session_report.json").read_text(encoding="utf-8"))

    def test_embedded_runtime_restore_session_is_allowlisted_and_verifiable(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        runtime_zip = self.tmp / "runtime.zip"
        self.assertEqual(main(["validate-release", str(self.package)]), 0)
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--out", str(runtime_zip), "--ci-evidence", str(_write_ci_evidence(self.package))]), 0)
        extract = self.tmp / "runtime_extract"
        shutil.unpack_archive(str(runtime_zip), extract)
        root = next(extract.iterdir())
        embedded = root / "cli_embedded" / "ordo"
        self.assertTrue(embedded.exists())
        result = subprocess.run([sys.executable, str(embedded), "intake", str(root), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        result = subprocess.run([sys.executable, str(embedded), "intake", str(root), "--submit", "N_PATH_SELECT", "--answer", "A"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        result = subprocess.run([sys.executable, str(embedded), "restore-session", str(root), "--to-seq", "1"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("restore-session: passed", result.stdout)
        self.assertIn("session-trace:", result.stdout)
        result = subprocess.run([sys.executable, str(embedded), "verify-session", str(root)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("session-chain: intact", result.stdout)

class RuntimeBranchAwareLiveCurrentNodeM60_4_1Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_branch_current_test_"))
        self.package = self.tmp / "branch_package"
        (self.package / "source").mkdir(parents=True)
        (self.package / "tests").mkdir()
        (self.package / "output_templates" / "templates").mkdir(parents=True)
        (self.package / "ordo.yml").write_text(
            """
name: branch.test
version: 0.1.0
source: source/program.ordo.yaml
tests: tests/test_cases.yaml
compiled: compiled/program.ir.json
reports: reports
""".strip() + "\n",
            encoding="utf-8",
        )
        (self.package / "tests" / "test_cases.yaml").write_text("test_cases: []\n", encoding="utf-8")
        (self.package / "output_templates" / "output_templates.yaml").write_text("output_templates: []\n", encoding="utf-8")
        shutil.copy2(WORKSPACE / "packages" / "history_event_guided_intake" / "START_HERE_RUNTIME_MODE.md", self.package / "START_HERE_RUNTIME_MODE.md")
        shutil.copy2(WORKSPACE / "packages" / "history_event_guided_intake" / "START_PROMPT_RUNTIME_MODE.md", self.package / "START_PROMPT_RUNTIME_MODE.md")
        shutil.copy2(WORKSPACE / "packages" / "history_event_guided_intake" / "README.md", self.package / "README.md")
        (self.package / "reports").mkdir()
        (self.package / "reports" / "CLI_VALIDATION_SUMMARY.md").write_text("# CLI validation summary\n\nCLI status: not_run_cli_unavailable\n", encoding="utf-8")
        (self.package / "source" / "program.ordo.yaml").write_text(
            """
ordo:
  version: "0.12"
  package: branch.test
  control_level: standard
  execution_mode: chat_internal
intent:
  id: INTENT_BRANCH_TEST
  description: Branch current-node test.
contract:
  id: CONTRACT_BRANCH_TEST
  required: [path_complete]
state:
  id: STATE_BRANCH_TEST
  schema:
    selected_path: null
    step_1: null
    node_1: null
    path_complete: false
nodes:
  - id: A_START
    question: Choose branch.
    answer_type: single_select
    allow_unmatched_input: true
    allowed_answers: [left, right]
    on_answer:
      left:
        update_state:
          selected_path: $answer
        next: B_LEFT
      right:
        update_state:
          selected_path: $answer
        next: B_RIGHT
  - id: B_LEFT
    question: Left branch.
    answer_type: single_select
    allow_unmatched_input: true
    allowed_answers: [finish]
    on_answer:
      finish:
        update_state:
          step_1: $answer
          node_1: B_LEFT
          path_complete: true
        next: G_DONE
  - id: B_RIGHT
    question: Right branch.
    answer_type: single_select
    allow_unmatched_input: true
    allowed_answers: [finish]
    on_answer:
      finish:
        update_state:
          step_1: $answer
          node_1: B_RIGHT
          path_complete: true
        next: G_DONE
gates:
  - id: G_DONE
    method: mechanical
    trust_class: deterministic
    condition: state.path_complete is true
    on_fail: block
assertions: []
outputs: []
graph_contract:
  entry_node: A_START
  external_terminal_targets:
    - G_DONE
""".strip() + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_incomplete_branch_fixture_is_blocked_by_green_release_gate(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["validate-release", str(self.package)]), 1)
        runtime_zip = self.tmp / "runtime.zip"
        self.assertEqual(main(["package", str(self.package), "--profile", "runtime", "--runtime-view", "ordo-code", "--out", str(runtime_zip), "--ci-evidence", str(_write_ci_evidence(self.package))]), 1)
        self.assertFalse(runtime_zip.exists())


class CleanCheckCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_clean_check_test_"))
        self.package = self.tmp / "clean_package"
        (self.package / "source").mkdir(parents=True)
        (self.package / "tests").mkdir(parents=True)
        (self.package / "reports").mkdir(parents=True)
        (self.package / "source" / "program.ordo.yaml").write_text("name: clean.example\nnodes: []\n", encoding="utf-8")
        (self.package / "tests" / "test_cases.yaml").write_text("tests: []\n", encoding="utf-8")
        (self.package / "ordo.yml").write_text(
            "name: clean.example\nversion: '0.1'\nsource: source/program.ordo.yaml\ntests: tests/test_cases.yaml\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_clean_check_passes_minimal_package(self) -> None:
        self.assertEqual(main(["clean-check", str(self.package)]), 0)
        report = json.loads((self.package / "reports" / "clean_check_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "passed")
        self.assertIn("source_yaml_parse", {item["check_id"] for item in report["checks"]})

    def test_clean_check_blocks_missing_source_yaml(self) -> None:
        (self.package / "source" / "program.ordo.yaml").unlink()
        self.assertEqual(main(["clean-check", str(self.package)]), 1)
        report = json.loads((self.package / "reports" / "clean_check_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "blocked")
        self.assertIn("source_yaml_exists", {item["check_id"] for item in report["errors"]})

    def test_clean_check_json_output_and_fail_on_warning(self) -> None:
        (self.package / "tests" / "test_cases.yaml").unlink()
        self.assertEqual(main(["clean-check", str(self.package), "--profile", "light", "--json"]), 0)
        self.assertEqual(main(["clean-check", str(self.package), "--profile", "light", "--fail-on-warning"]), 1)
        report = json.loads((self.package / "reports" / "clean_check_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "passed_with_warnings")
