#!/usr/bin/env python3
import copy, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import editor_service as mod

class MaterializationAndContractRegressions(unittest.TestCase):
    def setUp(self):
        self.pkg=copy.deepcopy(mod.PLAYBOOK_PACKAGE)
    def tearDown(self):
        mod.PLAYBOOK_PACKAGE.clear(); mod.PLAYBOOK_PACKAGE.update(self.pkg)

    def test_pseudo_source_fallback_is_not_applicable_not_unresolved(self):
        rows=[
            {'source_field':'static','target_field':'alias','transformation':'Constant: X','basic_fallback':'UNRESOLVED (no fallback evidence in runtime_state)'},
            {'source_field':'system','target_field':'date','transformation':'runtime date'},
            {'source_field':'algorithm','target_field':'flag','transformation':'computed'},
        ]
        migrated, unresolved=mod._migrate_rows_to_contract(rows,['source_field','target_field','transformation','basic_fallback'],{})
        self.assertEqual(unresolved,[])
        self.assertTrue(all(r['basic_fallback']=='NOT_APPLICABLE' for r in migrated))

    def test_applicable_missing_field_remains_unresolved(self):
        rows=[{'source_field':'payload.x','target_field':'x','transformation':'direct'}]
        migrated, unresolved=mod._migrate_rows_to_contract(rows,['source_field','target_field','transformation','basic_fallback'],{})
        self.assertEqual(migrated[0].get('basic_fallback'),None)
        self.assertIn('basic_fallback',unresolved)

    def test_branch_specific_human_updates_are_atomic_with_route_choice(self):
        rec={'on_answer':{'branch':{
            'approve':{'update_state':{'approval':True},'next':'NEXT'},
            'reject':{'update_state':{'approval':False},'next':'RETRY'},
        }}}
        state,updates=mod._apply_direct_answer_updates(rec,{},'approve')
        self.assertEqual(state['approval'],True)
        self.assertEqual(updates,{'approval':True})

    def test_dotted_binding_targets_build_nested_document_context(self):
        bound={}
        mod._set_dotted_state(bound,'risk_factor_identity.alias','ABC_RISK')
        mod._set_dotted_state(bound,'jira_task.title','Create ABC')
        self.assertEqual(mod._lookup_bound_path(bound,'risk_factor_identity.alias'),'ABC_RISK')
        self.assertEqual(mod._lookup_bound_path(bound,'jira_task.title'),'Create ABC')

    def test_table_contract_uses_only_declared_column_keys(self):
        contract={'collection':'state.catalog.rows','columns':[
            {'key':'tc_id','label':'TC','required':True},
            {'key':'scenario','label':'Scenario','required':True},
            {'key':'manual_check','label':'Manual','required':True},
            {'key':'short_input','label':'Input','required':True},
            {'key':'expected_result','label':'Expected','required':True},
        ]}
        value={'rows':[{'tc_id':'T-1','scenario':'positive','short_input':'x=1','expected_result':'Present'}]}
        text=mod._render_contract_table(value,contract,{})
        self.assertIn('| T-1 | positive | NOT_APPLICABLE | x=1 | Present |',text)

    def test_derivation_contract_requires_machine_readable_sources(self):
        rec={'derivation_contract':{
            'task.title':'derive concise title from approved state',
            'task.passport_reference':'generated_outputs/PASSPORT.md',
            'task.alias':{'source':'state.identity.alias'},
        }}
        state={'identity':{'alias':'EXAMPLE'}}
        derived,audit=mod._derive_document_contract(rec,state)
        self.assertIsNone(mod._state_subtree(derived,'task.title'))
        self.assertEqual(mod._state_subtree(derived,'task.passport_reference'),'generated_outputs/PASSPORT.md')
        self.assertEqual(mod._state_subtree(derived,'task.alias'),'EXAMPLE')
        self.assertEqual(len(audit),2)

    def test_validator_alignment_is_scoped_to_downstream_validator(self):
        validator='''REQUIRED_HEADINGS=["## 1. Correct title"]\nREQUIRED_IDENTITY_ROWS=[]\n'''
        source={'nodes':[{'id':'DOC','action':'DOCUMENT.GENERATE','next':'G'}],
                'gates':[{'id':'G','validator':'validators/v.py','on_pass':'END','on_fail':'DOC'}]}
        mod.PLAYBOOK_PACKAGE.clear(); mod.PLAYBOOK_PACKAGE.update({'source':source,'resources':{'validators/v.py':validator}})
        out,audit=mod._align_rendered_document_to_validator_contract('## 1. Wrong title\n',source['nodes'][0])
        self.assertIn('## 1. Correct title',out)
        self.assertEqual(len(audit),1)

if __name__=='__main__': unittest.main(verbosity=2)
