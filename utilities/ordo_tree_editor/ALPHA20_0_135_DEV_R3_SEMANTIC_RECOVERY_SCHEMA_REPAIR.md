# alpha.20.0.135-dev

Fixes a generic Execute Playbook failure where semantic recovery returned a malformed StatePatch such as a non-array `operations`.

Behavior:
- initial semantic-recovery response is validated against StatePatch/route constraints;
- if structurally invalid, Editor performs exactly one model retry;
- retry receives the previous candidate and exact validation errors;
- retry is instructed to repair response shape only and remains bounded by the same allowed write paths / next targets;
- if the repaired candidate is still invalid, execution fails closed;
- no playbook/domain source is changed.
