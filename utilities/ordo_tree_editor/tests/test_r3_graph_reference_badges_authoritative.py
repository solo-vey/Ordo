import io
import zipfile

from utilities.ordo_tree_editor import editor_service as es


def test_graph_badges_match_resolved_inspector_references():
    source="""nodes:
  - id: N_START
    question: Start.
gates:
  - id: G_ONE
    validator: validators/validate_example.py
  - id: G_TWO
    validator: validators/validate_example.py
  - id: G_THREE
    validator: validators/validate_example.py
"""
    archive=io.BytesIO()
    with zipfile.ZipFile(archive,"w") as bundle:
        bundle.writestr("source/program.ordo.yaml",source)
        bundle.writestr("validators/validate_example.py","# validator\n")
    pkg=es.parse_playbook_package("portable-playbook.zip",archive.getvalue())
    for node_id in ('G_ONE','G_TWO','G_THREE'):
        view=next(n for n in pkg['graph']['nodes'] if n['id']==node_id)
        assert len(view['resource_references'])==1
        assert view['resource_references'][0].endswith('validators/validate_example.py')
        assert not any(x.endswith('.md') or x.endswith('.json') for x in view['resource_references'])
