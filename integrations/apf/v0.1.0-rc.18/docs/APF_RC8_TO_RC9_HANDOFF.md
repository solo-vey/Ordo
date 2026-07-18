# APF rc.8 → rc.9 Handoff

## Current rc.8 scope

APF rc.8 adds a process-change confirmation layer for playbook authoring and package-generation changes.

It does not implement Ordo language package, compiler, runtime, or CLI behavior.

## Baseline after rc.8

```text
APF_TRANSFER_PACKAGE_CURRENT_STATE_RC8_NODE_CHANGE_CONFIRMATION.zip
```

## Expected human confirmations after rc.8

```text
APF-RC8-01 — no silent process mutation policy
APF-RC8-02 — NODE_CHANGE_IMPACT_REVIEW_GATE
APF-RC8-03 — GATE_ORDER_CONFIRMATION_GATE
APF-RC8-04 — PROCESS_RAIL_CHANGE_CONFIRMATION_GATE
APF-RC8-05 — PACKAGE_PROFILE_CHANGE_CONFIRMATION_GATE
APF-RC8-06 — APF_HUMAN_CONFIRMATION_REGISTER standard
APF-RC8-07 — conditional activation model
```

## Candidate rc.9 direction

After rc.8 is confirmed, the next APF patch should likely focus on:

```text
APF rc.9 — Playbook package template/intake coverage enforcement hardening
```

Potential scope:

```text
- ensure every generated package document has a template
- ensure every template required field maps to intake/source/default/open-question
- make tree × template coverage visible before final package generation
- add template coverage evidence to validation report
```
