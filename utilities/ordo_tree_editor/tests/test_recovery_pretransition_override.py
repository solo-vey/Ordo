from pathlib import Path
p=Path(__file__).resolve().parents[1]/'editor_service.py'
s=p.read_text(encoding='utf-8')
checks={
 'payload read':'analyst_override_context = str(payload.get("analyst_override_context") or "").strip()',
 'enter-only injection':'if phase == "enter" and analyst_override_context:',
 'context field':'context["analyst_override_context"] = analyst_override_context',
 'non-authoritative rule':'It may refine requested content or coverage, but it MUST NOT override canonical state paths',
 'diagnostic length':'"analyst_override_chars": len(analyst_override_context)',
}
for name,needle in checks.items():
    assert needle in s, f'{name} missing'
print('recovery pre-transition override backend regression: PASS')
