from editor_service import _node_display_label


def test_node_title_precedes_question():
    node={"id":"N_X","title":"Short title","question":"A very long question","purpose":"Purpose"}
    assert _node_display_label(node)=="Short title"


def test_node_question_fallback_when_title_missing():
    node={"id":"N_X","question":"Question","purpose":"Purpose"}
    assert _node_display_label(node)=="Question"
