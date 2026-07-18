# External Developer Independence Verification

External adoption and external-team independence are separate claims. A publication-safe case may be useful even when independence is only self-declared.

## Rule

A case must not claim a stronger independence level than its attached evidence supports.

## Levels

1. `self_declared_independence_unverified`
2. `timestamp_verified`
3. `public_release_bound_verified`
4. `organizationally_separated`
5. `third_party_verified`

External timestamp and signature services are optional for Level 0 and required only when a stronger level depends on them. Only hashes, signatures, or privacy-safe verification records should be sent to such services.

## Publication safety

The confidential original remains private. Its SHA-256 is recorded; the publication-safe derivative carries transformation provenance and new checksums.

## Admission

The validator fails closed when required evidence is absent, a claim overstates independence, internal access is incompatible with the selected level, or confidential source material is exposed.
