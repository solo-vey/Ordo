# APF rc.8 — Package Profile Change Confirmation Policy

## Purpose

`PACKAGE_PROFILE_CHANGE_CONFIRMATION_GATE` checks changes to package profile behavior and profile-dependent readiness rules.

## Gate ID

```text
Node ID: N_SHARED_TAIL_PACKAGE_PROFILE_CHANGE_CONFIRMATION_GATE
Gate name: PACKAGE_PROFILE_CHANGE_CONFIRMATION_GATE
```

## Trigger

Run when APF changes:

```text
- package_profile taxonomy
- runtime/source/hybrid behavior
- startup mode
- required startup files
- required external checks
- deferred evidence policy
- readiness statuses
- go/no-go behavior per package profile
```

## Required checks

```text
- old profile rule exists or is explicitly new
- new profile rule is stated
- affected profiles are named
- required/deferred checks are listed
- runtime-capable packages are not silently relaxed
- source/design packages do not receive false runtime readiness
```

## Result statuses

```text
passed
needs-human-confirmation
blocked
not-applicable
```
