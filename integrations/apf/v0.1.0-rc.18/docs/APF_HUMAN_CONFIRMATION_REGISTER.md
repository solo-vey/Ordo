# APF Human Confirmation Register

## Purpose

This register records explicit human confirmations for APF process-level changes.

It is the standard place to record decisions that affect nodes, gates, process rail, package profile, startup behavior, or readiness settings.

## Current rc.8 confirmation items

```text
APF-RC8-01 — no silent process mutation policy
APF-RC8-02 — NODE_CHANGE_IMPACT_REVIEW_GATE
APF-RC8-03 — GATE_ORDER_CONFIRMATION_GATE
APF-RC8-04 — PROCESS_RAIL_CHANGE_CONFIRMATION_GATE
APF-RC8-05 — PACKAGE_PROFILE_CHANGE_CONFIRMATION_GATE
APF-RC8-06 — APF_HUMAN_CONFIRMATION_REGISTER standard
APF-RC8-07 — conditional activation model for confirmation gates
```

## Record format

```text
CONFIRMED APF-RC8-xx:
<decision>

Reason:
<why accepted>

Impact:
<affected nodes/gates/settings>

Status:
confirmed / deferred / rejected
```

## Initial status for rc.8 package

```text
APF-RC8-01: proposed
APF-RC8-02: proposed
APF-RC8-03: proposed
APF-RC8-04: proposed
APF-RC8-05: proposed
APF-RC8-06: proposed
APF-RC8-07: proposed
```

These items should be confirmed step-by-step after the rc.8 package is reviewed.

---

# RC8 confirmed closure entries

```yaml
confirmations:
  - id: APF-RC8-01
    decision: accept no silent process mutation policy
    status: confirmed
    impact: process graph, gates, rail, profile, readiness changes must be explicit
  - id: APF-RC8-02
    decision: accept NODE_CHANGE_IMPACT_REVIEW_GATE
    status: confirmed
    impact: node additions/removals/renames/moves/semantic changes require review when triggered
  - id: APF-RC8-03
    decision: accept GATE_ORDER_CONFIRMATION_GATE
    status: confirmed
    impact: gate order/tail/dependency changes require review when triggered
  - id: APF-RC8-04
    decision: accept PROCESS_RAIL_CHANGE_CONFIRMATION_GATE
    status: confirmed
    impact: process rail/lifecycle/shared/final tail/go-no-go changes require review when triggered
  - id: APF-RC8-05
    decision: accept PACKAGE_PROFILE_CHANGE_CONFIRMATION_GATE
    status: confirmed
    impact: profile/readiness/status/artifact/evidence changes require review when triggered
  - id: APF-RC8-06
    decision: accept APF_HUMAN_CONFIRMATION_REGISTER standard
    status: confirmed
    impact: future process-changing patches must preserve explicit confirmation records
  - id: APF-RC8-07
    decision: accept conditional activation model
    status: confirmed
    impact: confirmation gates are not-applicable unless trigger present; required when trigger exists
```
