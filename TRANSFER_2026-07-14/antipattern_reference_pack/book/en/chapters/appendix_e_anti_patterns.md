# Appendix E. Anti-patterns

An anti-pattern is an approach that appears convenient or fast but makes an Ordo program less controllable, less verifiable, or less safe in real use.

This appendix does not replace a full playbook review. It is useful as a quick list of common mistakes before an Ordo program is handed over for use, a library is published, or a final package is assembled.

## E.1. One Large Prompt Instead of an Ordo Program

### Symptom

All logic is described in one large block of text without explicit `intent`, `contract`, `state`, `node`, `gate`, `output`, and `handoff` elements.

### Why This Is a Problem

The model may execute only part of the instruction, skip an important gate, confuse an example with a rule, or move to the final result before the process is actually ready.

### How to Fix It

Split the instruction into explicit parts:

```text
intent → contract → context → state → path → steps → gates → result → handoff
```

## E.2. Contract Hidden in Prose

### Symptom

The text contains phrases such as “obviously,” “when needed,” or “if everything is ready,” but does not define who confirms readiness or how confirmation is recorded.

### Why This Is a Problem

The model begins deciding by itself what is already confirmed, even when the user has not confirmed it.

### How to Fix It

Model the contract explicitly through `CONTRACT.DEF`, `ANSWER.REGISTRY`, `APPROVAL.REQUIRE`, and blocking gates.

## E.3. Gate Used as Advice

### Symptom

A gate is described as “it is recommended to check,” but the process can continue after the gate fails.

### Why This Is a Problem

Such a gate does not control execution. It only decorates the documentation.

### How to Fix It

Use a blocking gate for critical checks:

```text
if gate.failed → stop / ask / repair / no handoff
```

## E.4. Missing `ASSERT.NOT`

### Symptom

The Ordo program describes what must be done but does not describe what must not be done.

### Why This Is a Problem

The model may create an unnecessary file, invent a missing value, skip approval, or generate a final package in a situation where it should stop.

### How to Fix It

Add negative assertions:

```text
ASSERT.NOT final_output_before_approval
ASSERT.NOT invented_source_row
ASSERT.NOT hidden_required_gate_inside_freeform
```

## E.5. FREEFORM Used as a Dumping Ground

### Symptom

Everything that was difficult to formalize is placed in `FREEFORM`: gates, rules, status semantics, approval logic, templates, and prohibitions.

### Why This Is a Problem

FREEFORM stops being a controlled escape hatch and becomes the place where the real execution logic is hidden.

### How to Fix It

Keep in `FREEFORM` only what genuinely should not be formalized at the current stage. Move critical rules into `GATE.DEF`, `ASSERT.NOT`, `STATUS.SEMANTICS`, `OUTPUT.DEF`, or a library.

## E.6. Invisible Library Imports

### Symptom

The Ordo program uses rules or templates from a library, but this is not declared through `include`, `import`, or `use`.

### Why This Is a Problem

It becomes unclear where a rule came from, which library version was used, and who owns a behavior change.

### How to Fix It

Include every library explicitly:

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
    as: "contract_first"
```

## E.7. Override Without Permission

### Symptom

A Profile, Domain Pack, or Library silently rewrites a gate, status, or output rule defined in another layer.

### Why This Is a Problem

The behavior change becomes invisible. Existing tests may fail without an obvious cause.

### How to Fix It

Every override must be explicit and include a reason and trace:

```yaml
override:
  allow:
    - target: "G_PRE_ARCHIVE_APPROVAL"
      reason: "domain pack requires stricter approval gate"
