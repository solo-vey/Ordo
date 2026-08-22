import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
EDITOR = HERE.parent / 'editor_service.py'
spec = importlib.util.spec_from_file_location('ordo_editor_service_regression', EDITOR)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def load_fixture(name):
    return json.loads((HERE / 'fixtures' / name).read_text(encoding='utf-8'))


class GenericExecutorRegressionTests(unittest.TestCase):
    def test_real_debug_source_collection_human_and_deterministic_variants(self):
        f = load_fixture('real_source_collection_decision.json')
        producer = f['producer']
        history = [{'role': 'analyst', 'text': f['analyst_input'], 'node_id': producer['id']}]
        for gate_key in ('gate_human_variant', 'gate_deterministic_variant'):
            with self.subTest(gate_variant=gate_key):
                gate = f[gate_key]
                source = {'nodes': [producer], 'gates': [gate]}
                routes = mod._live_routes(gate, 'gate')
                route, evidence = mod._inherited_human_gate_route(source, gate, gate['id'], routes, history)
                self.assertIsNotNone(route)
                self.assertEqual(route['key'], f['expected_route'])
                self.assertEqual(route['target'], f['expected_next'])
                self.assertEqual(evidence['previous_route_target'], gate['id'])
                # The generic fix must not invent a state value based on the required-input name.
                self.assertEqual(evidence['inherited_state_updates'], {})

    def test_missing_required_input_is_unresolved_not_fail(self):
        gate = {
            'id': 'GENERIC_DETERMINISTIC_GATE',
            'method': 'deterministic',
            'trust_class': 'deterministic',
            'required_inputs': ['totally_arbitrary_input_name'],
            'on_pass': 'NEXT', 'on_fail': 'RETRY',
        }
        status, reason, extra = mod._deterministic_gate_decision(gate, {})
        self.assertEqual(status, 'unresolved')
        self.assertIn('totally_arbitrary_input_name', reason)
        self.assertEqual(extra['missing_required_inputs'], ['totally_arbitrary_input_name'])

    def test_false_is_present_not_missing(self):
        gate = {
            'id': 'GENERIC_DETERMINISTIC_GATE',
            'method': 'deterministic',
            'trust_class': 'deterministic',
            'required_inputs': ['decision.value'],
        }
        status, reason, _ = mod._deterministic_gate_decision(gate, {'decision': {'value': False}})
        self.assertNotEqual(status, 'unresolved')
        self.assertEqual(status, 'pass')

    def test_real_debug_bare_confirmation_preserves_full_proposal_schema(self):
        f = load_fixture('real_attribute_confirmation.json')
        record = {
            'id': 'ANY_PROPOSAL_NODE',
            'answer_type': 'table_confirmation_or_correction',
            'on_answer': {
                'normalize': {'mapping.rows': 'AI.NORMALIZE_CONFIRMED_RELEVANT_FIELD_ROWS($answer)'},
                'update_state': {'mapping.rows': '$normalized.mapping.rows'},
                'next': 'VALIDATION_GATE',
            },
        }
        routes = [{'key': 'next', 'target': 'VALIDATION_GATE'}]
        history = [{'role': 'assistant', 'text': f['assistant_proposal'], 'node_id': record['id']}]
        result = mod._proposal_confirmation_result(record, record['id'], f['analyst_input'], history, f['state'], routes)
        self.assertIsNotNone(result)
        rows, selected, _ = result
        self.assertTrue(rows)
        self.assertEqual(selected['target'], 'VALIDATION_GATE')
        for row in rows:
            for col in f['expected_required_columns']:
                self.assertIn(col, row)
            self.assertTrue(row['confirmed'])

    def test_real_debug_correction_preserves_structured_proposal_schema(self):
        f = load_fixture('real_attribute_correction_schema_loss.json')
        record = {
            'id': 'GENERIC_TABLE_REVIEW',
            'answer_type': 'table_confirmation_or_correction',
            'on_answer': {
                'normalize': {'mapping.rows': 'AI.NORMALIZE_CONFIRMED_RELEVANT_FIELD_ROWS($answer)'},
                'update_state': {'mapping.rows': '$normalized.mapping.rows'},
                'next': 'VALIDATION_GATE',
            },
        }
        history = [{'role': 'assistant', 'text': f['assistant_proposal'], 'node_id': record['id']}]
        updates, audit = mod._reconcile_structured_proposal_updates(
            record, record['id'], f['analyst_input'], history, f['state'], f['model_updates']
        )
        self.assertIsNotNone(audit)
        self.assertEqual(audit['mode'], 'schema-preserving-reconciliation')
        rows = updates['source_attribute_mapping.rows']
        self.assertEqual(len(rows), 2)
        for row in rows:
            for col in f['expected_columns']:
                self.assertIn(col, row)
                self.assertNotIn(row[col], (None, ''))
            self.assertTrue(row['confirmed'])
        self.assertEqual(rows[0]['field_path'], 'statusCode')
        self.assertEqual(rows[0]['field_type'], 'string')
        self.assertEqual(rows[0]['field_role'], 'Trigger')
        self.assertEqual(rows[0]['module'], 'company-profile')
        self.assertEqual(rows[0]['data_type'], 'companyProfile')

    def test_proposal_context_is_detected_without_specific_element_id(self):
        record = {
            'id': 'WHATEVER',
            'answer_type': 'structured_confirmation_or_correction',
            'on_answer': {'next': 'NEXT'}
        }
        self.assertTrue(mod._looks_like_proposal_confirmation_record(record))

    def test_unrelated_free_text_node_does_not_reconcile_table_schema(self):
        record = {'id': 'FREE_TEXT', 'answer_type': 'text', 'on_answer': {'next': 'NEXT'}}
        proposal = '| a | b |\n|---|---|\n|1|2|'
        history = [{'role':'assistant','text':proposal,'node_id':'FREE_TEXT'}]
        updates = {'rows': [{'x': 1}]}
        out, audit = mod._reconcile_structured_proposal_updates(record, 'FREE_TEXT', 'ok', history, {}, updates)
        self.assertEqual(out, updates)
        self.assertIsNone(audit)

    def test_canonical_draft_columns_are_authoritative_even_if_markdown_is_sparse(self):
        record = {
            'id': 'TABLE_NODE',
            'answer_type': 'table_confirmation_or_correction',
            'draft_generation': {'columns': ['source_field','target_field','transformation','basic_fallback']},
            'on_answer': {'update_state': {'output_payload_mapping.rows': '$normalized.rows'}, 'next':'GATE'}
        }
        history=[{'role':'assistant','text':'| source_field | target_field |\n|---|---|\n| a | b |','node_id':'TABLE_NODE'}]
        updates={'output_payload_mapping.rows':[{'source_field':'a','target_field':'b','transformation':'direct','basic_fallback':'null'}]}
        out,audit=mod._reconcile_structured_proposal_updates(record,'TABLE_NODE','підтверджую',history,{},updates)
        self.assertEqual(audit['proposal_contract']['columns'], ['source_field','target_field','transformation','basic_fallback'])
        self.assertEqual(out, updates)

    def test_structured_object_correction_deep_merges_existing_state(self):
        record={
            'id':'ALGORITHM_NODE',
            'answer_type':'text_confirmation_or_correction',
            'draft_generation': {'required_coverage':['positive condition','negative condition','null behavior']},
            'on_answer': {'update_state': {'trigger_logic':'$normalized.trigger_logic'}, 'next':'GATE'}
        }
        history=[{'role':'assistant','text':'Draft algorithm with positive, negative and null behavior.','node_id':'ALGORITHM_NODE'}]
        state={'trigger_logic': {'positive':'x == closed','negative':'otherwise','null_behavior':'absent'}}
        updates={'trigger_logic': {'positive':'statusCode == closed'}}
        out,audit=mod._reconcile_structured_proposal_updates(record,'ALGORITHM_NODE','коригую тільки позитивну умову',history,state,updates)
        self.assertEqual(out['trigger_logic']['positive'],'statusCode == closed')
        self.assertEqual(out['trigger_logic']['negative'],'otherwise')
        self.assertEqual(out['trigger_logic']['null_behavior'],'absent')
        self.assertIn('trigger_logic',audit['merged_targets'])

    def test_real_debug_completed_respond_cannot_invent_another_analyst_turn(self):
        f = load_fixture('real_completed_respond_orchestration.json')
        record = f['record']
        routes = mod._live_routes(record, 'node')
        await_analyst, selected, reason = mod._resolve_respond_orchestration(
            record, 'node', 'respond', routes, f['model_result']
        )
        self.assertFalse(await_analyst)
        self.assertIsNotNone(selected)
        self.assertEqual(selected['key'], f['expected']['route_key'])
        self.assertEqual(selected['target'], f['expected']['next_id'])
        self.assertEqual(reason, 'allowed-route-overrides-model-await')

    def test_canonical_complete_updates_force_fixed_next_even_without_model_route(self):
        f = load_fixture('real_completed_respond_orchestration.json')
        record = f['record']
        routes = mod._live_routes(record, 'node')
        model_result = dict(f['model_result'])
        model_result['route_key'] = None
        await_analyst, selected, reason = mod._resolve_respond_orchestration(
            record, 'node', 'respond', routes, model_result
        )
        self.assertFalse(await_analyst)
        self.assertEqual(selected['target'], f['expected']['next_id'])
        self.assertEqual(reason, 'canonical-on-answer-complete')

    def test_partial_updates_may_still_wait_for_clarification(self):
        f = load_fixture('real_completed_respond_orchestration.json')
        record = f['record']
        routes = mod._live_routes(record, 'node')
        model_result = dict(f['model_result'])
        model_result['route_key'] = None
        model_result['state_updates'] = {'source_data_definition.rows': f['model_result']['state_updates']['source_data_definition.rows']}
        await_analyst, selected, reason = mod._resolve_respond_orchestration(
            record, 'node', 'respond', routes, model_result
        )
        self.assertTrue(await_analyst)
        self.assertIsNone(selected)
        self.assertIsNone(reason)

    def test_real_client_mapping_retry_uses_existing_owned_output(self):
        f = load_fixture('real_client_value_retry_continuity.json')
        existing = mod._existing_structured_outputs_for_record(f['record'], f['state'])
        self.assertIn('output_payload_mapping.rows', existing)
        self.assertEqual(existing['output_payload_mapping.rows'], f['state']['output_payload_mapping']['rows'])
        # The retry base must be the analyst-confirmed output, not a fresh upstream draft.
        self.assertEqual(existing['output_payload_mapping.rows'][0]['target_field'], 'values.companyTypeUA')

    def test_real_client_mapping_source_field_namespace_is_canonicalized(self):
        f = load_fixture('real_client_value_retry_continuity.json')
        updates, audit = mod._canonicalize_confirmed_source_references(f['state'], f['regenerated_model_updates'])
        self.assertIsNotNone(audit)
        rows = updates['output_payload_mapping.rows']
        self.assertEqual(rows[0]['source_field'], 'statusCode')
        self.assertEqual(rows[1]['source_field'], 'termination.date')
        self.assertEqual(rows[2]['source_field'], 'companyType.isIndividualInterprener')

    def test_source_reference_canonicalization_preserves_unmatched_pseudo_sources(self):
        state = {'source_attribute_mapping': {'rows': [{'field_path':'statusCode','analyst_status':'Confirmed'}]}}
        updates = {'mapping.rows': [
            {'source_field':'static','target_field':'aliasRisk'},
            {'source_field':'system','target_field':'calculationDate'},
            {'source_field':'algorithm','target_field':'riskFound'}
        ]}
        out, audit = mod._canonicalize_confirmed_source_references(state, updates)
        self.assertIsNone(audit)
        self.assertEqual(out, updates)

    def test_unrelated_deterministic_gate_does_not_inherit_branch(self):
        producer = {
            'id': 'DECISION_A', 'answer_type': 'enum', 'allowed_values': ['yes', 'no'],
            'on_answer': {'branch': {'no': {'next': 'GATE_B'}, 'yes': {'next': 'OTHER'}}},
        }
        gate = {
            'id': 'GATE_B', 'method': 'deterministic', 'trust_class': 'deterministic',
            'required_inputs': ['document.sha256'],
            'condition': 'document checksum must match the expected checksum',
            'on_pass': 'NEXT', 'on_fail': 'RETRY',
        }
        source = {'nodes': [producer], 'gates': [gate]}
        routes = mod._live_routes(gate, 'gate')
        route, evidence = mod._inherited_human_gate_route(source, gate, gate['id'], routes, [{'role':'analyst','text':'no','node_id':'DECISION_A'}])
        self.assertIsNone(route)
        self.assertIsNone(evidence)
        status, _, _ = mod._deterministic_gate_decision(gate, {})
        self.assertEqual(status, 'unresolved')


    def test_compiled_rejection_yaml_fallback_preserves_full_canonical_state(self):
        state = {
            'risk_factor_identity': {'alias': 'EXAMPLE'},
            'business_meaning': 'meaning',
            'source_attribute_mapping.rows': [{'field_path': 'statusCode'}],
            'functional_test_catalog': {'rows': [{'scenario_class': 'positive'}]},
        }
        projected = mod._fallback_runtime_state(state)
        self.assertEqual(projected['risk_factor_identity']['alias'], 'EXAMPLE')
        self.assertEqual(projected['business_meaning'], 'meaning')
        self.assertEqual(projected['source_attribute_mapping']['rows'][0]['field_path'], 'statusCode')
        self.assertIn('functional_test_catalog', projected)

    def test_compiled_state_defaults_fill_absent_paths_without_overwriting_runtime_values(self):
        projected = {'risk_factor_identity': {'alias': 'EXAMPLE'}}
        defaults = {'open_questions': [], 'risk_factor_identity.alias': 'SHOULD_NOT_OVERWRITE'}
        out = mod._apply_compiled_state_defaults(projected, defaults)
        self.assertEqual(out['open_questions'], [])
        self.assertEqual(out['risk_factor_identity']['alias'], 'EXAMPLE')

    def test_retry_contract_aware_migration_repairs_legacy_narrow_rows_without_model(self):
        f = load_fixture('real_legacy_narrow_schema_retry.json')
        result = mod._retry_existing_table_message(f['record'], 'GENERIC_TABLE_NODE', f['history'], f['state'])
        self.assertIsNotNone(result)
        message, audit = result
        self.assertFalse(audit.get('requires_schema_repair', False))
        self.assertEqual(audit['unresolved_columns'], [])
        rows = audit['migrated_value']
        self.assertEqual(rows[0]['module'], 'company-profile')
        self.assertEqual(rows[0]['data_type'], 'companyProfile')
        self.assertEqual(rows[0]['field_path'], 'statusCode')
        self.assertEqual(rows[0]['field_role'], 'Trigger')
        self.assertEqual(rows[0]['calculation_relevance'], 'value == closed')
        self.assertEqual(rows[0]['source_evidence'], 'confirmed source description')
        self.assertEqual(rows[0]['analyst_status'], 'Confirmed')
        self.assertNotIn('| null |', message.lower())

    def test_retry_contract_aware_migration_requests_schema_repair_only_when_unresolved(self):
        f = load_fixture('real_legacy_narrow_schema_retry.json')
        state = {'mapping': f['state']['mapping']}
        result = mod._retry_existing_table_message(f['record'], 'GENERIC_TABLE_NODE', f['history'], state)
        self.assertIsNotNone(result)
        message, audit = result
        self.assertEqual(message, '')
        self.assertTrue(audit.get('requires_schema_repair'))
        self.assertIn('module', audit['unresolved_columns'])
        self.assertIn('data_type', audit['unresolved_columns'])
        self.assertIn('source_evidence', audit['unresolved_columns'])
        # Existing values are preserved as the repair baseline; no fresh proposal is synthesized.
        self.assertEqual(audit['migrated_value'][0]['field_path'], 'statusCode')
        self.assertEqual(audit['migrated_value'][0]['field_type'], 'string')

