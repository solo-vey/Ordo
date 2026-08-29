# Playbook Contract

## Stable identity
- ID: `PB_PLAYBOOK_REGRESSION`
- Name: Playbook Regression Playbook
- Short name: PRP

## Trigger
A baseline playbook and a candidate playbook must be compared before candidate promotion, replacement, migration or release.

## Supported use cases
- version-to-version regression;
- migration across ARF/package formats;
- deterministic-only preflight;
- chat-native behavioral pilot;
- provider API behavioral pilot;
- multi-chat and cross-model comparison.

## Unsupported claims
- chat-native evidence is not provider provenance;
- semantic projection cannot replace dynamic execution;
- a missing or corrupt baseline cannot be reconstructed from the candidate;
- `GO` cannot be issued without the evidence required by the selected production policy.

## Retry and resume
Every step emits a checkpoint. Completed deterministic work may be reused if package digests and tool versions are unchanged.

## Safe stop
Missing mandatory inputs, checksum failure, incompatible package identity, unresolved duplicate IDs or absent required evidence must not be silently ignored.

## Evidence
Every verdict must trace to immutable reports, source package digests and the resolved PRH version.


## Negative-test semantics
Negative scenarios must declare expected violations before execution. A valid negative test requires:
- expected violation observed;
- no unexpected violations;
- no unexpected success;
- consistent route and terminal across required repetitions.

## Package provenance checks
Before behavioral execution, PRP must run:
- release metadata consistency;
- checksum-domain and manifest-drift validation.

PRP detects package defects but does not silently rewrite the tested baseline or candidate package.
