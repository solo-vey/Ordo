from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from ordo.build_identity import new_build_identity, bind_report
from ordo.package_reconciliation import pre_zip_reconciliation


class TestM854PostValidationMutationBlocking(unittest.TestCase):
    def _prepare(self, root: Path):
        source = root / "source.txt"
        compiled = root / "compiled" / "program.ir.json"
        compiled.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("source-v1", encoding="utf-8")
        compiled.write_text('{"version": 1}', encoding="utf-8")

        checksums = root / "SHA256SUMS.txt"
        checksums.write_text(
            f"{hashlib.sha256(source.read_bytes()).hexdigest()}  source.txt\n"
            f"{hashlib.sha256(compiled.read_bytes()).hexdigest()}  compiled/program.ir.json\n",
            encoding="utf-8",
        )

        manifest = root / "BUILD_MANIFEST.json"
        manifest.write_text(json.dumps({
            "files": [
                {"path": "source.txt", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
                {"path": "compiled/program.ir.json", "sha256": hashlib.sha256(compiled.read_bytes()).hexdigest()},
            ]
        }), encoding="utf-8")

        identity = new_build_identity(root, build_session_id="build-1")
        report = root / "reports" / "release_validation_report.json"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(bind_report({"status": "passed"}, identity)), encoding="utf-8")
        return source, compiled, checksums, manifest, identity, report

    def _assert_blocked(self, root, identity, report, checksums, manifest, expected_codes):
        result = pre_zip_reconciliation(
            root,
            identity,
            [report],
            checksum_manifest=checksums,
            build_manifest=manifest,
        )
        self.assertEqual(result["status"], "failed")
        codes = {item["code"] for item in result["issues"]}
        self.assertTrue(codes.intersection(expected_codes), codes)

    def test_source_mutation_after_validation_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, compiled, checksums, manifest, identity, report = self._prepare(root)
            source.write_text("source-v2", encoding="utf-8")
            self._assert_blocked(root, identity, report, checksums, manifest, {"ORDO-RECON-010", "ORDO-RECON-004", "ORDO-RECON-009"})

    def test_compiled_output_mutation_after_validation_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, compiled, checksums, manifest, identity, report = self._prepare(root)
            compiled.write_text('{"version": 2}', encoding="utf-8")
            self._assert_blocked(root, identity, report, checksums, manifest, {"ORDO-RECON-010", "ORDO-RECON-004", "ORDO-RECON-009"})

    def test_checksum_manifest_mutation_after_validation_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, compiled, checksums, manifest, identity, report = self._prepare(root)
            checksums.write_text("0" * 64 + "  source.txt\n", encoding="utf-8")
            self._assert_blocked(root, identity, report, checksums, manifest, {"ORDO-RECON-004"})

    def test_build_manifest_mutation_after_validation_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, compiled, checksums, manifest, identity, report = self._prepare(root)
            manifest.write_text(json.dumps({
                "files": [{"path": "source.txt", "sha256": "0" * 64}]
            }), encoding="utf-8")
            self._assert_blocked(root, identity, report, checksums, manifest, {"ORDO-RECON-009"})

    def test_validation_report_rebinding_attempt_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, compiled, checksums, manifest, identity, report = self._prepare(root)
            payload = json.loads(report.read_text(encoding="utf-8"))
            payload["build_identity"]["build_session_id"] = "other-build"
            report.write_text(json.dumps(payload), encoding="utf-8")
            self._assert_blocked(root, identity, report, checksums, manifest, {"ORDO-BUILD-001"})

    def test_missing_compiled_output_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, compiled, checksums, manifest, identity, report = self._prepare(root)
            compiled.unlink()
            self._assert_blocked(root, identity, report, checksums, manifest, {"ORDO-RECON-003", "ORDO-RECON-008", "ORDO-RECON-010"})


if __name__ == "__main__":
    unittest.main()
