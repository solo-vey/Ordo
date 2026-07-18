# BL-ORDO-025 Closure Report

Status: `closed`

APF linter hardening replaces recursive/unbounded graph processing with bounded partition refinement and iterative SCC traversal. Full APF lint is mandatory under a standard-CI budget of 512 MiB peak RSS and 15 seconds; `--skip-heavy` is now a compatibility no-op.

Evidence: 17/17 affected tests, 4/4 performance tests, 4/4 package lints, 0 blockers.
