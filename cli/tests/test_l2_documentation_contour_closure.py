import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def j(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def find(v):
    out=[]
    if isinstance(v,dict):
        if v.get('id')=='L.2': out.append(v)
        for x in v.values(): out+=find(x)
    elif isinstance(v,list):
        for x in v: out+=find(x)
    return out
def test_l2_closed_everywhere():
    hits=find(j('manifests/CONSOLIDATED_BACKLOG.json'))
    assert len(hits)==1 and hits[0]['status']=='closed'
    m=j('manifests/CURRENT_MATURITY_STATE.json')
    assert m['documentation_quality']['L.2']=='closed'
    assert m['documentation_quality']['primary_onboarding']=='chat_first'
    assert m['documentation_quality']['optional_mechanical_validation']=='python_cli'
    assert all('L.2' not in x for x in m.get('next_documentation_tasks',[]))
    c=j('manifests/L2_DOCUMENTATION_CONTOUR_CLOSURE.json')
    assert c['contour_id']=='L.2' and c['status']=='closed'
    for p in c['evidence']: assert (ROOT/p).is_file()
