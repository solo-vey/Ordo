# Appendix D. Checklists

This appendix contains practical checklists for working with Ordo programs. They can be used when creating a new playbook, reviewing an existing instruction, preparing a Domain Pack, connecting libraries, debugging, testing, or performing the final check before handoff.

A checklist in Ordo is not a substitute for gates or tests. It is a supporting tool for an author, analyst, or reviewer that helps prevent important parts of the process from being missed.

## D.1. Checklist: Is the Idea Ready for Ordo?

Before turning an instruction into an Ordo program, determine whether it actually contains a controllable process.

```text
[ ] There is a clear intent.
[ ] There is an expected result.
[ ] The model's responsibility boundaries are defined.
[ ] There are actions the model must not perform.
[ ] There are points that require human confirmation.
[ ] There are alternative execution paths.
[ ] There is data that must be collected before action.
[ ] There are rules that must not be skipped.
[ ] There is a final handoff or output.
[ ] There is an error risk that justifies formalization.
```

If most items are empty, this may not yet be an Ordo program; it may simply be a short request to a model.

If most items are satisfied, the process is a good candidate for Ordo.

## D.2. Intent Checklist

Intent should answer the question: what does the user actually want to obtain?

```text
[ ] Intent is expressed in one or more simple sentences.
[ ] Intent is not mixed with implementation details.
[ ] Intent contains no unconfirmed assumptions.
[ ] Intent is separated from the output format.
[ ] Intent is not replaced by a task title.
[ ] Intent does not describe a random example instead of the general goal.
[ ] Intent is understandable without reading the entire program.
```

Poor intent:

```text
Do it like in the previous example.
```

Better intent:

```text
Guide the user through controlled data collection for creating an analytical package for a historical event.
```

## D.3. Contract Checklist

The contract defines what must be confirmed before execution begins or before critical actions are performed.

```text
[ ] Required fields are known.
[ ] Decisions requiring user confirmation are known.
[ ] It is clear what counts as confirmed.
[ ] It is clear what must not be treated as confirmed.
[ ] Rules for an incomplete contract are defined.
[ ] A gate blocks further execution without a valid contract.
[ ] The contract is not silently constructed from model assumptions.
[ ] The contract is stored in state.
[ ] Contract changes are recorded as a state diff.
```

Critical rule:

```text
If the contract is not confirmed, the model must not behave as though it were confirmed.
```

## D.4. Context Checklist

Context includes the data, documents, rules, examples, and constraints required for correct execution.

```text
[ ] Documents that act as rule sources are identified.
[ ] Input data is identified.
[ ] Examples that are only examples are marked as such.
[ ] Context priority is defined.
[ ] Conflict-resolution behavior is defined.
[ ] Data that must not be invented is identified.
[ ] Sources that may be cited or used as evidence are identified.
[ ] Context is not mixed with state.
```

## D.5. State Checklist

State shows what is known, what is confirmed, what is awaiting a decision, and what is prohibited.

```text
[ ] State has an explicit schema.
[ ] State contains confirmed and pending values.
[ ] State does not mix facts with assumptions.
[ ] State is updated after every important step.
[ ] A state snapshot is available for debug mode.
[ ] A state diff records value changes.
[ ] Hidden conversational memory is not used instead of state.
[ ] Critical decisions are not lost inside response text.
```

Example of useful state:

```yaml
state:
  contract:
    alias:
      value: "LU_CHANGE_STATUS"
      status: "confirmed"

  approvals:
    pre_archive:
      status: "pending"

  execution:
    selected_path: "A1"
```

## D.6. Entry and Node Checklist

Entry and Node control the dialogue.

```text
[ ] There is a starting ENTRY.
[ ] Every NODE has a clear purpose.
[ ] Every NODE asks only necessary questions.
[ ] A NODE does not jump ahead.
[ ] A NODE has entry conditions.
[ ] A NODE has exit conditions.
[ ] A NODE updates state.
[ ] A NODE knows where to transition next.
[ ] Rules exist for ambiguous user answers.
[ ] Rules exist for revising a previous decision.
```

