# QA Automation Quality Evaluation Criteria

The automation specification must be implementation-ready and traceable to manual QA and the approved passport.

Required: suite purpose/scope; runner assumptions; defaults/shared configuration; stable source lookup; explicit case IDs; representative mapping to manual QA; case-local setup; input construction; action/invocation; expected-event assertions; explicit absence assertions for negative cases; error/side-effect assertions; cleanup/rollback; post-cleanup verification; deduplication/idempotency where required; limitations; live-run status separated from specification readiness; traceability.

Minimum required structure for every automated test:
1. `id` and `title`;
2. `requirement_refs` / passport references;
3. `manual_test_refs`;
4. `preconditions`;
5. `test_data`;
6. `setup`;
7. `action` or `invoke`;
8. `assertions`, including explicit absence assertions for negative cases;
9. `cleanup` or `rollback`;
10. `post_cleanup_assertions`;
11. `limitations` or environment dependencies where applicable.

Each automated case must make setup, action, assertions and cleanup understandable without inferring hidden steps from another case.

The automated test-case list must exactly correspond to the automated tests declared in the approved passport. Missing, extra, merged, or renamed cases require explicit justification and traceability.

Failure cap: a checklist/prose summary, automation without the minimum per-test structure, or automation without passport/manual-test correspondence cannot score above 50%.
