
from utilities.ordo_tree_editor import editor_service as es

def test_data_lineage_builds_analyst_state_document_and_archive():
    source={
      "nodes":[
        {"id":"N_INPUT","question":"Name?","on_answer":{"update_state":{"customer.name":"$answer"}}},
        {"id":"N_DERIVE","action":"AI.GENERATE","update_state":{"summary":"state.customer.name"}},
        {"id":"N_DOC","output":"generated/report.md","inputs":["state.summary"]},
        {"id":"N_ZIP","action":"deterministic package","output":"generated/package.zip","inputs":["generated/report.md"]},
      ],"gates":[]
    }
    data=es._build_data_lineage({"resources":{}},source,{"customer":{"name":"Acme"}})
    by={n["id"]:n for n in data["nodes"]}
    assert by["state:customer.name"]["kind"]=="analyst_input"
    assert by["state:customer.name"]["current_value"]=="Acme"
    assert by["state:summary"]["kind"]=="derived_state"
    assert by["artifact:generated/report.md"]["kind"]=="document"
    assert by["artifact:generated/package.zip"]["kind"]=="archive"
    rel={(e["source"],e["target"],e["relation"]) for e in data["edges"]}
    assert ("state:customer.name","state:summary","derived_from") in rel
    assert ("state:summary","artifact:generated/report.md","materializes") in rel
    assert ("artifact:generated/report.md","artifact:generated/package.zip","packages") in rel
