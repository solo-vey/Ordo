from integrated_compiler.compile_runtime_semantic_plan_v7 import _interaction_contract

def test_language_inference_uses_node_prose_when_interaction_model_absent():
    doc={'intent':{},'nodes':[{'id':'N1','purpose':'Перевірити коректність даних та попросити аналітика підтвердити рішення.'}],'gates':[]}
    c=_interaction_contract(doc)
    assert c['locale']=='uk-UA' and c['model_output_language']=='uk' and c['source']=='compatibility_inference'

def test_explicit_language_stays_authoritative():
    c=_interaction_contract({'interaction_model':{'locale':'en-GB','model_output_language':'en'},'nodes':[{'purpose':'Український текст'}]})
    assert c['locale']=='en-GB' and c['model_output_language']=='en' and c['source']=='interaction_model'