Poor:

```text
Ask the user everything that is needed.
```

Better:

```yaml
node:
  id: "N_COLLECT_ALIAS"
  asks:
    - "Confirm the event alias."
  writes:
    - "state.contract.alias"
  next:
    when_confirmed: "N_COLLECT_SOURCE_FIELD"
```

## D.7. Path Checklist

A Path is needed when the same intent can be fulfilled through different routes.

```text
[ ] All primary paths are listed.
[ ] Selection conditions are defined for each path.
[ ] Each path has a reason.
[ ] Debug mode records rejected paths and reasons.
[ ] Ambiguity handling is defined.
[ ] Risky paths require a gate or user approval.
[ ] A path is not selected based on model intuition alone.
[ ] Path selection can be tested.
```

## D.8. Gate Checklist

A Gate is a control point, not advice.

```text
[ ] The gate has an id.
[ ] The gate has a pass condition.
[ ] The gate has a status.
[ ] The gate has evidence.
[ ] The consequence of fail/block is defined.
[ ] It is clear whether the gate is blocking.
[ ] The gate cannot pass without required data.
[ ] The gate is not hidden inside FREEFORM.
[ ] The gate appears in the debug trace.
[ ] The gate has a test or coverage.
```

Critical rule:

```text
If a gate is blocking, the model must not continue the action that the gate blocks.
```

## D.9. ASSERT.NOT Checklist

Negative assertions prevent unsafe actions.

```text
[ ] Actions the model must not perform are listed.
[ ] Every prohibited action has an ASSERT.NOT.
[ ] ASSERT.NOT is linked to a specific risk.
[ ] ASSERT.NOT is checked before output.
[ ] ASSERT.NOT has a test.
[ ] ASSERT.NOT is not replaced by a soft recommendation.
```

Examples:

```text
[ ] Do not create the final archive before approval.
[ ] Do not invent a source row.
[ ] Do not treat an example as a confirmed rule.
[ ] Do not change the contract without confirmation.
```

## D.10. Output Checklist

Output must be explicit and verifiable.

```text
[ ] The output type is defined.
[ ] The output format is defined.
[ ] Mandatory output parts are defined.
[ ] Excluded output content is defined.
[ ] Required pre-output gates are defined.
[ ] Output can be checked through validation.
[ ] Output includes a handoff note or next action.
[ ] Output is not created before the permitted point.
```

## D.11. FREEFORM Checklist

FREEFORM is useful for complex semantic content, but it must remain controlled.

```text
[ ] FREEFORM has an id.
[ ] There is a reason why this part is not formalized.
[ ] Purpose is defined.
[ ] Binding is defined.
[ ] Usage locations are identified.
[ ] It is clear what FREEFORM cannot override.
[ ] Coverage or a coverage plan exists.
[ ] No hidden gates exist inside FREEFORM.
[ ] No hidden statuses exist inside FREEFORM.
[ ] No rules remain that should be moved into Core, Profile, or Domain Pack.
```

## D.12. Debug Checklist

Debug mode should explain execution rather than merely repeat the final response.

```text
[ ] There is a run_id.
[ ] There is an input snapshot.
[ ] The selected path is recorded.
[ ] Rejected paths and reasons are recorded.
[ ] There is a decision log.
[ ] There are state snapshots.
[ ] There are state diffs.
[ ] There is a gate report.
[ ] There is a knowledge trace.
[ ] Warnings are recorded.
[ ] Violations are recorded.
[ ] A failure explanation exists when the process fails.
```

The debug trace should answer:

```text
Why did the model do this?
```

## D.13. Test Checklist

Tests should verify Ordo-program behavior, not only final wording.

```text
[ ] TEST.DEF exists.
[ ] FIXTURE.DEF exists.
[ ] Expected path is defined.
[ ] Expected state is defined.
[ ] Expected gates are defined.
[ ] Expected output is defined.
[ ] EXPECT.NOT covers prohibited actions.
[ ] No-op tests exist.
[ ] Negative tests exist.
[ ] Edge-case tests exist.
[ ] Tests exist for FREEFORM-backed decisions.
```

