
from pathlib import Path
import yaml
from utilities.ordo_tree_editor import editor_service as es


def _package_from_dir(base: Path):
    resources={}
    for p in base.rglob('*'):
        if not p.is_file():
            continue
        rel=p.relative_to(base).as_posix()
        try: text=p.read_text(encoding='utf-8')
        except Exception: continue
        resources[rel]=text
    return {"resources":resources}


def test_real_rfp_lineage_has_transformations_and_registry_traceability():
    base=Path('/tmp/rfp095/RISK_FACTOR_PASSPORT_PLAYBOOK_ALFA_0.9.5_DEV_R3COMPAT')
    source=yaml.safe_load((base/'source/program.ordo.yaml').read_text(encoding='utf-8'))
    data=es._build_data_lineage(_package_from_dir(base),source,{})
    by={n['id']:n for n in data['nodes']}
    edges={(e['source'],e['target'],e['relation']) for e in data['edges']}
    assert data['summary']['transformations'] > 10
    assert 'transform:N_RISK_FACTOR_IDENTITY_DRAFT' in by
    assert ('state:risk_factor_candidate','transform:N_RISK_FACTOR_IDENTITY_DRAFT','input_to') in edges
    assert ('transform:N_RISK_FACTOR_IDENTITY_DRAFT','state:risk_factor_identity.contract_version','produces') in edges
    assert 'transform:N_BUSINESS_MEANING' in by
    assert ('state:risk_factor_identity','transform:N_BUSINESS_MEANING','input_to') in edges
    assert ('transform:N_DERIVE_JIRA_TASK_CONTENT','state:jira_task.title','produces') in edges
    assert ('transform:N_GENERATE_PASSPORT_DRAFT','artifact:generated_outputs/RISK_FACTOR_PASSPORT.md','materializes') in edges
    assert ('artifact:generated_outputs/RISK_FACTOR_PASSPORT.md','transform:N_FORM_DELIVERY_PACKAGE','input_to') in edges
    assert ('transform:N_FORM_DELIVERY_PACKAGE','artifact:generated_outputs/RISK_FACTOR_PASSPORT_PACKAGE.zip','packages') in edges
    cv=by['state:risk_factor_identity.contract_version']
    assert cv.get('registry_metadata',{}).get('source_node')=='N_RISK_FACTOR_IDENTITY_DRAFT'
