from utilities.ordo_tree_editor.editor_service import _lineage_state_refs,_build_data_lineage
def test_template_ref():
 assert "risk_factor_identity.contract_version" in _lineage_state_refs("{{risk_factor_identity.contract_version}}")
def test_template_edge():
 source={"nodes":[{"id":"N_INPUT","question":"v","on_answer":{"update_state":{"risk_factor_identity.contract_version":"$answer.contract_version"},"next":"N_DOC"}},{"id":"N_DOC","template":"output_templates/doc.md","output":"generated_outputs/doc.md","next":"END"}],"gates":[]}
 package={"resources":{"output_templates/doc.md":"Version {{risk_factor_identity.contract_version}}"}}
 r=_build_data_lineage(package,source,{})
 assert any(e["source"]=="state:risk_factor_identity.contract_version" and e["target"]=="artifact:generated_outputs/doc.md" for e in r["edges"])