```

## E.8. Testing Only the Final Text

### Symptom

Tests verify only the final response but do not verify path, state, gates, no-op behavior, or prohibited actions.

### Why This Is a Problem

The model may reach the correct result through an incorrect process. In production playbooks, this is unsafe.

### How to Fix It

Test behavior:

```text
EXPECT.PATH
EXPECT.STATE
EXPECT.GATE
EXPECT.OUTPUT
EXPECT.NOOP
EXPECT.NOT
```

## E.9. Missing Debug Trace

### Symptom

When the Ordo program behaves incorrectly, there is no record of the selected path, rejected paths, passed gates, or knowledge sources used.

### Why This Is a Problem

It is impossible to determine what failed: the instruction, domain rule, library, fixture, compiler, or model behavior.

### How to Fix It

For complex Ordo programs, run `debug` or `test` mode and retain:

```text
TRACE.LOG
DECISION.LOG
PATH.EXPLAIN
STATE.DIFF
GATE.REPORT
KNOWLEDGE.TRACE
```

## E.10. Feedback Lost in Chat

### Symptom

The user reports a problem or improvement, but it remains only in the conversation and is not converted into a structured improvement record.

### Why This Is a Problem

The same issue repeats. Instructions improve accidentally, without backlog, tests, or changelog history.

### How to Fix It

Use the `Feedback & Improvement Loop`:

```text
FEEDBACK.CAPTURE
→ ISSUE.RECORD
→ ROOT_CAUSE.LINK
→ PATCH.SUGGEST
→ TEST.SUGGEST
→ human approval
→ regression run
```

## E.11. All-in-One as the Source of Truth

### Symptom

A large assembled Markdown file is edited directly while the individual source files remain outdated.

### Why This Is a Problem

The build stops being reproducible. Different documentation versions begin contradicting one another.

### How to Fix It

Treat individual documents as the source of truth:

```text
section files / chapter files / domain pack files → all-in-one → PDF / archive
```

## E.12. Validating the Template Instead of the Rendered Artifact

### Symptom

The template or Markdown source is checked, but the actual PDF, archive, Jira task, or other assembled output is not checked.

### Why This Is a Problem

The failure may appear only during rendering or package generation: a broken link, missing file, wrong order, unclosed code block, or incorrect numbering.

### How to Fix It

Add `RENDER.VALIDATE` and inspect the actual result before handoff.

## E.13. “The Model Will Figure It Out”

### Symptom

The author does not explicitly define path selection, gates, outputs, or exceptions because the model is expected to “understand anyway.”

### Why This Is a Problem

The more complex the process, the more expensive incorrect model assumptions become.

### How to Fix It

Everything that matters for execution must be represented explicitly in Source or IR. If something is not formalized, it should be controlled `FREEFORM`, not a silent assumption.

## E.14. Overgrown Core

### Symptom

Domain-specific rules, templates for particular documents, or product-specific behavior are added to Core.

### Why This Is a Problem

Core loses universality. The language becomes harder to maintain and less portable across domains.

### How to Fix It

Keep Core minimal and move specialization into Profiles, Domain Packs, and Libraries.

## E.15. No Responsibility Boundary Between Model and Runner

### Symptom

It is unclear what the model decides, what the helper runner controls, and what requires human confirmation.

### Why This Is a Problem

A gate may be skipped, output may be created without approval, and the trace may not show who authorized a transition.

### How to Fix It

Separate responsibilities explicitly:

```text
model → semantic work
runner → process control / gates / state / tests
human → approval / governance / final decisions
```

## E.16. Quick Pre-handoff Check

Before handing over an Ordo program or package, quickly verify:

```text
- Is intent explicit?
- Is there a contract?
- Are gates hidden inside FREEFORM?
- Are blocking gates present before final output?
- Are ASSERT.NOT rules defined for prohibited actions?
- Are all libraries included explicitly?
- Is there a debug/test mode for complex logic?
- Is there a regression suite?
- Is feedback converted into improvement records?
- Was the actual rendered artifact checked?
```

Main rule:

```text
If behavior cannot be explained, verified, and reproduced, it is not yet an Ordo program; it is only a well-written prompt.
```

---

## E.17. False Deterministic Gate

### Symptom

A gate looks like a normal control point but has no `method`, or a semantic judgment is presented as if it were a mechanical check.

### Why This Is a Problem

The user sees `status: passed` but cannot tell whether the gate was checked by code or assessed by a model.

### How to Fix It

Every gate should define `method` and `trust_class`:

```yaml
gate:
  id: G_NO_UNSUPPORTED_FACTS
  method: self_verification
  trust_class: model_judgment
