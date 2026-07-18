# S02 Branch-Heavy Comparative Finding

Ordo completed the branch-heavy scenario with correct independent branch and loop routing.

The instruction-only executor processed all 36 Driver events and tracked repeated occurrences, but selected the wrong next step at two critical decision points:

- Critical supplier replacement should have routed back to the design/procurement stage, but the executor advanced to the people plan.
- Blocked readiness should have routed to remediation, but the executor advanced to pilot day.

The Driver subsequently imposed the expected route. Therefore the final completion does not demonstrate independent instruction-only control-flow correctness.

Composite scores: Ordo 98; instruction-only 81.
