# CSG-5 — Validation, Regression, and Specification Release

**Status:** normative integration artifact  
**Parent contract:** `ORDO-CAP-CSG-001`

## 1. Release rule

`Conversation Scope Guard` MUST NOT be released as a language-integrated specification until CSG-0 through CSG-4 specification validation reports pass and the cross-artifact consistency gate passes.

This gate does not claim toolchain execution, runtime enforcement, real-model benchmarking, or production readiness.

## 2. Validation layers

Required validation:

```text
contract validation
schema validation
taxonomy consistency
mode-policy consistency
state-protection consistency
authoring/package binding consistency
trace-event consistency
regression coverage
release manifest integrity
```

## 3. Cross-artifact invariants

The release validator MUST confirm:

```text
CSG remains optional
Core default remains disabled
APF self-guard remains disabled
all four canonical modes exist
all canonical deviation classes exist
unrelated_topic cannot mutate protected state
unclassifiable_input cannot mutate protected state
safety bypass remains available
control intents remain available
controlled suspension is not completion
exit defaults to exited_incomplete
enabled package binding requires contract, policy, tests, and trace artifacts
Profile recommendation does not activate CSG
Domain Pack constraint does not silently activate CSG
```

## 4. Required regression groups

```text
classification
strictness modes
escalation
state protection
response actions
pause/resume/exit
correction/backtracking/requirement change
safety bypass
authoring flow
package binding
manifest/source consistency
APF boundary
```

## 5. Release gate

```yaml
G_CSG_SPEC_RELEASE_READY:
  type: "blocking"
  requires:
    - "CSG_0_VALIDATION_REPORT.status == passed"
    - "CSG_1_VALIDATION_REPORT.status == passed"
    - "CSG_2_VALIDATION_REPORT.status == passed"
    - "CSG_3_VALIDATION_REPORT.status == passed"
    - "CSG_4_VALIDATION_REPORT.status == passed"
    - "CSG_FULL_REGRESSION_REPORT.status == passed"
    - "CSG_RELEASE_MANIFEST.integrity == passed"
```

## 6. Release status

Passing CSG-5 changes the specification status from:

```text
draft normative contract
```

to:

```text
language-integrated optional specification
```

This does not make CSG mandatory. It also does not make it toolchain-integrated, runtime-enforced, model-benchmarked, or production-recommended.

Legacy references to `G_CSG_RELEASE_READY` are interpreted as aliases for `G_CSG_SPEC_RELEASE_READY` only.

Additional readiness gates:

```text
G_CSG_TOOLCHAIN_READY
G_CSG_MODEL_BENCHMARK_READY
G_CSG_PRODUCTION_READY
```

## 7. Release artifacts

Canonical release set:

```text
CONVERSATION_SCOPE_GUARD_CONTRACT.md
conversation_scope_guard.contract.yaml
CSG_1_DEVIATION_CLASSIFICATION_CONTRACT.md
CSG_2_STRICTNESS_AND_ESCALATION_POLICY.md
CSG_3_RESPONSE_AND_STATE_PROTECTION_RULES.md
CSG_4_AUTHORING_FLOW_AND_PACKAGE_INTEGRATION.md
CSG_INTEGRATION_LINE.md
schemas/deviation_classification.schema.json
schemas/scope_guard_policy.schema.json
schemas/state_protection.schema.json
schemas/csg_package_binding.schema.json
CSG_1_CLASSIFICATION_REGRESSION_FIXTURES.yaml
CSG_2_ESCALATION_REGRESSION_FIXTURES.yaml
CSG_3_STATE_PROTECTION_REGRESSION_FIXTURES.yaml
CSG_4_PACKAGE_INTEGRATION_REGRESSION_FIXTURES.yaml
```

## 8. Diagnostics

```text
CSG501_PREREQUISITE_VALIDATION_FAILED
CSG502_CROSS_ARTIFACT_INVARIANT_FAILED
CSG503_REGRESSION_GROUP_MISSING
CSG504_RELEASE_MANIFEST_MISMATCH
CSG505_RELEASE_ARTIFACT_MISSING
CSG506_APF_BOUNDARY_REGRESSION
CSG507_OPTIONALITY_REGRESSION
```

All CSG-5 diagnostics are blocking.

## 9. Conformance

CSG-5 conforms when all prerequisite specification reports pass, all release artifacts exist, checksums are recorded, cross-artifact invariants pass, declarative fixture groups are represented, and `G_CSG_SPEC_RELEASE_READY` passes.
