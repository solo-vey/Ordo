# Compile and coverage checks for contract → artifact mapping

M46.2 adds deterministic checks to make the new contract/artifact model executable enough for pre-release validation.

## `compile`

`compile` checks the source model for reference integrity:

- every `artifact_requirement.when.contract` must reference a declared contract;
- every required artifact must reference a declared artifact or output id;
- every `must_include_fields` entry must reference a known field in the selected contract;
- every `rendered_artifact_assertion.field` must reference a known contract field;
- every `rendered_artifact_assertion.must_appear_in` target must reference a known artifact.

If this fails, the package cannot be treated as a valid Semantic JSON IR candidate.

## `coverage`

`coverage` now checks declared mapping completeness:

```text
confirmed contract
→ artifact_requirement
→ mapped required fields
```

A confirmed contract without artifact mapping is a blocking coverage issue.

A confirmed required contract field without mapping is also blocking.

## Boundary

This layer does not check rendered artifact content. It only proves that the source model declares a route from confirmed contracts to expected artifacts.
