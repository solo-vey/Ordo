from utilities.ordo_tree_editor.editor_service import _apply_authority_contract_to_candidate


def _element():
    return {
        "semantic_source": {
            "authority_contract": {
                "derived_targets": {
                    "derived_text": {"sources": ["source_contract"], "must_include_from": ["source_contract.exact"]},
                    "derived_list": {"sources": ["source_rows"]},
                },
                "clarification_only_fields": ["target_module"],
                "open_questions_path": "open_questions",
            }
        }
    }


def _patch(ops):
    return {"state_patch": {"base_revision": 1, "operations": ops}}


def _op(path, value, basis="derived"):
    return {"op":"set","path":path,"value":value,"basis":basis,"reason":"test","row_key":None,"row_match":None}


def test_authority_requires_derived_targets_when_sources_exist_and_owns_open_questions():
    state = {"source_contract":{"exact":"x"}, "source_rows":[{"field":"a"}], "target_module":None}
    candidate, adaptations, errors = _apply_authority_contract_to_candidate(
        _patch([]), semantic_element=_element(), state=state, phase="enter"
    )
    assert any("derived_text" in e for e in errors)
    assert any("derived_list" in e for e in errors)
    assert adaptations and adaptations[0]["missing_fields"] == ["target_module"]
    open_ops=[op for op in candidate["state_patch"]["operations"] if op["path"]=="open_questions"]
    assert open_ops[0]["value"] == ["target_module"]


def test_authority_accepts_grounded_derivation_and_does_not_invent_clarification_field():
    state = {"source_contract":{"exact":"x"}, "source_rows":[{"field":"a"}], "target_module":None}
    candidate, adaptations, errors = _apply_authority_contract_to_candidate(
        _patch([_op("derived_text","exact x"), _op("derived_list",["a"]) ]),
        semantic_element=_element(), state=state, phase="enter"
    )
    assert errors == []
    assert [op for op in candidate["state_patch"]["operations"] if op["path"]=="open_questions"][0]["value"] == ["target_module"]


def test_authority_preserves_existing_canonical_target_against_model_replacement():
    state = {"source_contract":{"exact":"x"}, "source_rows":[{"field":"a"}], "derived_text":"confirmed x", "derived_list":["confirmed"], "target_module":"real.module"}
    candidate, _, errors = _apply_authority_contract_to_candidate(
        _patch([_op("derived_text","generic default"), _op("derived_list",["generic"]) ]),
        semantic_element=_element(), state=state, phase="enter"
    )
    assert any("derived_text" in e and "cannot be replaced" in e for e in errors)
    assert any("derived_list" in e and "cannot be replaced" in e for e in errors)
    assert [op for op in candidate["state_patch"]["operations"] if op["path"]=="open_questions"][0]["value"] == []


def test_authority_rejects_generic_default_that_omits_required_canonical_literal():
    state = {"source_contract":{"exact":"x"}, "source_rows":[{"field":"a"}], "target_module":None}
    candidate, _, errors = _apply_authority_contract_to_candidate(
        _patch([_op("derived_text","generic default"), _op("derived_list",["a"]) ]),
        semantic_element=_element(), state=state, phase="enter"
    )
    assert any("derived_text" in e and "omits canonical literal" in e for e in errors)