```

## E.18. Gate Without `method`

### Symptom

The program contains `GATE.DEF` or `GATE.CHECK`, but the verification method is not specified.

### Why This Is a Problem

The playbook author has not made an explicit choice between a mechanical check, model judgment, and human decision.

### How to Fix It

In v0.12, missing `gate.method` should be a compilation error.

## E.19. Trace Without `trace_source`

### Symptom

The debug trace shows selected path, state diff, and gate report but does not state whether the trace is a runtime log, hybrid trace, or model self-report.

### Why This Is a Problem

The trace may create unjustified confidence in the model's explanation.

### How to Fix It

Add:

```yaml
trace_source: model_self_report | runtime_enforced | hybrid
```

## E.20. Chat-only Mode Presented as Full Runtime

### Symptom

The process runs in chat without an external runner, but the documentation describes gates as though code enforced them.

### Why This Is a Problem

In `chat_internal`, code may check a gate, but the model still decides when to invoke that check.

### How to Fix It

Declare explicitly:

```yaml
execution_mode: chat_internal
```

and do not confuse it with:

```yaml
execution_mode: full_runtime
```

## E.21. One Prohibition Duplicated Manually in Three Places

### Symptom

The same prohibition is independently described as `ASSERT.NOT`, a negative gate, and `EXPECT.NOT`.

### Why This Is a Problem

Sooner or later, one of the three records will be updated while the others are not.

### How to Fix It

Describe the prohibition once as `ASSERTION`, then derive its runtime, test, and debug projections.

## E.22. Missing Fallback for Unmatched Input

### Symptom

`NODE.DEF` has `allowed_answers` but no `on_unmatched_input`.

### Why This Is a Problem

When the user gives an unexpected answer, the model returns to improvisation.

### How to Fix It

Add:

```yaml
on_unmatched_input:
  action: CLARIFY.REQUEST
  strategy: rephrase_and_narrow
  max_attempts: 2
```

## E.23. Local IDs in Feedback Records

### Symptom

An improvement record references `G1` or `N2` without identifying the layer or library that owns the ID.

### Why This Is a Problem

In a complex system, `G1` may exist in Core, Profile, Domain Pack, and Library at the same time.

### How to Fix It

Use only full namespaced IDs in feedback, traces, and reports.

## E.24. Floating Library Version

### Symptom

A library is included without a version, or with an overly broad version range in a strict process.

### Why This Is a Problem

Program behavior may change even when the source file does not.

### How to Fix It

Define a version policy and do not use floating versions in critical or strict workflows.

## E.25. FREEFORM Never Matures

### Symptom

The same FREEFORM block repeatedly produces feedback incidents but is never formalized.

### Why This Is a Problem

FREEFORM becomes a permanent gray area.

### How to Fix It

Add a maturity lifecycle:

```yaml
freeform:
  maturity: candidate_for_formalization
  incident_count: 3
  incident_threshold: 3
```

and create `FREEFORM_FORMALIZATION_RECOMMENDED`.

---

## E. Fundamental anti-pattern taxonomy

Individual detector cases are organized under a small stable set of fundamental failure classes. This prevents the registry from growing into hundreds of unrelated top-level rules.

1. `RESPONSIBILITY_CONFLATION`
2. `CONTROL_FLOW_INTEGRITY_VIOLATION`
3. `AUTHORIZATION_BOUNDARY_VIOLATION`
4. `EVIDENCE_REALITY_MISMATCH`
5. `STATUS_EVIDENCE_MISMATCH`
6. `INCOMPLETE_VALIDATION_MODEL`
7. `TRACEABILITY_AND_COVERAGE_LOSS`
8. `STATE_COHERENCE_VIOLATION`
9. `PROVENANCE_AND_AUTHORITY_VIOLATION`
10. `BOUNDARY_AND_OWNERSHIP_VIOLATION`
11. `IDENTITY_AND_UNIQUENESS_MODEL_FAILURE`
12. `POLICY_ENFORCEMENT_GAP`

A fundamental rule describes the broad invariant. A subpattern describes a recurring concrete failure. A detector case is a machine-checkable manifestation used by tests or runtime validation.

Adding another detector case does not create a new fundamental rule. A new fundamental-level anti-pattern requires separate owner approval and evidence that the existing taxonomy cannot represent the failure without distortion.
