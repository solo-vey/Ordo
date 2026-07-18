from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]

class M712PromptRegistrySchemaProfileTests(unittest.TestCase):
    def test_registry_schema_requires_identity_fields(self):
        data = yaml.safe_load((ROOT / "language/schemas/prompt_registry_schema.yaml").read_text())
        required = set(data["properties"]["prompts"]["items"]["required"])
        self.assertTrue({"prompt_id", "prompt_family", "version"}.issubset(required))

    def test_prompt_id_pattern_accepts_semantic_id(self):
        data = yaml.safe_load((ROOT / "language/schemas/prompt_registry_schema.yaml").read_text())
        pattern = data["properties"]["prompts"]["items"]["properties"]["prompt_id"]["pattern"]
        self.assertRegex("hp.delta_intake.single_field.v1", re.compile(pattern))
        self.assertNotRegex("B1_N2B_helper", re.compile(pattern))

    def test_controlled_application_phases_are_exact(self):
        data = yaml.safe_load((ROOT / "language/schemas/prompt_registry_validation_profile_schema.yaml").read_text())
        phases = data["prompt_registry_validation_profile"]["controlled_application_phases"]
        self.assertEqual(phases, [
            "before_question", "during_clarification", "after_answer",
            "before_confirmation", "on_open_gap", "on_gate_fail",
            "before_artifact_generation",
        ])

    def test_identity_and_lineage_policy_present(self):
        data = yaml.safe_load((ROOT / "language/schemas/prompt_registry_validation_profile_schema.yaml").read_text())
        policy = data["prompt_registry_validation_profile"]["identity_policy"]
        for key in (
            "prompt_family_required", "version_required", "node_independence_required",
            "semantic_filename_required", "stable_id_immutable",
            "supersedes_same_family_only", "supersedes_lower_version_only",
            "supersedes_lineage_acyclic",
        ):
            self.assertTrue(policy[key])

    def test_attachment_authority_boundary(self):
        data = yaml.safe_load((ROOT / "language/schemas/prompt_registry_validation_profile_schema.yaml").read_text())
        policy = data["prompt_registry_validation_profile"]["attachment_policy"]
        self.assertEqual(policy["authoritative_source"], "node_or_artifact_prompt_refs")
        self.assertFalse(policy["prompt_may_change_navigation"] )

    def test_example_parses_and_uses_standard_profile(self):
        data = yaml.safe_load((ROOT / "language/examples/source/prompt_registry_validation_profile_example.ordo.yaml").read_text())
        profile = data["prompt_registry_validation_profile"]
        self.assertEqual(profile["selected_profile"], "standard")
        check_ids = {c["check_id"] for c in profile["checks"]}
        self.assertIn("prompt_ids_semantic_and_node_independent", check_ids)
        self.assertIn("prompt_ref_application_phase_valid", check_ids)

if __name__ == "__main__":
    unittest.main()
