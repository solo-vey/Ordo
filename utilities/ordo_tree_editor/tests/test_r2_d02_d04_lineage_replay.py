import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import editor_service as es


def test_state_lineage_hash_is_canonical_and_records_revision():
    a={"z":1,"a":{"b":2}}
    b={"a":{"b":2},"z":1}
    assert es._canonical_value_hash(a)==es._canonical_value_hash(b)
    patch={"operations":[{"op":"set","path":"x","value":a,"basis":"generated","reason":"fixture"}]}
    rows=es._state_lineage_entries(patch=patch,new_state={"x":b},revision=7,producer_element_id="N_X",source_run_id="run-7")
    assert rows==[{"path":"x","revision":7,"producer_element_id":"N_X","operation":"set","basis":"generated","reason":"fixture","source_run_id":"run-7","value_hash":es._canonical_value_hash(b)}]


def test_strict_replay_requires_component_provenance():
    repro={
      "kind":"debug_reproduction","schema_version":"ordo.debug_reproduction.v2",
      "strict_replay_provenance":True,"source_run_id":"run-r2",
      "recorded_against":{"compiler":"V7.14-r2","editor":"a20.35","playbook":"ALFA0.9.4","semantic_plan_sha256":"a"*64},
      "recorded_calls":[],"answers_by_node":{},"suggested_checkpoint":"N_END"
    }
    raw=json.dumps(repro,sort_keys=True).encode()
    out=es.parse_replay_package('reproduction.json',raw)
    assert out['source_run_id']=='run-r2'
    assert out['recorded_against']['playbook']=='ALFA0.9.4'
    assert out['source_sha256']==hashlib.sha256(raw).hexdigest()


def test_strict_replay_rejects_missing_component_provenance():
    repro={"kind":"debug_reproduction","schema_version":"ordo.debug_reproduction.v2","strict_replay_provenance":True,"source_run_id":"run-r2","recorded_against":{},"recorded_calls":[],"answers_by_node":{}}
    try:
        es.parse_replay_package('reproduction.json',json.dumps(repro).encode())
    except ValueError as e:
        assert 'recorded_against.compiler' in str(e)
    else:
        raise AssertionError('strict replay provenance should fail closed')
