# Generated-playbook mini-prompt validation and test policy

An approved mini-prompt is not release-ready until validation and mandatory test scenarios pass.

Validation must cover structure, registry/manifest integrity, attachment, authority boundaries, required context, fallback behavior, duplication/conflicts, approval integrity and test coverage.

A prompt is blocked if it can navigate, bypass gates, confirm decisions, mutate confirmed state, introduce hidden business logic, lacks valid approval, has a checksum mismatch or lacks mandatory fallback/tests.

Mandatory scenarios are: intended use, insufficient context, irrelevant context, authority boundary, gate-bypass attempt and prompt-absent fallback.

Contract/package-level evidence is acceptable for PMP-4. Live-model replay is not required and no deterministic natural-language output is claimed.
