from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from ordo.release import validate_release
from ordo.package_profiles import build_package_profile

WORKSPACE = Path(__file__).resolve().parents[2]


class MandatoryGreenReleaseGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_m84_2_"))
        self.package = self.tmp / "history_event_guided_intake"
        shutil.copytree(WORKSPACE / "packages" / "history_event_guided_intake", self.package)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_failed_release_validation_does_not_create_archive(self) -> None:
        source = self.package / "source" / "program.ordo.yaml"
        source.write_text(source.read_text(encoding="utf-8") + "\n  BROKEN_TARGET_FOR_M84: missing\n", encoding="utf-8")
        out = self.tmp / "blocked.zip"
        report = validate_release(self.package, out=out, skip_runtime=True)
        self.assertEqual(report["status"], "failed")
        self.assertFalse(out.exists())
        package_step = next(step for step in report["steps"] if step["name"] == "package")
        self.assertEqual(package_step["status"], "blocked")
        self.assertIsNone(report["release_archive"])

    def test_profile_packaging_requires_green_release_report(self) -> None:
        out = self.tmp / "blocked-profile.zip"
        report = build_package_profile(self.package, profile="dev", out=out)
        self.assertEqual(report["status"], "failed")
        self.assertFalse(out.exists())
        self.assertIn("ORDO-PACKAGE-014", {issue["code"] for issue in report["issues"]})

    def test_green_release_creates_archive(self) -> None:
        out = self.tmp / "green.zip"
        with patch("ordo.release.validate_output", return_value={"status": "passed", "summary": {}}):
            report = validate_release(self.package, out=out, skip_runtime=True)
        self.assertEqual(report["status"], "passed")
        self.assertTrue(out.exists())
        package_step = next(step for step in report["steps"] if step["name"] == "package")
        self.assertEqual(package_step["status"], "created")


if __name__ == "__main__":
    unittest.main()
