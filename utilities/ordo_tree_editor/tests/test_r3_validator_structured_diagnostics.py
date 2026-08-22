import json, subprocess, sys
from pathlib import Path

def test_validator_preserves_structured_compiler_diagnostics(tmp_path):
    validator=Path(__file__).resolve().parents[1]/'integrated_compiler'/'validate_runtime_semantic_plan_v7.py'
    source=tmp_path/'program.ordo.yaml'
    source.write_text('nodes:\n  - id: N_START\n  - id: G_ORPHAN\n',encoding='utf-8')
    plan={
      'format':'ordo.runtime_semantic_plan','format_version':'1.4.0',
      'runtime_execution_contract':{'instruction_assembler':'runtime_semantic_v1'},
      'source':{'program':'program.ordo.yaml'},
      'graph':{'entry_node':'N_START','external_terminal_targets':[],'regions':[]},
      'state':{'schema_paths':[],'dependency_map':{}},
      'elements':{
        'N_START':{'id':'N_START','kind':'terminal','semantic_source':{},'semantic_fidelity':{'source_keys':[]},'state_contract':{'writes':[],'declared_inputs':[],'declared_inputs_by_class':{}},'output_contract':{'contract':'NodeExecutionResult'}},
        'G_ORPHAN':{'id':'G_ORPHAN','kind':'human_gate','semantic_source':{},'semantic_fidelity':{'source_keys':[]},'state_contract':{'writes':[],'declared_inputs':[],'declared_inputs_by_class':{}},'output_contract':{'contract':'GateFailureOrPass'},'gate_contract':{},'analyst_interaction':{'criterion':'x'},'routes':[]},
      },
      'validation':{'compilation_issues':[
        {'severity':'error','code':'GRAPH_NOT_FULLY_REACHABLE','reachable':1,'total':2,'unreachable':['G_ORPHAN']},
        {'severity':'error','code':'NONTERMINAL_WITHOUT_ROUTE','element_id':'G_ORPHAN'}
      ]}
    }
    pp=tmp_path/'plan.json'; pp.write_text(json.dumps(plan),encoding='utf-8')
    cp=subprocess.run([sys.executable,str(validator),str(pp)],cwd=tmp_path,capture_output=True,text=True)
    out=json.loads(cp.stdout)
    assert out['status']=='FAIL'
    by={d['code']:d for d in out['diagnostics']}
    assert by['GRAPH_NOT_FULLY_REACHABLE']['unreachable']==['G_ORPHAN']
    d=by['NONTERMINAL_WITHOUT_ROUTE']
    assert d['element_id']=='G_ORPHAN'
    assert d['source_location']['file']=='program.ordo.yaml'
    assert d['source_location']['line']==3
    assert d['current_routes']==[]
    assert d['expected'] and d['remediation']
