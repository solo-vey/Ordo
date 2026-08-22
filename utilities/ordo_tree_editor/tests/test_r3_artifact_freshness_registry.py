from utilities.ordo_tree_editor import editor_service as es


def test_artifact_becomes_stale_when_dependency_changes():
    token=es._ACTIVE_RUN_CONTEXT.set({'package_id':'p','session_id':'s','run_id':'r'})
    try:
        es.RUN_ARTIFACT_REGISTRY.pop(('p','s','r'),None)
        es._update_artifact_registry(artifact_lineage={'path':'out/a.md','materialized_from_revision':2,'depends_on_paths':['doc.status']})
        assert es._run_artifact_status('out/a.md')['freshness_status']=='fresh'
        es._update_artifact_registry(state_lineage=[{'path':'doc.status','revision':3,'producer_element_id':'N_APPROVE'}])
        row=es._run_artifact_status('out/a.md')
        assert row['freshness_status']=='stale'
        assert row['stale_by_state_lineage'][0]['revision']==3
    finally:
        es._ACTIVE_RUN_CONTEXT.reset(token)


def test_unrelated_state_change_does_not_stale_artifact():
    token=es._ACTIVE_RUN_CONTEXT.set({'package_id':'p','session_id':'s','run_id':'r2'})
    try:
        es.RUN_ARTIFACT_REGISTRY.pop(('p','s','r2'),None)
        es._update_artifact_registry(artifact_lineage={'path':'out/a.md','materialized_from_revision':2,'depends_on_paths':['doc.status']})
        es._update_artifact_registry(state_lineage=[{'path':'other.value','revision':3,'producer_element_id':'N_X'}])
        assert es._run_artifact_status('out/a.md')['freshness_status']=='fresh'
    finally:
        es._ACTIVE_RUN_CONTEXT.reset(token)


def test_artifact_dependencies_use_canonical_semantic_plan_package_key():
    pkg={
        'id':'p-deps',
        'semantic_plan':{'elements':{'N_DOC':{'state_contract':{
            'reads_hint':['doc.status','payload'],
            'declared_inputs_by_class':{'state':['approval']},
        }}}},
    }
    token=es._ACTIVE_PLAYBOOK_PACKAGE.set(pkg)
    try:
        assert es._artifact_dependency_paths_for_element('N_DOC') == ['approval','doc.status','payload']
    finally:
        es._ACTIVE_PLAYBOOK_PACKAGE.reset(token)