if __name__ == '__main__':
    unittest.main(verbosity=2)


class Alpha20RecoveryLoopRegressionTests(unittest.TestCase):
    def test_routed_gate_failure_forces_revisit_extension(self):
        node_id = "N_GENERATE_FUNCTIONAL_TESTS"
        previous_state = {"functional_test_catalog": {"rows": [{"tc_id": "FT-1"}]}}
        history = [
            {
                "role": "assistant",
                "node_id": node_id,
                "text": "Generated prior functional tests",
                "debug": {"runtime": {"state_after": previous_state}},
            },
            {
                "role": "assistant",
                "node_id": "G_TEST_COVERAGE_COMPLETE",
                "text": "FAIL",
                "debug": {
                    "current_id": "G_TEST_COVERAGE_COMPLETE",
                    "alpha20": {
                        "gate_failure": {
                            "gate_id": "G_TEST_COVERAGE_COMPLETE",
                            "failed_checks": [{"check_id": "G_TEST_COVERAGE_COMPLETE", "summary": "missing declared test coverage: schedules, calculation timestamps"}],
                            "invalid_state": [],
                            "missing_information": [],
                            "missing_coverage": ["schedules", "calculation timestamps"],
                            "affected_state": ["functional_test_catalog"],
                            "evidence": [],
                            "suggested_recovery_scope": "tests",
                        }
                    },
                    "runtime": {"next_id": node_id, "state_after": previous_state},
                },
            },
        ]
        element = {"state_contract": {"reads_hint": ["functional_test_catalog"], "writes": ["functional_test_catalog"]}}
        revisit = mod._revisit_context(history, node_id, previous_state, element)
        self.assertEqual(revisit["previous_answer_status"], "needs_extension")
        self.assertFalse(revisit["can_confirm_without_changes"])
        self.assertEqual(revisit["required_extension"]["missing_coverage"], ["schedules", "calculation timestamps"])
        self.assertEqual(revisit["recovery_gate_failure"]["gate_id"], "G_TEST_COVERAGE_COMPLETE")

    def test_deterministic_coverage_gate_structures_missing_coverage(self):
        record = {"id": "G_TEST_COVERAGE_COMPLETE", "coverage_requirements": ["alpha", "beta"], "coverage_catalogs": ["catalog_a.rows", "catalog_b.rows"], "on_pass": "NEXT", "on_fail": "N_GENERATE_FUNCTIONAL_TESTS"}
        # Generic coverage reads only explicit playbook-declared covers.
        state = {
            "catalog_a": {"rows": [{"tc_id":"A-1","scenario":"a","short_input":"x","expected_result":"y","covers":["alpha"]}]},
            "catalog_b": {"rows": [{"tc_id":"B-1","scenario":"b","short_input":"x","expected_result":"y","covers":["alpha"]}]},
        }
        routes = [{"key": "on_pass", "target": "NEXT"}, {"key": "on_fail", "target": "N_GENERATE_FUNCTIONAL_TESTS"}]
        creds = {"provider":"custom","base_url":"http://local/v1","api_style":"runtime_only","model":"m"}
        out = mod._execute_deterministic_gate(creds, record, record["id"], state, routes)
        failure = out["debug"]["alpha20"]["gate_failure"]
        self.assertIsNotNone(failure)
        self.assertIn("beta", failure["missing_coverage"])
        self.assertEqual(failure["missing_coverage"], ["beta"])
        self.assertEqual(failure["suggested_recovery_scope"], "local")

    def test_gate_failure_is_not_leaked_to_unrelated_revisit(self):
        node_id = "N_GENERATE_UNIT_TESTS"
        previous_state = {"unit_test_catalog": {"rows": [{"tc_id": "UT-1"}]}}
        history = [
            {"role": "assistant", "node_id": node_id, "text": "Generated prior unit tests", "debug": {"runtime": {"state_after": previous_state}}},
            {"role": "assistant", "node_id": "G_TEST_COVERAGE_COMPLETE", "text": "FAIL", "debug": {
                "alpha20": {"gate_failure": {"gate_id": "G_TEST_COVERAGE_COMPLETE", "missing_coverage": ["schedules"]}},
                "runtime": {"next_id": "N_GENERATE_FUNCTIONAL_TESTS", "state_after": previous_state},
            }},
        ]
        element = {"state_contract": {"reads_hint": ["unit_test_catalog"], "writes": ["unit_test_catalog"]}}
        revisit = mod._revisit_context(history, node_id, previous_state, element)
        self.assertEqual(revisit["previous_answer_status"], "still_valid")
        self.assertNotIn("recovery_gate_failure", revisit)
