import json
from pathlib import Path
from language.process_patterns.pattern_engine import validate_registry,recommend,compose,render_review_card
ROOT=Path(__file__).resolve().parents[2]
REG=json.loads((ROOT/'language/process_patterns/pattern_registry.v1.json').read_text())
def test_registry_valid(): assert validate_registry(REG)==[]
def test_two_stable_real_patterns(): assert len([p for p in REG['patterns'] if p['status']=='stable'])>=2
def test_stable_patterns_have_two_packages(): assert all(len(set(p['provenance']['packages']))>=2 for p in REG['patterns'] if p['status']=='stable')
def test_recommend_fail_closed(): assert recommend(REG,{'multiple_predecessors'})==[]
def test_recommend_shared_tail(): assert recommend(REG,{'multiple_predecessors','equivalent_completion_semantics','deterministic_return'})==['PAT-SHARED-CONVERGENCE']
def test_declared_composition_passes(): assert compose(REG,['PAT-SHARED-CONVERGENCE','PAT-GUIDED-REVIEW-LOOP'])['status']=='passed'
def test_unknown_composition_fails(): assert compose(REG,['PAT-UNKNOWN'])['status']=='failed'
def test_review_card_blocks_missing_evidence():
 p=REG['patterns'][0]; c=render_review_card(p,{}); assert c['decision']=='blocked' and c['missing_evidence']
def test_review_card_ready_with_evidence():
 p=REG['patterns'][0]; e={x:'ref' for x in p['evidence_requirements']}; assert render_review_card(p,e)['decision']=='pending_human_review'
