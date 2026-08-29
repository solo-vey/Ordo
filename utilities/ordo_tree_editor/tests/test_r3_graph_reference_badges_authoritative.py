from pathlib import Path
from utilities.ordo_tree_editor import editor_service as es


def test_graph_badges_match_resolved_inspector_references():
    p=Path('/mnt/data/RISK_FACTOR_PASSPORT_PLAYBOOK_ALFA_0.9.5_DEV_R3COMPAT_SOURCE_ONLY(2).zip')
    pkg=es.parse_playbook_package(p.name,p.read_bytes())
    for node_id in ('G_PASSPORT_COMPLETENESS','G_PASSPORT_POST_MATERIALIZATION_PYTHON','G_PASSPORT_CONSISTENCY'):
        view=next(n for n in pkg['graph']['nodes'] if n['id']==node_id)
        assert len(view['resource_references'])==1
        assert view['resource_references'][0].endswith('validators/validate_risk_factor_passport.py')
        assert not any(x.endswith('.md') or x.endswith('.json') for x in view['resource_references'])