## D.14. Regression Suite Checklist

A regression suite is required before changes are released.

```text
[ ] A baseline scenario set exists.
[ ] Scenarios exist for every path.
[ ] Scenarios exist for blocking gates.
[ ] No-op scenarios exist.
[ ] Invalid or incomplete input scenarios exist.
[ ] Library scenarios exist.
[ ] Domain Pack scenarios exist.
[ ] The regression suite runs before release.
[ ] Regression results are recorded in a report.
```

## D.15. Coverage Checklist

Coverage shows how much of the Ordo program is actually controlled and verified.

```text
[ ] All primary paths are covered.
[ ] All blocking gates are covered.
[ ] All critical ASSERT.NOT rules are covered.
[ ] All output types are covered.
[ ] All status transitions are covered.
[ ] No-op scenarios are covered.
[ ] Critical FREEFORM blocks are covered.
[ ] Imported libraries are covered.
[ ] Uncovered areas are listed.
[ ] A coverage improvement plan exists.
```

## D.16. Feedback and Improvement Loop Checklist

When a user reports a problem, it should become a structured record.

```text
[ ] Feedback is captured.
[ ] The original user message is recorded.
[ ] The problem is classified.
[ ] Severity is recorded.
[ ] The affected unit is identified.
[ ] A root-cause hypothesis exists.
[ ] A proposed patch exists.
[ ] A suggested test exists.
[ ] Required approval is identified.
[ ] A version note or changelog item exists.
[ ] A regression test is added after the fix.
```

Feedback must not disappear inside chat history.

## D.17. Ordo Library Checklist

Connected libraries require control over version, namespace, and conflicts.

```text
[ ] The library is included explicitly.
[ ] The version is pinned.
[ ] An alias or namespace is defined.
[ ] Used exports are identified.
[ ] A compatibility check has been performed.
[ ] Conflicts have been checked.
[ ] Override is allowed only explicitly.
[ ] There are no implicit imports.
[ ] A trust level is defined.
[ ] The library is covered by tests or has its own test pack.
```

Poor:

```yaml
include:
  - "ordo.qa"
```

Better:

```yaml
include:
  - library: "ordo.qa.manual_runbook"
    version: "0.1"
    as: "manual_qa"
```

## D.18. Domain Pack Checklist

A Domain Pack should describe domain logic, not a random collection of examples.

```text
[ ] Domain vocabulary exists.
[ ] Domain-specific paths exist.
[ ] Domain-specific gates exist.
[ ] Domain-specific statuses exist.
[ ] Domain-specific output templates exist.
[ ] Mapping to Ordo Core exists.
[ ] Controlled FREEFORM is used for complex edge cases.
[ ] Domain tests exist.
[ ] A coverage report exists.
[ ] An improvement loop exists.
```

## D.19. Legacy Playbook Migration Checklist

```text
[ ] The old playbook has been split into logical parts.
[ ] Intent has been identified.
[ ] Contract has been identified.
[ ] The decision tree has been identified.
[ ] Paths have been identified.
[ ] Nodes have been identified.
[ ] Gates have been identified.
[ ] Statuses have been identified.
[ ] Outputs have been identified.
[ ] Handoff has been identified.
[ ] FREEFORM blocks have been identified.
[ ] Reusable libraries have been identified.
[ ] Semantic JSON IR has been built.
[ ] Test cases have been created.
[ ] A coverage report has been created.
[ ] A consistency check has been completed.
```

## D.20. Final Handoff Checklist

Before handing an Ordo program or package over for use, verify:

```text
[ ] All mandatory sections are present.
[ ] No blocking gates remain unresolved.
[ ] No contract fields remain pending.
[ ] No conflicts remain unresolved.
[ ] No implicit assumptions remain.
[ ] No hidden rules remain in FREEFORM.
[ ] A debug trace can be obtained.
[ ] The regression suite passed, or its absence is stated honestly.
[ ] A coverage report has been produced.
[ ] Improvement records were addressed or moved to backlog.
[ ] The version note was updated.
[ ] The handoff note was written.
```

