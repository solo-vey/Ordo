from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_graph_context_menus_are_available_for_tree_path_and_data_flow():
    html = (ROOT / 'web' / 'index.html').read_text(encoding='utf-8')
    js = (ROOT / 'web' / 'app.js').read_text(encoding='utf-8')
    assert 'id="canvas-general-actions"' in html
    assert 'id="canvas-download-svg"' in html
    assert 'id="source-flow-context-menu"' in html
    assert 'id="source-flow-context-download-svg"' in html
    assert 'if (!state.source) return;' in js
    assert 'state.panelTab !== "dialog"' not in js[js.index('function showCanvasContextMenu'):js.index('function disconnectedNodeTemplate')]
    assert 'vp?.addEventListener("contextmenu",showSourceFlowContextMenu)' in js
    for token in ['source-flow-context-fit','source-flow-context-auto','source-flow-context-tb','source-flow-context-lr']:
        assert token in html
