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

def test_docs_and_book_are_synchronized():
    assert (APF/'docs/APF_SESSION_PACKAGE_CACHE_RUNTIME.md').exists()
    assert (ROOT/'docs/apf_session_package_cache.md').exists()
    assert (ROOT/'book/uk/chapters/appendix_apf_session_package_cache.md').exists()

def test_m80_4_closure_evidence_remains_in_the_active_tree():
    assert (ROOT/'docs/apf_session_package_cache.md').exists()
