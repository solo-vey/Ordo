# APF rc.12 — Concrete Playbook Intake Gate Policy

## Gate
`CONCRETE_PLAYBOOK_INTAKE_GATE`

This is an APF downstream-contract gate. It validates that the APF package contains a complete reusable intake and requirement-capture standard for future concrete playbook authoring. It does not conduct a real intake.

## Required artifacts
- `templates/CONCRETE_PLAYBOOK_INTAKE_CONTRACT.template.yaml`
- `templates/PLAYBOOK_REQUIREMENT_CAPTURE_MATRIX.template.yaml`
- `templates/INTAKE_ASSUMPTION_AND_UNKNOWN_REGISTER.template.yaml`
- `templates/PLAYBOOK_SCOPE_BOUNDARY_REGISTER.template.yaml`
- `templates/APF_CONCRETE_PLAYBOOK_INTAKE_COMPLETENESS_REPORT.template.json`

## Required contract rules
- Required intake fields are defined.
- Unknowns are distinct from assumptions and confirmed facts.
- Blocking gaps prevent decision-tree readiness.
- Critical requirements are traceable.
- Scope and layer ownership are explicit.

## Execution boundary
- No real intake is performed.
- No real domain is selected.
- No concrete decision tree or playbook package is created.
- No Ordo language/compiler/runtime changes are made.
