from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_integrated_compilation_ui_contract():
    html=(ROOT/'web/index.html').read_text()
    js=(ROOT/'web/app.js').read_text()
    css=(ROOT/'web/styles.css').read_text()
    assert 'Upload Playbook' in html
    assert '.yaml,.yml,.zip' in html
    assert 'Preparing Playbook' in html
    assert 'beginPlaybookPreparation' in js
    assert 'finishPlaybookPreparation' in js
    assert 'Playbook could not be started' in js
    assert 'compiled and verified internally' in js
    assert '.playbook-preparation-overlay' in css
