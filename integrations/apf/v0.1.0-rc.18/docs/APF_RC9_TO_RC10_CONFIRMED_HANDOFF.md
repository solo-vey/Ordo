# APF rc.9 to rc.10 Confirmed Handoff

## Current accepted baseline

`v0.1.0-rc.9-confirmed-closure` is the current APF baseline.

## What rc.9 finalized

rc.9 finalized APF-level real-module testcase generation planning and utility packaging. It added a target manifest, scenario catalog, expected behavior matrix, generated testcase plan placeholder, coverage planning report, and a packaged APF testcase specification utility.

## Scope boundary to preserve

The testcase utility is APF-level only. It can generate testcase specifications, coverage reports, and expected behavior matrices. It must not run the Ordo compiler, execute Ordo runtime, modify the Ordo language package, or claim runtime test success without external evidence.

## Recommended next patch

`APF rc.10 — Package handoff readiness and consumer-start protocol`

Purpose: make the package easier and safer for the next model/human to consume by standardizing startup order, source-of-truth files, deferred items, accepted gates, and scope boundaries.
