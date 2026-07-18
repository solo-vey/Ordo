# APF rc.8 — No Silent Process Mutation Policy

## Status

```text
status: accepted-for-rc8
scope: APF package/playbook creation process only
language_package_changes: forbidden
```

## Rule

APF must not silently mutate the playbook-authoring process graph, shared tail, gate order, package profile, startup behavior, evidence policy, or readiness model.

Any change that affects execution behavior must be surfaced before final readiness.

## Required disclosure

For every process-affecting change APF must show:

```text
old state / previous rule
new state / proposed rule
reason
affected nodes / gates / settings
impact classification
confirmation status
```

## Blocking behavior

A process-affecting change may not be hidden inside README text, validation narrative, or a generated artifact without a confirmation record.

If confirmation is missing, APF must mark the package as:

```text
needs-human-confirmation
```

rather than `ready/go`.

## Out of scope

This policy does not implement Ordo language, runtime, compiler, or CLI changes. It only governs how APF records and confirms its own process changes.
