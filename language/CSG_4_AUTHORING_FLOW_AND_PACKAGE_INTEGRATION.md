# CSG-4 — Authoring-Flow and Package Integration

**Status:** normative integration artifact  
**Parent contract:** `ORDO-CAP-CSG-001`

## 1. Rule

A playbook authoring process MAY design `Conversation Scope Guard` for the generated process.

The guard MUST NOT be enabled merely because the authoring system supports it.

For APF:

```yaml
conversation_scope_guard:
  enabled: false
```

APF designs the capability for generated playbooks but does not use CSG as a mandatory guard for its own authoring dialogue.

## 2. Authoring-flow position

Canonical position:

```text
process rail confirmed
→ conversation deviation policy design
→ human confirmation
→ CSG source generation
→ CSG validation and tests
→ package assembly
```

CSG design MUST occur before final package assembly.

## 3. Design phase

Canonical phase:

```text
CONVERSATION_DEVIATION_POLICY_DESIGN
```

The phase determines:

```text
guard required or not
declared conversation scope
strictness mode
accepted process intents
deviation taxonomy extensions
escalation counter scope
escalation reset rules
response actions
pause/resume/exit behavior
state-protection targets
trace requirements
regression requirements
```

## 4. Minimum authoring questions

The authoring process SHOULD resolve:

```text
1. Does this process require conversation-scope control?
2. How broad is the allowed conversation scope?
3. May the process briefly answer unrelated questions?
4. Which strictness mode is appropriate?
5. Which messages count as related context?
6. How should repeated unrelated messages escalate?
7. When should pause or exit be offered?
8. Which state must never change because of unrelated input?
9. Which trace events are required?
10. Which regression cases must be generated?
```

These questions MAY be resolved from existing process contracts when evidence is explicit.

## 5. Applicability recommendation

APF SHOULD recommend CSG when the generated process has one or more of:

```text
guided intake
persistent process state
decision-tree path selection
blocking gates
long-running dialogue
expensive state transitions
regulated interaction
high-discipline package generation
```

APF SHOULD normally recommend CSG as unnecessary for:

```text
single-turn transformation
simple rewrite
open brainstorming
casual conversation
stateless question answering
```

Recommendation is not activation.

## 6. Human confirmation gate

Before generating enabled CSG artifacts:

```yaml
G_CSG_POLICY_CONFIRMED:
  type: "blocking"
  requires:
    - "csg.required_decision_confirmed"
    - "csg.mode_confirmed"
    - "csg.scope_confirmed"
    - "csg.escalation_confirmed"
    - "csg.state_protection_confirmed"
```

If CSG is explicitly not required, the gate records:

```yaml
csg:
  enabled: false
  decision_status: "confirmed_not_required"
```

## 7. Generated package artifacts

When CSG is enabled, the generated playbook package SHOULD contain:

```text
conversation_scope_guard.contract.yaml
conversation_deviation_policy.md
conversation_scope_guard_tests.yaml
conversation_scope_guard_trace_events.yaml
```

A compact package MAY embed these in existing canonical files if bindings remain explicit.

## 8. Source generation

Recommended generated source:

```yaml
conversation_scope_guard:
  supported: true
  enabled: true
  mode: "guided_redirect"

  scope:
    process_id: "PROCESS_ID"
    active_node_ref: "STATE.current_node"
    active_question_ref: "STATE.current_question"

  out_of_scope_behavior:
    answer_external_question: false
    acknowledge_message: true
    repeat_active_question: true
    preserve_state: true
    complete_active_node: false
    change_selected_path: false
    confirm_state_value: false

  escalation:
    counter_scope: "active_node"
    reset_on:
      - "valid_process_answer"
      - "node_transition"
      - "process_resume"

  trace:
    required: true
```

## 9. Profile and Domain Pack binding

A Profile MAY define a recommended CSG policy:

```yaml
profile:
  id: "guided_intake"
  recommends:
    conversation_scope_guard:
      mode: "guided_redirect"
```

A Domain Pack MAY tighten policy:

```yaml
domain_pack:
  id: "regulated_claim_intake"
  constraints:
    conversation_scope_guard:
      minimum_mode: "strict_redirect"
```

A Domain Pack MUST NOT silently enable CSG. Activation remains explicit in the playbook contract.

## 10. Package manifest binding

Package manifest SHOULD declare:

```yaml
capabilities:
  conversation_scope_guard:
    supported: true
    enabled: true
    contract: "conversation_scope_guard.contract.yaml"
    policy: "conversation_deviation_policy.md"
    tests: "conversation_scope_guard_tests.yaml"
    trace_events: "conversation_scope_guard_trace_events.yaml"
```

If disabled:

```yaml
capabilities:
  conversation_scope_guard:
    supported: true
    enabled: false
    decision_status: "confirmed_not_required"
```

## 11. Generated regression suite

When enabled, package generation MUST include tests for:

```text
valid active answer
clarification
correction
backtrack request
requirement change
pause
resume
exit
process meta-question
related context
first unrelated topic
repeated unrelated topic
unclassifiable input
safety bypass
state preservation
path preservation
gate preservation
counter reset
controlled suspension
```

## 12. Package assembly gate

Before assembly:

```yaml
G_CSG_PACKAGE_READY:
  type: "blocking"
  when: "conversation_scope_guard.enabled == true"
  requires:
    - "G_CSG_POLICY_CONFIRMED == passed"
    - "csg.contract.valid == true"
    - "csg.policy.valid == true"
    - "csg.tests.generated == true"
    - "csg.trace_bindings.valid == true"
```

If CSG is disabled, package assembly MUST NOT require enabled-CSG artifacts.

## 13. Rendered artifact validation

Package validation MUST check:

```text
manifest capability status matches source declaration
mode matches resolved policy
state-protection assertions are present
escalation actions are defined
pause/resume/exit bindings exist
trace events are declared when required
tests cover CSG invariants
disabled CSG does not appear as active runtime behavior
```

## 14. APF boundary

APF integration is limited to:

```text
recommend capability
design policy
request confirmation
generate artifacts
generate tests
validate package integration
```

APF MUST NOT:

```text
force CSG into every playbook
enable CSG without confirmation
use generated playbook CSG policy as APF's own dialogue guard
treat recommendation as activation
```

## 15. Diagnostics

```text
CSG401_POLICY_PHASE_SKIPPED
CSG402_ACTIVATED_WITHOUT_CONFIRMATION
CSG403_PACKAGE_ARTIFACT_MISSING
CSG404_MANIFEST_SOURCE_MISMATCH
CSG405_PROFILE_BINDING_INVALID
CSG406_DOMAIN_PACK_SILENT_ACTIVATION
CSG407_TEST_SUITE_MISSING
CSG408_TRACE_BINDING_MISSING
CSG409_DISABLED_GUARD_RENDERED_ACTIVE
CSG410_APF_SELF_GUARD_ENABLED_BY_GENERATED_POLICY
```

Blocking diagnostics:

```text
CSG402
CSG403
CSG404
CSG406
CSG407
CSG408
CSG409
CSG410
```

## 16. Conformance

CSG-4 conforms when:

- CSG design is an explicit pre-assembly authoring phase;
- activation requires an explicit decision;
- enabled CSG produces bound package artifacts;
- disabled CSG does not require active artifacts;
- Profiles may recommend but not silently activate;
- Domain Packs may constrain but not silently activate;
- package manifest records capability status;
- regression tests are generated when enabled;
- package validation checks CSG consistency;
- APF does not inherit the generated playbook's guard.
