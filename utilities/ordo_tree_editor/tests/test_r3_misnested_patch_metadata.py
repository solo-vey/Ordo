import copy
import editor_service as es


def test_misnested_basis_reason_are_hoisted_only_when_contract_becomes_valid():
    patch={"base_revision":7,"operations":[{
        "op":"append","path":"items.rows","value":{
            "id":"A","text":"ok","basis":"generated","reason":"model derivation"
        }
    }]}
    schemas={"items.rows":{"type":"array","items":{"type":"object","required":["id","text"],"additionalProperties":False,"properties":{"id":{"type":"string"},"text":{"type":"string"}}}}}
    variants=[{"op":"append","path":"items.rows"}]
    before=copy.deepcopy(patch)
    out, adaptations=es._adapt_misnested_patch_metadata(
        patch,allowed_paths=["items.rows"],current_revision=7,value_schemas=schemas,operation_variants=variants)
    assert before==patch  # helper does not mutate caller object
    assert adaptations and adaptations[0]["fields"]==["basis","reason"]
    assert out["operations"][0]["basis"]=="generated"
    assert out["operations"][0]["reason"]=="model derivation"
    assert "basis" not in out["operations"][0]["value"]
    assert es.validate_state_patch(out,allowed_paths=["items.rows"],current_revision=7,value_schemas=schemas,operation_variants=variants)["valid"]


def test_no_hoist_when_removed_value_still_violates_contract():
    patch={"base_revision":0,"operations":[{"op":"append","path":"items.rows","value":{"basis":"generated","reason":"x","unknown":1}}]}
    schemas={"items.rows":{"type":"array","items":{"type":"object","required":["id"],"additionalProperties":False,"properties":{"id":{"type":"string"}}}}}
    out, adaptations=es._adapt_misnested_patch_metadata(patch,allowed_paths=["items.rows"],current_revision=0,value_schemas=schemas,operation_variants=[{"op":"append","path":"items.rows"}])
    assert out==patch
    assert adaptations==[]
