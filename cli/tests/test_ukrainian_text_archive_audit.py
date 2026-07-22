from __future__ import annotations

import importlib.util
import io
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/audit_ukrainian_text.py"
spec = importlib.util.spec_from_file_location("ukrainian_audit", SCRIPT)
audit_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(audit_module)


class UkrainianTextArchiveAuditTests(unittest.TestCase):
    def limits(self) -> object:
        return audit_module.Limits(4, 100, 1_000_000, 5_000_000)

    def test_detects_plain_zip_and_nested_tar_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "plain.md").write_text("English only\n", encoding="utf-8")
            tar_buffer = io.BytesIO()
            with tarfile.open(fileobj=tar_buffer, mode="w") as archive:
                content = "Український текст\n".encode("utf-8")
                info = tarfile.TarInfo("nested.txt")
                info.size = len(content)
                archive.addfile(info, io.BytesIO(content))
            with zipfile.ZipFile(root / "payload.zip", "w") as archive:
                archive.writestr("inner.tar", tar_buffer.getvalue())

            result = audit_module.audit(root, filesystem=True, exclusions=(), limits=self.limits(), sample_limit=2)

        self.assertEqual(result["status"], "findings")
        self.assertEqual(result["finding_count"], 1)
        finding = result["findings"][0]
        self.assertEqual(finding["source_path"], "payload.zip")
        self.assertEqual(finding["member_path"], "inner.tar!/nested.txt")
        self.assertEqual(finding["samples"], ["Український текст"])

    def test_excludes_book_contour_but_not_other_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "book").mkdir()
            (root / "book" / "uk.md").write_text("Український текст\n", encoding="utf-8")
            (root / "docs.md").write_text("Український текст\n", encoding="utf-8")

            result = audit_module.audit(root, filesystem=True, exclusions=("book/**",), limits=self.limits(), sample_limit=2)

        self.assertEqual(result["excluded_file_count"], 1)
        self.assertEqual(result["finding_count"], 1)
        self.assertEqual(result["findings"][0]["source_path"], "docs.md")

    def test_archive_limits_report_warning_without_extracting_to_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with zipfile.ZipFile(root / "large.zip", "w") as archive:
                archive.writestr("large.txt", "x" * 50)

            result = audit_module.audit(
                root,
                filesystem=True,
                exclusions=(),
                limits=audit_module.Limits(4, 100, 10, 100),
                sample_limit=2,
            )

        self.assertEqual(result["finding_count"], 0)
        self.assertEqual(result["warning_count"], 1)
        self.assertIn("member too large", result["warnings"][0]["warning"])


if __name__ == "__main__":
    unittest.main()
