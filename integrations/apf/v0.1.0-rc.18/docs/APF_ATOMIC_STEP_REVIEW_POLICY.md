# APF Atomic Step Review Policy

APF performs Atomic Step Review after a draft process structure exists and before final generated-playbook validation.

The review inspects responsibilities, outputs, validation, confirmation, state transitions, reconstruction, and failure routing. APF records findings and proposes a minimal safe decomposition.

A recommendation must identify:

- the mixed responsibilities;
- the independent outputs or statuses;
- the concrete risk;
- the proposed replacement steps;
- the required confirmation point;
- the nearest valid failure route.

APF must distinguish mechanical grouping from semantic grouping. Mechanical transformations of one confirmed source may remain in one step when they create one result and share one completion criterion.

APF must not treat file presence, schema presence, or a generation plan as proof that a usable artifact exists.


## ASR-1 review record

Every reviewed step must produce a structured review record conforming to `docs/APF_ATOMIC_STEP_REVIEW_CONTRACT.yaml`.

The record must preserve evidence, per-dimension results, findings, proposed decomposition, transition decision, and any required human decision. A recommendation does not block progression; a `blocking_issue` does. `needs_human_decision` pauses progression until the decision is recorded.

A proposed decomposition must preserve confirmed inputs and business rules. If it changes ownership, approval authority, business semantics, or confirmed-state transitions, `semantic_change` must be `true` and human approval is mandatory.

## ASR-2 gates and severity

Gate definitions are normative in `docs/APF_ATOMICITY_GATE_CONTRACT.yaml`. Severity evaluation and escalation are normative in `docs/APF_ATOMICITY_SEVERITY_RULES.yaml`.

Every failed or unclear gate must emit a diagnostic code, evidence references, transition effect, and corrective action. Any blocked gate makes the whole step `blocking_issue`. Human review is required only where business semantics, ownership, approval authority, or multiple valid decompositions cannot be resolved deterministically.
