# Manual QA Package Quality Evaluation Criteria

The manual QA package must be an executable tester runbook.

Required: prerequisites/environment assumptions; exact reference data and stable lookup; endpoints/tools; focused reads/projections; individually identified positive, negative, normalization, no-op, missing-data and relevant regression cases; exact setup; action/mutation; trigger/invocation; verification; concrete expected values; explicit absence/error assertions; rollback for every mutating case; post-rollback verification; limitations and execution-readiness status.

Every test case must independently contain the complete reproducible command sequence that a tester can execute step by step without referring to shared or general document sections. Placeholders may be used only when their values are explicitly obtained from a preceding operation in that same test case.

Every test case must independently state: purpose, test data, preconditions, setup commands, action commands, trigger/invocation commands, verification commands, expected result, absence/error assertions where applicable, rollback commands, and rollback verification.

The manual test-case list must exactly correspond to the manual tests declared in the approved passport. Missing, extra, merged, or renamed cases require explicit justification and traceability.

Failure cap: Input/Expected/Cleanup tables, references to shared command blocks instead of case-local commands, or cases requiring the tester to reconstruct missing commands cannot score above 50%.
