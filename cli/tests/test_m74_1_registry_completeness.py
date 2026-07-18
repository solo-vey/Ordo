from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from ordo.cli import main
from ordo.registry_checks import find_repo_root, validate_capability_registry


WORKSPACE = Path(__file__).resolve().parents[2]
EXAMPLE = WORKSPACE / "packages" / "ordo_project_builder"


class RegistryCompletenessM741Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_m74_1_"))
        self.package = self.tmp / "ordo_project_builder"
        shutil.copytree(EXAMPLE, self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _source(self) -> tuple[Path, dict]:
        path = self.package / "source" / "program.ordo.yaml"
        return path, yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_capability_registry_cross_references_pass(self) -> None:
        report = validate_capability_registry(find_repo_root(WORKSPACE))
        self.assertEqual(report["status"], "passed", report)
        self.assertIn("conversation_scope_guard", report["capabilities"])

    def test_unknown_top_level_source_construct_is_blocking(self) -> None:
        path, data = self._source()
        data["unregistered_future_construct"] = {"enabled": True}
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        self.assertEqual(main(["lint", str(self.package)]), 1)
        report = json.loads((self.package / "reports" / "lint_report.json").read_text())
        self.assertTrue(any(i["code"] == "SOURCE_CONSTRUCT_NOT_IN_REGISTRY" for i in report["issues"]))

    def test_invalid_csg_mode_is_rejected(self) -> None:
        path, data = self._source()
        data["conversation_scope_guard"] = {"supported": True, "enabled": True, "mode": "totally_invalid_mode", "state_change_on_out_of_scope": False}
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        self.assertEqual(main(["lint", str(self.package)]), 1)
        report = json.loads((self.package / "reports" / "lint_report.json").read_text())
        self.assertTrue(any(i["code"] == "CSG_MODE_INVALID" for i in report["issues"]))

    def test_valid_csg_compiles_to_registered_ir_opcode(self) -> None:
        path, data = self._source()
        data["conversation_scope_guard"] = {
            "supported": True,
            "enabled": True,
            "mode": "guided_redirect",
            "state_change_on_out_of_scope": False,
            "escalation": {"counter_scope": "active_node", "reset_on": ["valid_process_answer", "node_transition", "process_resume"]},
        }
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        self.assertEqual(main(["lint", str(self.package)]), 0)
        self.assertEqual(main(["compile", str(self.package)]), 0)
        ir = json.loads((self.package / "compiled" / "program.ir.json").read_text())
        csg = [op for op in ir["ops"] if op.get("op") == "CONVERSATION.SCOPE.DEF"]
        self.assertEqual(len(csg), 1)
        self.assertEqual(csg[0]["mode"], "guided_redirect")
        compile_report = json.loads((self.package / "reports" / "compile_report.json").read_text())
        self.assertEqual(compile_report["opcode_registry_check"]["status"], "passed")
        self.assertEqual(compile_report["capability_registry_check"]["status"], "passed")


if __name__ == "__main__":
    unittest.main()
