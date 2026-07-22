from pathlib import Path
import sys, yaml
import pytest

pytestmark = pytest.mark.xfail(
    strict=True,
    reason="BL-ORDO-061: APF module source has drifted from the canonical program.",
)
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from assemble_ordo_modules import assemble

def test_modular_assembly_matches_canonical_program():
    source=ROOT/'packages/ordo_applied_project_factory/source'
    assembled=assemble(source/'module_manifest.yaml')
    canonical=yaml.safe_load((source/'program.ordo.yaml').read_text(encoding='utf-8'))
    assert assembled==canonical

def test_module_ownership_is_complete_and_unique():
    source=ROOT/'packages/ordo_applied_project_factory/source'
    manifest=yaml.safe_load((source/'module_manifest.yaml').read_text(encoding='utf-8'))
    owned=[]
    for module in manifest['modules']:
        owned.extend(module['owns_top_level_keys'])
    assert len(owned)==len(set(owned))
    canonical=yaml.safe_load((source/'program.ordo.yaml').read_text(encoding='utf-8'))
    assert set(owned)==set(canonical)
