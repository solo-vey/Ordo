from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from ordo.cli import main


WORKSPACE = Path(__file__).resolve().parents[2]


class RuntimeContextSeparationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_bl108_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_live_session_separates_business_state_from_runtime_context(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        live = json.loads((self.package / "runtime" / "live_session_state.json").read_text(encoding="utf-8"))
        self.assertEqual(live["format"], "ordo-runtime-session.v1")
        self.assertEqual(live["business_state"]["event_goal"], "Зміна капіталу")
        self.assertNotIn("current_node", live["business_state"])
        self.assertEqual(live["runtime_context"]["current_node"], "N_PATH_SELECT")
        self.assertEqual(live["runtime_context"]["source_binding"]["compiled_ir"]["path"], "compiled/program.ir.json")

    def test_stale_compiled_binding_blocks_automatic_resume(self) -> None:
        self.assertEqual(main(["compile", str(self.package)]), 0)
        self.assertEqual(main(["intake", str(self.package), "--submit", "N_EVENT_GOAL", "--answer", "Зміна капіталу"]), 0)
        compiled = self.package / "compiled" / "program.ir.json"
        compiled.write_text(compiled.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.assertEqual(main(["next-step", str(self.package)]), 1)
        report = json.loads((self.package / "reports" / "next_step_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "blocked")
        self.assertIn("ORDO-RUNTIME-CONTEXT-003", json.dumps(report, ensure_ascii=False))
