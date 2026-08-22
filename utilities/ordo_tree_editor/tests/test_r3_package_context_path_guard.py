
import importlib.util, tempfile, shutil
from pathlib import Path

spec=importlib.util.spec_from_file_location("editor_service_path_guard",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

# Exact regression class: long prose containing slash-like references must not become a path.
long_prompt=("Внутрішньо витягни лише факти з наданої відповіді та source_mapping / "
             "source_discrepancies. Не вигадуй значення. " + "дуже_довгий_текст "*1000)
assert not m._plausible_resource_path(long_prompt)
assert m._string_paths({"prompt":long_prompt})==[]

# Command line is not a resource path.
cmd="python tools/validate_applied_json_content.py --state runtime_state.json --output reports/runtime/out.json"
assert not m._plausible_resource_path(cmd)
assert m._string_paths({"question":cmd})==[]

# Genuine resource paths remain discoverable.
for value in [
    "reports/runtime/root_validation.json",
    "validators/validate_risk_factor_passport.py",
    "generated_outputs/RISK_FACTOR_PASSPORT.md",
    "contracts/VALIDATION_CONTRACT.json",
]:
    assert m._plausible_resource_path(value),value
    assert value in m._string_paths({"ref":value})

# Oversized single filename component is rejected before OS stat/resolve.
oversized="reports/" + ("x"*500) + ".json"
assert not m._plausible_resource_path(oversized)

# Context resolution itself must never raise on malformed/oversized prose.
old_active=m._active_playbook_package
old_runtime=m._runtime_workspace
tmp=Path(tempfile.mkdtemp())
try:
    m._active_playbook_package=lambda: {"resources":{}}
    m._runtime_workspace=lambda: tmp
    out=m._package_context_for_record({"question":long_prompt,"other":oversized})
    assert out=={"resolved_resources":[]}
finally:
    m._active_playbook_package=old_active
    m._runtime_workspace=old_runtime
    shutil.rmtree(tmp,ignore_errors=True)

print("PASS package-context path guard rejects prose/commands/oversized paths")
