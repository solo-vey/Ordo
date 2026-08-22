import editor_service as es

def routes():
    return [{'key':'on_pass','target':'PASS'},{'key':'on_fail','target':'FAIL'}]

def record():
    return {'method':'human','trust_class':'human_decision'}

def test_ukrainian_display_pass_label_is_runtime_owned():
    assert es._select_direct_answer_route(record(), routes(), 'Погодити — критерій виконано')['key']=='on_pass'

def test_ukrainian_display_fail_label_is_runtime_owned():
    assert es._select_direct_answer_route(record(), routes(), 'Потрібне виправлення — критерій не виконано')['key']=='on_fail'