## Brief Summary

Checklists do not automatically make an Ordo program correct. They help authors avoid missing the core elements:

```text
intent
contract
context
state
path
node
gate
assertion
output
debug
test
coverage
feedback
library
domain pack
handoff
```

If an Ordo program passes these checklists, it is not only readable; it can also be maintained, tested, improved, and handed to other people or systems.

---

## D.22. Ordo v0.12 Reliability Checklist

Use this checklist after upgrading a program or playbook to Ordo v0.12.

```text
[ ] Every gate has a mandatory method field.
[ ] Every gate defines trust_class.
[ ] Mechanical gates are not mixed with semantic model-judgment gates.
[ ] Gates with method: self_verification have an evidence protocol.
[ ] Critical semantic gates use a generator/critic or self_consistency pattern.
[ ] Gate reports show method and trust_class.
[ ] Execution traces include trace_source.
[ ] The Ordo program defines execution_mode.
[ ] Documentation does not imply that model_self_report equals a runtime_enforced log.
[ ] ASSERT.NOT is described as a shortcut/projection of ASSERTION.
[ ] Critical prohibitions are modeled as ASSERTION with phase: [runtime, test].
[ ] EXPECT.NOT is derived from ASSERTION projection rather than manually duplicating ASSERT.NOT.
[ ] NODE defines on_unmatched_input or an explicit fallback.
[ ] Unmatched input is handled through CLARIFY.REQUEST.
[ ] The node_coverage_gap feedback class is used for recurring uncovered answers.
[ ] Program defines control_level: light / standard / strict.
[ ] A strict program has regression coverage for mandatory gates and assertions.
[ ] Trace, gate_report, and improvement_record use namespaced IDs.
[ ] Includes define a version.
[ ] Layer priority is defined and respected.
[ ] Override is explicit and includes a reason.
[ ] No unresolved layer conflicts remain.
[ ] FREEFORM blocks define maturity.
[ ] FREEFORM incident_count and incident_threshold are defined for risky blocks.
[ ] FREEFORM blocks exceeding the threshold produce a formalization warning or improvement record.
```

## D.23. gate.method Checklist

```text
[ ] method: mechanical is used only for deterministic checks.
[ ] method: self_verification is used for semantic model judgments supported by evidence.
[ ] method: self_consistency is used for critical repeated model checks.
[ ] method: human is used for human decisions.
[ ] Examples contain no GATE.CHECK without method.
[ ] gate_report contains no status: passed without method/trust_class explanation.
```

## D.24. execution_mode Checklist

```text
[ ] full_runtime is used only where a runner actually controls transitions.
[ ] chat_internal is honestly described as an intermediate mode.
[ ] freeform_only is not presented as fully controlled execution.
[ ] In chat_internal, documentation states that gate invocation is not enforceable without an external runtime.
[ ] chat_internal defines state_backing or another mechanism for reducing state drift.
[ ] Strict processes do not use freeform_only without a dedicated warning.
```

## D.25. ASSERTION Checklist

```text
[ ] Prohibitions are modeled through ASSERTION.
[ ] Every ASSERTION defines polarity.
[ ] Every ASSERTION defines phase.
[ ] A blocking assertion uses severity: block.
[ ] Runtime projection creates ASSERT.NOT or a gate.
[ ] Test projection creates EXPECT.NOT.
[ ] Debug projection creates a violation record.
[ ] The regression suite verifies critical assertions.
```

## D.26. Namespace, Version, and Layer-Priority Checklist

```text
[ ] Source may use local IDs, but IR uses full namespaced IDs.
[ ] All improvement records reference namespaced IDs.
[ ] All libraries define a version.
[ ] Floating versions are not used for strict processes.
[ ] Core is not overridden by a lower layer without explicit override.
[ ] Domain Pack does not silently change Profile.
[ ] A Library does not silently change Domain Pack.
[ ] FREEFORM cannot override a formal rule.
[ ] G_NO_UNRESOLVED_LAYER_CONFLICT is present for complex programs.
```
