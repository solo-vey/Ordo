from pathlib import Path

SERVICE = Path(__file__).resolve().parents[1] / "editor_service.py"

def test_provider_capability_probe_is_post_allowlisted_and_handled():
    text = SERVICE.read_text(encoding="utf-8")
    allowlist_block = text[text.index('if path not in {'):text.index('try:', text.index('if path not in {'))]
    assert '"/api/provider-capability-probe"' in allowlist_block
    assert 'if path == "/api/provider-capability-probe":' in text
