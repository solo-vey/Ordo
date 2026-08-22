import copy
import editor_service as es


def base(nodes, outputs=None):
    source={
        'graph_contract':{'entry_node':nodes[0]['id'] if nodes else None,'external_terminal_targets':['END']},
        'nodes':nodes,
        'gates':[],
        'terminals':[{'id':'END'}],
    }
    if outputs is not None:
        source['outputs']=outputs
    return source


def output_node(graph, oid):
    return next(n for n in graph['nodes'] if n['id']==oid)


def trace(graph, oid):
    rows=graph['projection_diagnostics']['declared_output_producer_traceability']
    return next(x for x in rows if x['output_id']==oid)


def semantic_edges(graph, oid):
    return [e for e in graph['edges'] if e.get('edge_type')=='declares_output' and e['target']==oid]


def test_single_formal_producer_association_is_non_execution():
    s=base([
        {'id':'N_MATERIALIZE','action':'DOCUMENT.GENERATE','output':'generated/passport.md','next':'END'}
    ],[
        {'id':'OUT_PASSPORT','type':'document','artifact':{'expected_path':'generated/passport.md'}}
    ])
    g=es.graph_view(s)
    out=output_node(g,'OUT_PASSPORT')
    assert out['entity_type']=='declared_output'
    assert out['producers']==['N_MATERIALIZE']
    edge=semantic_edges(g,'OUT_PASSPORT')[0]
    assert edge['source']=='N_MATERIALIZE'
    assert edge['relation_type']=='declares_output'
    assert edge['edge_type']!='control_flow'
    assert not any(e.get('edge_type')=='control_flow' and e['target']=='OUT_PASSPORT' for e in g['edges'])
    assert trace(g,'OUT_PASSPORT')['status']=='PASS'


def test_one_materializer_can_form_multiple_declared_outputs():
    s=base([
        {'id':'N_MATERIALIZE','artifacts':[{'expected_path':'generated/a.md'},{'expected_path':'generated/b.json'}],'next':'END'}
    ],[
        {'id':'OUT_A','artifact':{'expected_path':'generated/a.md'}},
        {'id':'OUT_B','artifact':{'expected_path':'generated/b.json'}},
    ])
    g=es.graph_view(s)
    assert output_node(g,'OUT_A')['producers']==['N_MATERIALIZE']
    assert output_node(g,'OUT_B')['producers']==['N_MATERIALIZE']
    assert len(semantic_edges(g,'OUT_A'))==1 and len(semantic_edges(g,'OUT_B'))==1


def test_different_materializers_resolve_different_outputs():
    s=base([
        {'id':'N_A','output':'generated/a.md','next':'N_B'},
        {'id':'N_B','artifact':{'expected_path':'generated/b.yaml'},'next':'END'},
    ],[
        {'id':'OUT_A','path':'generated/a.md'},
        {'id':'OUT_B','artifact':{'expected_path':'generated/b.yaml'}},
    ])
    g=es.graph_view(s)
    assert output_node(g,'OUT_A')['producers']==['N_A']
    assert output_node(g,'OUT_B')['producers']==['N_B']


def test_unresolved_declared_output_is_diagnostic_not_guessed():
    s=base([{'id':'N_A','output':'generated/a.md','next':'END'}],[{'id':'OUT_UNKNOWN','path':'generated/other.md'}])
    g=es.graph_view(s)
    out=output_node(g,'OUT_UNKNOWN')
    assert out['producers']==[]
    assert semantic_edges(g,'OUT_UNKNOWN')==[]
    t=trace(g,'OUT_UNKNOWN')
    assert t['status']=='WARNING' and t['reason']=='unresolved_producer'


def test_ambiguous_declared_output_has_no_semantic_link():
    s=base([
        {'id':'N_A','output':'generated/x.md','next':'N_B'},
        {'id':'N_B','output':'generated/x.md','next':'END'},
    ],[{'id':'OUT_X','artifact':{'expected_path':'generated/x.md'}}])
    g=es.graph_view(s)
    assert output_node(g,'OUT_X')['producers']==[]
    assert semantic_edges(g,'OUT_X')==[]
    t=trace(g,'OUT_X')
    assert t['status']=='FAIL' and t['reason']=='ambiguous_producer'
    assert set(t['candidates'])=={'N_A','N_B'}


