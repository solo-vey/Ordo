# APF rc.8 — Gate Order Confirmation Policy

## Purpose

`GATE_ORDER_CONFIRMATION_GATE` checks whether the final APF gate order changed and whether the new order is dependency-safe.

## Gate ID

```text
Node ID: N_SHARED_TAIL_GATE_ORDER_CONFIRMATION_GATE
Gate name: GATE_ORDER_CONFIRMATION_GATE
```

## Trigger

Run this gate when APF changes:

```text
- canonical final tail
- shared tail
- package composition order
- archive assembly prerequisites
- position of any blocking gate
- order between profile, CLI discovery, evidence, hardening, package composition, and archive gates
```

## Dependency checks

The gate must verify:

```text
PACKAGE_PROFILE_GATE comes before checks that depend on package profile.
CLI_CAPABILITY_DISCOVERY_GATE comes after PACKAGE_PROFILE_GATE.
CLI evidence checks do not run before capability discovery.
EXTERNAL_CHECK_EVIDENCE_GATE runs after specialized external check gates.
PACKAGE_COMPOSITION_GATE runs after hardening/evidence gates.
FINAL_ARCHIVE_ASSEMBLY remains last.
```

## Required output

```text
previous_tail
new_tail
moved_gates
reason
impact
confirmation_status
```

## Fail-fast rule

If a new order causes a gate to run before its input exists, APF must mark the result as `blocked`.
