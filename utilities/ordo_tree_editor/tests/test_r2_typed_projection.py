import editor_service as es


def _base():
    return {'graph_contract':{'entry_node':'N1','external_terminal_targets':['END']},'nodes':[],'gates':[],'terminals':[{'id':'END'}]}


def test_r2_projection_typed_entities_and_no_navigation_control_flow():
    s=_base();s['nodes']=[
      {'id':'N1','title':'produce','writes':['x'],'next':'G1','navigation_contract':{'allowed_to':['N2']}},
      {'id':'N2','title':'doc','action':'DOCUMENT.GENERATE','inputs':['x'],'output':'generated_outputs/X.md','next':'END'}]
    s['gates']=[{'id':'G1','title':'validate x','inputs':['x'],'on_pass':'N2','on_fail':'END'}]
    g=es.graph_view(s)
    types={n['id']:n.get('entity_type') for n in g['nodes']}
    assert types['N1']=='execution_node' and types['G1']=='gate' and types['END']=='terminal'
    outs=[n for n in g['nodes'] if n.get('entity_type')=='output']
    assert len(outs)==1 and outs[0]['path']=='generated_outputs/X.md'
    assert not any(e['source']=='N1' and e['target']=='N2' and e['edge_type']=='control_flow' for e in g['edges'])
    dep=next(e for e in g['edges'] if e['source']=='N1' and e['target']=='G1' and e['edge_type']=='validation_dependency')
    assert (dep['source'],dep['target'],dep['edge_type'])==('N1','G1','validation_dependency')
    oid=outs[0]['id']
    assert any(e['source']=='N2' and e['target']==oid and e['edge_type']=='produces_output' for e in g['edges'])
    assert any(e['source']=='G1' and e['target']==oid and e['edge_type']=='enables_output' for e in g['edges'])


def test_r2_projection_block_disposition_never_becomes_entity():
    s=_base();s['nodes']=[{'id':'N1','next':'G1'}];s['gates']=[{'id':'G1','on_pass':'END','on_fail':'block'}]
    g=es.graph_view(s)
    assert 'block' not in {n['id'] for n in g['nodes']}
    assert not any(e['target']=='block' for e in g['edges'])


def test_r2_projection_unresolved_dependency_is_diagnostic_not_fake_edge():
    s=_base();s['nodes']=[{'id':'N1','next':'G1'}];s['gates']=[{'id':'G1','inputs':['missing.path'],'on_pass':'END'}]
    g=es.graph_view(s)
    assert any(x['gate']=='G1' and x['path']=='missing.path' for x in g['projection_diagnostics']['unresolved_validation_dependencies'])
    assert not any(e['edge_type']=='validation_dependency' and e.get('state_path')=='missing.path' for e in g['edges'])


def test_r2_projection_output_does_not_change_terminal_reachability():
    s=_base();s['nodes']=[{'id':'N1','action':'DOCUMENT.GENERATE','output':'x.md','next':'END'}]
    g=es.graph_view(s)
    assert g['projection_diagnostics']['unreachable_terminals']==[]
    assert not any(e['edge_type'] in {'produces_output','enables_output'} and e['target']=='END' for e in g['edges'])

def test_r2_projection_validator_passes_clean_fixture_and_fails_unresolved():
    s=_base();s['nodes']=[{'id':'N1','writes':['x'],'next':'G1'}];s['gates']=[{'id':'G1','inputs':['x'],'on_pass':'END'}]
    assert es.graph_view(s)['projection_validation']['status']=='PASS'
    s2=_base();s2['nodes']=[{'id':'N1','next':'G1'}];s2['gates']=[{'id':'G1','inputs':['missing'],'on_pass':'END'}]
    assert es.graph_view(s2)['projection_validation']['status']=='FAIL'
