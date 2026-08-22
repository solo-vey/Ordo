from utilities.ordo_tree_editor import editor_service as es

def test_kf016_evaluator_proves_recovered_coverage():
    record={
        "coverage_requirements":["alpha","beta"],
        "coverage_catalogs":["catalog.rows"],
    }
    state={"catalog":{"rows":[
        {"tc_id":"T-1","scenario":"a","short_input":"x","expected_result":"y","covers":["alpha"]},
        {"tc_id":"T-2","scenario":"b","short_input":"x","expected_result":"y","covers":["beta"]},
    ]}}
    result=es._evaluate_test_coverage_gate(record,state)
    assert result[0]=="pass", result
    assert result[2]["coverage_requirements"]=={"alpha":True,"beta":True}
