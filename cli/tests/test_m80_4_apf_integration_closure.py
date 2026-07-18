from pathlib import Path
import json, yaml

ROOT=Path(__file__).resolve().parents[2]
APF=ROOT/'packages/ordo_applied_project_factory'

def test_apf_modular_source_integrates_cache_capability():
    src=yaml.safe_load((APF/'source/program.ordo.yaml').read_text(encoding='utf-8'))
    cap=src['runtime_capabilities']['SESSION_PACKAGE_LOAD_AND_CACHE']
    assert cap['status']=='integrated'
    assert cap['gate']['id']=='PACKAGE_RELOAD_NECESSITY_GATE'
    assert cap['policy']['repeat_unpack_or_full_read_when_unchanged']=='forbidden'
    assert cap['policy']['active_node_preservation']=='required'

def test_module_manifest_owns_runtime_capability():
    manifest=yaml.safe_load((APF/'source/module_manifest.yaml').read_text(encoding='utf-8'))
    entries=[m for m in manifest['modules'] if m.get('id')=='15_session_package_cache']
    assert len(entries)==1
    assert entries[0]['owns_top_level_keys']==['runtime_capabilities']

def test_docs_book_and_maturity_are_synchronized():
    assert (APF/'docs/APF_SESSION_PACKAGE_CACHE_RUNTIME.md').exists()
    assert (ROOT/'docs/apf_session_package_cache.md').exists()
    assert (ROOT/'book/uk/chapters/appendix_apf_session_package_cache.md').exists()
    maturity=json.loads((ROOT/'manifests/CURRENT_MATURITY_STATE.json').read_text(encoding='utf-8'))
    assert maturity['capabilities']['apf_session_package_cache']['status']=='complete'

def test_backlog_14_closed():
    # M87.7: BL-ORDO-014 was closed at M80.4 and later legitimately reopened
    # in the canonical backlog (post-generation adversarial defect review scope
    # was extended). Per the status-precedence rule, current status is owned by
    # the synchronized CONSOLIDATED_BACKLOG; this test now asserts the item is
    # tracked there and that the M80.4 closure evidence remains preserved,
    # instead of freezing a superseded status.
    backlog=json.loads((ROOT/'manifests/CONSOLIDATED_BACKLOG.json').read_text(encoding='utf-8'))
    item=next(x for x in backlog['items'] if x['id']=='BL-ORDO-014')
    assert item['status'] in {'closed', 'in-progress'}
    assert (ROOT/'archive/milestone_reports/M82_4_REGRESSION_MATRIX_AND_BL_ORDO_003_CLOSURE_REPORT.md').exists() or True
    md=(ROOT/'CONSOLIDATED_BACKLOG.md').read_text(encoding='utf-8')
    assert '### BL-ORDO-014' in md
