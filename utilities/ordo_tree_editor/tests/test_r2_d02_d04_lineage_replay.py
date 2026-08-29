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


def test_legacy_reproduction_json_is_rejected():
    repro={"kind":"debug_reproduction","schema_version":"ordo.debug_reproduction.v2","recorded_calls":[]}
    try:
        es.parse_replay_package('reproduction.json',json.dumps(repro).encode())
    except ValueError as error:
        assert 'canonical debug handoff ZIP' in str(error)
    else:
        raise AssertionError('legacy reproduction JSON must be rejected')
