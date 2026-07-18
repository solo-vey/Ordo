# BL-ORDO-002 Execution Plan

Status: completed

1. Revalidate the current APF graph contract.
2. Reproduce PathWalk cycle/dead-end blockers on the current APF source.
3. Make PathWalk graph-contract-aware: declared review loops are pruned as noncanonical routes; internal terminal nodes are terminal outcomes.
4. Enumerate canonical shortest routes to each terminal outcome to prevent combinatorial expansion.
5. Regenerate clean/noise testcase evidence.
6. Run affected regression, package lints, hygiene/sync gates, and non-destructive hash check.
7. Synchronize backlog, maturity, supersession registry, checksums, and archive.
