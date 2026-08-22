
from utilities.ordo_tree_editor import editor_service as es


def test_lineage_has_transformations_and_registry_traceability():
    """Lineage behavior must be verified without a developer-machine fixture."""
    source={
        "nodes":[
            {
                "id":"N_DRAFT_IDENTITY", "runtime_executor":"deterministic",
                "update_state":{"risk_factor_identity.contract_version":"$state.risk_factor_candidate"},
            },
            {
                "id":"N_GENERATE_DOCUMENT", "runtime_executor":"deterministic",
                "output":"generated_outputs/RISK_FACTOR_PASSPORT.md",
                "derive_before_generate":{"document.title":"$state.risk_factor_identity"},
            },
            {
                "id":"N_PACKAGE_DOCUMENT", "runtime_executor":"deterministic",
                "package":{"path":"generated_outputs/RISK_FACTOR_PASSPORT_PACKAGE.zip"},
                "inputs":["generated_outputs/RISK_FACTOR_PASSPORT.md"],
            },
        ],
        "gates":[],
    }
    package={"resources":{
        "registries/state.yaml": "variables:\n  - path: risk_factor_identity.contract_version\n    source_node: N_DRAFT_IDENTITY\n",
    }}
    data=es._build_data_lineage(package,source,{})
    by={n['id']:n for n in data['nodes']}
    edges={(e['source'],e['target'],e['relation']) for e in data['edges']}
    assert data['summary']['transformations'] >= 3
    assert 'transform:N_DRAFT_IDENTITY' in by
    assert ('state:risk_factor_candidate','transform:N_DRAFT_IDENTITY','input_to') in edges
    assert ('transform:N_DRAFT_IDENTITY','state:risk_factor_identity.contract_version','produces') in edges
    assert ('transform:N_GENERATE_DOCUMENT','artifact:generated_outputs/RISK_FACTOR_PASSPORT.md','materializes') in edges
    assert ('transform:N_PACKAGE_DOCUMENT','artifact:generated_outputs/RISK_FACTOR_PASSPORT_PACKAGE.zip','packages') in edges
    cv=by['state:risk_factor_identity.contract_version']
    assert cv.get('registry_metadata',{}).get('source_node')=='N_DRAFT_IDENTITY'