def test_document_json_yaml_and_zip_paths_are_format_agnostic():
    paths=['generated/doc.md','generated/data.json','generated/spec.yaml','generated/package.zip']
    nodes=[]; outputs=[]
    for i,path in enumerate(paths):
        nid=f'N_{i}'; oid=f'OUT_{i}'
        nodes.append({'id':nid,'output':path,'next':f'N_{i+1}' if i+1<len(paths) else 'END'})
        outputs.append({'id':oid,'artifact':{'expected_path':path}})
    g=es.graph_view(base(nodes,outputs))
    for i in range(len(paths)):
        assert output_node(g,f'OUT_{i}')['producers']==[f'N_{i}']


def test_nested_package_assembly_resolves_by_formal_package_path():
    s=base([
        {'id':'N_PACKAGE','package':{'path':'dist/releases/final_bundle.zip'},'next':'END'}
    ],[{'id':'OUT_PACKAGE','type':'archive','artifact':{'expected_path':'dist/releases/final_bundle.zip'}}])
    g=es.graph_view(s)
    assert output_node(g,'OUT_PACKAGE')['producers']==['N_PACKAGE']


def test_playbook_without_declared_outputs_keeps_existing_derived_projection():
    s=base([{'id':'N_DOC','output':'generated/doc.md','next':'END'}],None)
    g=es.graph_view(s)
    derived=output_node(g,'OUT::generated/doc.md')
    assert derived['entity_type']=='output'
    assert derived['producers']==['N_DOC']


def test_declared_output_id_is_not_implicitly_an_external_terminal():
    s=base([{'id':'N_DOC','output':'generated/doc.md','next':'END'}],[{'id':'OUT_DOC','path':'generated/doc.md'}])
    g=es.graph_view(s)
    nodes=[n for n in g['nodes'] if n['id']=='OUT_DOC']
    assert len(nodes)==1
    assert nodes[0]['entity_type']=='declared_output'
    assert nodes[0]['element_type']=='output'
    assert nodes[0]['terminal'] is False


def test_explicit_graph_contract_terminal_still_remains_execution_terminal():
    s=base([{'id':'N1','next':'OUT_ROUTED'}],[{'id':'OUT_ROUTED','path':'generated/routed.md'}])
    s['graph_contract']['external_terminal_targets']=['END','OUT_ROUTED']
    g=es.graph_view(s)
    routed=[n for n in g['nodes'] if n['id']=='OUT_ROUTED']
    assert len(routed)==1
    assert routed[0]['element_type']=='terminal'
    assert any(e.get('edge_type')=='control_flow' and e['source']=='N1' and e['target']=='OUT_ROUTED' for e in g['edges'])


def test_execution_control_flow_is_unchanged_by_output_projection():
    s=base([
        {'id':'N1','next':'N2'},
        {'id':'N2','output':'generated/x.md','next':'END'},
    ],[{'id':'OUT_X','path':'generated/x.md'}])
    control_before={(n['id'],e['target'],e.get('key')) for n in s['nodes'] for e in es._node_edges(n)}
    g=es.graph_view(copy.deepcopy(s))
    control_after={(e['source'],e['target'],e.get('key')) for e in g['edges'] if e.get('edge_type')=='control_flow'}
    assert control_after==control_before


def test_no_fuzzy_name_matching_for_output_ids():
    s=base([{'id':'N_MATERIALIZE_RISK_FACTOR_PASSPORT','output':'generated/unrelated.md','next':'END'}],[{'id':'OUT_RISK_FACTOR_PASSPORT','path':'generated/passport.md'}])
    g=es.graph_view(s)
    assert output_node(g,'OUT_RISK_FACTOR_PASSPORT')['producers']==[]
    assert trace(g,'OUT_RISK_FACTOR_PASSPORT')['reason']=='unresolved_producer'


def test_editor_validation_surfaces_traceability_warning_and_ambiguity():
    unresolved=base([{'id':'N1','output':'generated/a.md','next':'END'}],[{'id':'OUT_X','path':'generated/x.md'}])
    v=es.validate_source(unresolved)
    check=next(c for c in v['checks'] if c['name']=='DECLARED_OUTPUT_PRODUCER_TRACEABILITY')
    assert any(f['code']=='DECLARED_OUTPUT_PRODUCER_UNRESOLVED' for f in check['findings'])
    ambiguous=base([
        {'id':'N1','output':'generated/x.md','next':'N2'},
        {'id':'N2','output':'generated/x.md','next':'END'},
    ],[{'id':'OUT_X','path':'generated/x.md'}])
    v2=es.validate_source(ambiguous)
    check2=next(c for c in v2['checks'] if c['name']=='DECLARED_OUTPUT_PRODUCER_TRACEABILITY')
    assert any(f['code']=='DECLARED_OUTPUT_PRODUCER_AMBIGUOUS' and f['severity']=='error' for f in check2['findings'])
