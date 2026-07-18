# Ordo v0.12 Opcode / Construct Catalog

## Program and metadata

| Construct | Type | Description |
|---|---|---|
| `PROGRAM.DEF` | op | Defines program metadata. |
| `GRAPH.CONTRACT` | op | Defines graph entry, terminal, cycle and transition-provenance contracts. |
| `CONTROL_LEVEL.DEF` | field/construct | Defines `light`, `standard`, or `strict`. |
| `EXECUTION.MODE` | field/construct | Defines `full_runtime`, `chat_internal`, or `freeform_only`. |

## Core execution

| Construct | Type | Description |
|---|---|---|
| `INTERACTION.MODEL` | op | Defines human/AI interaction roles and raw tool-output policy. |
| `PROCESS_RAIL.DEF` | op | Defines the Process Rail contract for guided AI execution. |
| `CONVERSATION.SEMANTICS` | op | Defines classification and routing rules for conversational input. |
| `HYBRID_EXECUTION.MODEL` | op | Defines AI-led execution with CLI as deterministic helper layer. |
| `INTENT.DEF` | op | Defines user goal. |
| `CONTRACT.DEF` | op | Defines expected result contract. |
| `CONTEXT.DEF` | op | Defines available context. |
| `STATE.SCHEMA` | op | Defines state structure. |
| `ENTRY.DEF` | op | Defines entry point. |
| `NODE.DEF` | op | Defines question/decision node. |
| `NODE.ASK` | op | Asks node question. |
| `CLARIFY.REQUEST` | op | Controlled clarification for unmatched input. |
| `PATH.DEF` | op | Defines execution path. |
| `STEP.RUN` | op | Runs a step. |
| `OUTPUT.DEF` | op | Defines allowed output. |
| `HANDOFF.DEF` | op | Defines handoff behavior. |

## Gates and assertions

| Construct | Type | Description |
|---|---|---|
| `GATE.DEF` | op | Defines gate. |
| `GATE.CHECK` | op | Evaluates gate. |
| `GATE.METHOD` | field/construct | Required method classification. |
| `ASSERTION.DEF` | op | Canonical assertion primitive. |
| `ASSERTION.PROJECT` | compiler action | Projects assertion to runtime/test/debug. |
| `ASSERT.NOT` | shortcut | Runtime projection of negative assertion. |
| `EXPECT.NOT` | test projection | Test projection of negative assertion. |

## Contract and artifact coverage

| Construct | Type | Description |
|---|---|---|
| `CONTRACT.INSTANCE` | op | Declares a first-class process contract instance with field statuses. |
| `CONTRACT.FIELD` | field/construct | Declares a typed field inside a contract. |
| `CONTRACT.STATUS` | field/construct | Declares field/contract status: missing, candidate, proposed, confirmed, blocked, not_applicable. |
| `ARTIFACT.DEF` | op | Declares a generated artifact target. |
| `ARTIFACT.REQUIREMENT` | op | Maps confirmed contract fields to required artifacts. |
| `COVERAGE.RULE` | op | Defines deterministic coverage policy. |
| `RENDERED_ARTIFACT.ASSERT` | op | Asserts that rendered artifact content contains required contract fields/sections. |
| `CONSISTENCY.REPORT` | op | Records cross-artifact consistency validation. |
| `GO_NO_GO.DECISION` | op | Records machine-readable readiness decision. |

## Debug/Test/Improvement

| Construct | Type | Description |
|---|---|---|
| `TRACE.LOG` | op | Records execution trace. |
| `TRACE.SOURCE` | field/construct | Declares trace source. |
| `DECISION.LOG` | op | Records decision. |
| `PATH.EXPLAIN` | op | Explains path selection. |
| `STATE.SNAPSHOT` | op | Records state snapshot. |
| `STATE.DIFF` | op | Records state diff. |
| `GATE.REPORT` | op | Records gate result. |
| `TEST.DEF` | op | Defines test. |
| `FIXTURE.DEF` | op | Defines test fixture. |
| `EXPECT.PATH` | op | Expected path. |
| `EXPECT.STATE` | op | Expected state. |
| `EXPECT.OUTPUT` | op | Expected output. |
| `EXPECT.GATE` | op | Expected gate result. |
| `REGRESSION.SUITE` | op | Regression suite. |
| `COVERAGE.REPORT` | op | Coverage report. |
| `IMPROVEMENT.RECORD` | op | Structured improvement record. |

## Libraries and layers

| Construct | Type | Description |
|---|---|---|
| `LIB.INCLUDE` | op | Includes library. |
| `LIB.USE` | op | Uses exports from library. |
| `VERSION.REQUIRE` | op/field | Requires version. |
| `NAMESPACE.RESOLVE` | compiler action | Resolves local IDs into namespaced IDs. |
| `LAYER.CONFLICT.CHECK` | op | Checks unresolved layer conflicts. |
| `OVERRIDE.DEF` | op | Defines explicit override. |

## FREEFORM

| Construct | Type | Description |
|---|---|---|
| `FREEFORM.DEF` | op | Defines controlled freeform block. |
| `FREEFORM.COVERAGE` | op | Coverage metadata for freeform. |
| `FREEFORM.MATURITY` | field/construct | Maturity lifecycle. |
| `FREEFORM.INCIDENT_COUNT` | field/construct | Incident counter. |
| `FREEFORM.FORMALIZATION.WARNING` | linter warning | Suggested formalization. |
| `TEMPLATE.RENDER_POLICY` | concept | Describes deterministic vs model-assisted rendering policy for output templates. |
| `MODEL_RENDER.HANDOFF` | runtime evidence | Records an AI rendering handoff packet for a model-assisted template. |


## Execution trace

- `EXECUTION_TRACE.DEF` — declares the canonical trace artifact contract for a run.
- `TRACE.EVENT.APPEND` — appends an immutable canonical event. Reserved for runtime/compiler integration in Part 2.


## Conversation Scope Guard

| Construct | Type | Description |
|---|---|---|
| `CONVERSATION.SCOPE.DEF` | op | Defines the optional conversation scope guard policy in Semantic JSON IR. |
| `DEVIATION.CLASSIFY` | op | Classifies a user message against the canonical deviation taxonomy. |
| `DEVIATION.HANDLE` | op | Selects the response and process-preservation action for a classified deviation. |
| `DEVIATION.ESCALATE` | op | Advances the explicit deviation escalation policy. |
| `STATE.PROTECT` | op | Protects process state from unauthorized mutation during deviation handling. |
| `PROCESS.PAUSE` | op | Pauses a process while preserving resumable state. |
| `PROCESS.RESUME` | op | Resumes a previously paused process. |
| `PROCESS.EXIT` | op | Exits a process with controlled incomplete terminal semantics. |
