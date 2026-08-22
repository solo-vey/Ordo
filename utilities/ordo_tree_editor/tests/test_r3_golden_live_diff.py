from utilities.ordo_tree_editor.compare_golden_live_v3 import compare

def test_structural_invariant_diff_passes_without_text_identity():
    g={'acceptance_source':{'terminal':'END'},'calls':[{'element_id':'A'},{'element_id':'B'}]}
    l={'run':{'outcome':{'nodeId':'END'}},'calls':[{'step_class':'live_model_call','current_id':'A','output':{'raw_text':'different'}},{'step_class':'live_model_call','current_id':'B'}]}
    assert compare(g,l)['status']=='PASS'

def test_model_sequence_drift_fails():
    g={'acceptance_source':{'terminal':'END'},'calls':[{'element_id':'A'}]}
    l={'run':{'outcome':{'nodeId':'END'}},'calls':[{'step_class':'live_model_call','current_id':'B'}]}
    assert compare(g,l)['status']=='FAIL'
