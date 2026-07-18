# Concrete playbook authoring protocol — template

> Reusable APF template only. Do not fill with a real domain inside the APF baseline.

1. Declare authoring mode.
2. Select latest confirmed APF baseline.
3. Perform problem-domain intake.
4. Define target user or analyst role.
5. Define the decision object.
6. Design the decision tree.
7. Define terminal paths.
8. Define node, gate and artifact-generation contracts.
9. Run Prompt Sufficiency Review for all relevant objects.
10. Create candidate mini-prompts only for `new_prompt_candidate` results.
11. Obtain explicit human decisions for all candidates and unresolved prompt questions.
12. Materialize only approved/reused prompts into the generated playbook registry, manifest and attachment map.
13. Validate prompt authority, checksums, attachments and mandatory test scenarios.
14. Map output artifacts and templates.
15. Create and obtain human confirmation for the Execution Trace design decision.
16. If trace is supported, generate trace config, schema, event mapping, redaction and replay policies.
17. If `runtime_mode: runtime_enforced`, generate the adapter contract and conformance evidence.
18. Run Execution Trace readiness validation.
19. Define remaining validation gates.
20. Plan non-prompt test cases.
21. Assemble the concrete package.
22. Validate the package.
23. Prepare handoff.

## Conditional prompt-package rule

Do not create an empty prompt package. Prompt-specific artifacts are generated only when review results require reuse, a new candidate, or a human decision.

## Boundary

The concrete package workflow must not mutate the APF baseline. APF improvement candidates must be transferred to a separate APF patch workflow. Mini-prompts created here belong to the downstream playbook, not to APF internal nodes.


## Conditional Execution Trace rule

Every playbook records a trace design decision. Runtime trace artifacts are generated only when `execution_trace.supported: true`. APF does not generate the actual trace; the target runtime does.

## Atomic Step Review

After drafting each step contract and before confirming the step:

1. Run Atomic Step Review against responsibility, output, input/output clarity, reconstruction, generation/validation separation, confirmation, transition completeness, failure localization, artifact statuses, and post-render review.
2. Persist an `ATOMIC_STEP_REVIEW_RECORD`.
3. For `recommendation`, show the advice and continue only with it recorded.
4. For `blocking_issue`, create a minimal-safe `ATOMIC_STEP_DECOMPOSITION_PROPOSAL` and block downstream authoring.
5. For `needs_human_decision`, pause and request a decision on the proposed structure.
6. After an approved split, rerun the review for every replacement step.

Prompt sufficiency analysis and execution-trace event mapping must use the post-ASR confirmed step structure.
