# External Validation Rule — Authoritative Missing-Input Blocking

## Status

External evaluation rule.  
This rule is intentionally external to the Playbook and must not be treated as a Playbook gate unless separately adopted.

## Rule

A document or artifact must **not** be marked invalid merely because a scenario is not runnable when the user, Driver, repository evidence, contract, schema, or another authoritative source did not provide the information required to construct that scenario safely.

The correct behavior is to preserve the scenario as explicitly blocked rather than invent missing facts.

## Valid blocked scenario

A blocked scenario is valid when all of the following are true:

1. The missing information is genuinely authoritative and cannot be derived safely.
2. The scenario has a stable functional identifier.
3. Its status is explicit, for example:
   - `blocked`;
   - `blocked_missing_binding`;
   - `blocked_missing_contract`;
   - another precise blocked status.
4. The blocker names the exact missing capability, binding, schema, request body, repository symbol, endpoint, field, or contract.
5. Closure evidence is specified.
6. The blocked state is consistent across all related artifacts:
   - Passport;
   - Jira;
   - Manual QA;
   - Automation;
   - status registry;
   - traceability matrix.
7. No runnable commands, fixtures, schemas, endpoints, fields, or expected live results are invented.
8. The remaining runnable scenarios remain complete and internally consistent.

## Evaluation consequence

When these conditions are satisfied:

- the blocked scenario is not a document defect;
- the document is not capped or failed because the scenario is non-runnable;
- the blocked scenario counts as correctly handled coverage;
- a package may still receive `T_COMPLETED / GO` when the blocker is local and does not invalidate the remaining scope;
- the evaluator should assess the quality of blocker description, closure criteria, and cross-artifact consistency rather than penalizing the absence of fabricated execution steps.

## Invalid blocked scenario

A blocked scenario remains defective when:

- the missing information was actually available but ignored;
- the blocker is vague;
- closure criteria are absent;
- status differs across artifacts;
- the artifact silently omits the scenario;
- runnable content is partially fabricated;
- the blocker prevents the core requested scope from being delivered but the package still claims unconditional completion.

## Applied example

For `TC-006 / MQA-006 / AUTO-006`:

- authoritative omitted-field request binding is unavailable;
- exact legal request body and schema are missing;
- the scenario is consistently marked `blocked_missing_binding`;
- closure requires Driver-confirmed request body and schema;
- no executable omission fixture was invented.

Therefore the blocked scenario is valid and does not reduce document validity merely because it is not runnable.
