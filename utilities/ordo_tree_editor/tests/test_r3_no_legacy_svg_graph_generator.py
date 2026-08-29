from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_legacy_visual_graph_generator_removed_from_editor_package():
    assert not (ROOT / 'verification' / 'checks' / '090_graph_render.json').exists()
    assert not (ROOT / 'verification' / 'toolkit' / 'utilities' / 'ordo_visual_graph_generator').exists()


def test_editor_native_svg_export_is_preserved_without_legacy_generator():
    html = (ROOT / 'web' / 'index.html').read_text(encoding='utf-8')
    js = (ROOT / 'web' / 'app.js').read_text(encoding='utf-8')
    assert 'canvas-download-svg' in html
    assert 'Download current graph as SVG' in html
    assert 'downloadTreeSvg' in js
    assert 'ordo-tree.svg' in js
    assert 'source-flow-context-download-svg' in html
    assert 'downloadSourceFlowSvg' in js
    assert 'ordo-data-flow.svg' in js
    assert 'ordo_visual_graph_generator' not in js


def test_verification_toolkit_manifests_do_not_reference_removed_generator():
    for rel in ['verification/toolkit/MANIFEST.json', 'verification/TOOLKIT_SNAPSHOT_MANIFEST.json']:
        data = json.loads((ROOT / rel).read_text(encoding='utf-8'))
        paths = [item.get('path', '') for item in data.get('files', [])]
        assert not any('ordo_visual_graph_generator' in path for path in paths)
