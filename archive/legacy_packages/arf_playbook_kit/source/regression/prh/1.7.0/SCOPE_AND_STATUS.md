# Scope and status

Status: **Negative-test and provenance hardening implemented.**

Closed in module:
- expected violation declarations for PRH-DYN-002/003/005;
- generic fixture-aware stability semantics;
- unexpected success handling;
- release metadata consistency detection;
- checksum-domain and manifest-drift detection.

Not closed by this module:
- correcting metadata inside a specific candidate playbook package;
- rebuilding or correcting a specific baseline package checksum declaration.

Those remain defects of the corresponding playbook packages, while PRH now detects them deterministically.
