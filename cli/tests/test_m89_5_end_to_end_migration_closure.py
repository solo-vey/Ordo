from __future__ import annotations
import copy, json, sys, tempfile, unittest
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"language/migration"))

from end_to_end_migration import (
    migrate_source, segment_clauses, classify_clause, write_package
)
from bl_ordo_021_closure_gate import evaluate_closure

class TestM895EndToEndMigration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_path = ROOT/"language/migration/fixtures/legacy_all_in_one_instruction.md"
        cls.source = cls.source_path.read_text(encoding="utf-8")
        cls.package = migrate_source(cls.source, cls.source_path.name)
        cls.schema = json.loads(
            (ROOT/"language/schemas/process_instruction_migration_package.schema.json")
            .read_text(encoding="utf-8")
        )

    def test_segments_ten_clauses(self):
        self.assertEqual(len(segment_clauses(self.source)), 10)

    def test_classifies_authorization_clause(self):
        clause = classify_clause({
            "clause_id": "C-0001",
            "text": "Obtain explicit authorization before mutation.",
            "normativity": "normative",
            "mandatory": True,
        })
        self.assertIn("authorization", clause["semantic_classes"])
        self.assertIn("gate", clause["semantic_classes"])

    def test_package_schema_passes(self):
        errors = list(Draft202012Validator(self.schema).iter_errors(self.package))
        self.assertEqual(errors, [])

    def test_source_hash_is_bound(self):
        self.assertEqual(len(self.package["source"]["source_sha256"]), 64)

    def test_every_clause_has_full_traceability(self):
        rows = self.package["traceability_matrix"]["rows"]
        self.assertEqual(len(rows), 10)
        self.assertTrue(all(r["coverage_status"] == "full" for r in rows))

    def test_every_unit_has_mapping(self):
        nodes = self.package["dependency_graph"]["nodes"]
        entries = self.package["ordo_mapping"]["entries"]
        self.assertEqual({n["node_id"] for n in nodes}, {e["unit_id"] for e in entries})

    def test_authorization_edge_exists(self):
        relations = {e["relation"] for e in self.package["dependency_graph"]["edges"]}
        self.assertIn("authorizes", relations)

    def test_migration_gate_passes(self):
        self.assertEqual(self.package["gate_report"]["status"], "passed")
        self.assertEqual(self.package["gate_report"]["summary"]["blocking_finding_count"], 0)

    def test_playbook_is_materialized(self):
        playbook = self.package["playbook"]
        self.assertTrue(playbook["nodes"])
        self.assertTrue(playbook["edges"])
        self.assertEqual(playbook["status"], "migration_validated")

    def test_write_package_materializes_expected_files(self):
        with tempfile.TemporaryDirectory() as td:
            output = write_package(self.package, td)
            expected = {
                "migration_package.json",
                "clause_inventory.json",
                "dependency_graph.json",
                "ordo_mapping.json",
                "traceability_matrix.json",
                "migration_gate_report.json",
                "migrated_playbook.json",
                "SHA256SUMS.txt",
            }
            self.assertEqual({p.name for p in output.iterdir()}, expected)

    def test_closure_gate_passes(self):
        result = evaluate_closure(
            self.package,
            regression_passed=True,
            package_materialized=True,
        )
        self.assertEqual(result["status"], "passed")

    def test_closure_blocks_incomplete_traceability(self):
        package = copy.deepcopy(self.package)
        package["traceability_matrix"]["rows"] = package["traceability_matrix"]["rows"][:-1]
        result = evaluate_closure(package, regression_passed=True, package_materialized=True)
        self.assertIn("MIG-CLOSE-004", {i["code"] for i in result["issues"]})

    def test_closure_blocks_failed_loss_gate(self):
        package = copy.deepcopy(self.package)
        package["gate_report"]["status"] = "blocked"
        result = evaluate_closure(package, regression_passed=True, package_materialized=True)
        self.assertIn("MIG-CLOSE-005", {i["code"] for i in result["issues"]})

    def test_closure_blocks_failed_regression(self):
        result = evaluate_closure(
            self.package,
            regression_passed=False,
            package_materialized=True,
        )
        self.assertIn("MIG-CLOSE-007", {i["code"] for i in result["issues"]})

if __name__ == "__main__":
    unittest.main()
