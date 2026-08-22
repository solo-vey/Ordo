import editor_service as es

def test_explicit_interaction_locale_reaches_model_contract():
    old=es.PLAYBOOK_PACKAGE.copy()
    try:
        es.PLAYBOOK_PACKAGE["semantic_plan"]={"interaction_contract":{"locale":"uk-UA","model_output_language":"uk"}}
        c=es._interaction_contract()
        assert c=={"locale":"uk-UA","model_output_language":"uk"}
        text=es._analyst_language_instruction()
        assert "uk-UA" in text and "language=uk" in text and "assistant_message" in text
    finally:
        es.PLAYBOOK_PACKAGE.clear(); es.PLAYBOOK_PACKAGE.update(old)
