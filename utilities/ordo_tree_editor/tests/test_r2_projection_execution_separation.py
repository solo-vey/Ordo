from utilities.ordo_tree_editor import editor_service as es

def source():
    return {
      'graph_contract':{'entry_node':'N1','external_terminal_targets':['END']},
      'nodes':[
        {'id':'N1','next':'G1','writes':['x'],'output':'generated_outputs/X.md'},
        {'id':'N2','next':'END'},
      ],
      'gates':[{'id':'G1','required_inputs':['x'],'on_pass':'N2','on_fail':'N1'}],
      'terminals':[{'id':'END'}],
    }

g=es.graph_view(source())
# A derived output must be one entity, never duplicated as external terminal.
out=[n for n in g['nodes'] if n['id']=='OUT::generated_outputs/X.md']
assert len(out)==1, out
assert out[0]['entity_type']=='output', out[0]
# Dependency is typed separately from control flow.
deps=[e for e in g['edges'] if e.get('edge_type')=='validation_dependency']
assert any(e['source']=='N1' and e['target']=='G1' for e in deps), deps
# All executable path edges remain control flow only.
ctrl=[e for e in g['edges'] if e.get('edge_type')=='control_flow']
assert any(e['source']=='N1' and e['target']=='G1' for e in ctrl), ctrl
print('PASS')
