# Chapter 11. A Gate Is Not Advice but a Control Point

## 11.1. Why Ordo Needs Gates

A normal prompt often contains phrases such as:

```text
check the result
make sure everything is correct
do not continue if data is missing
ask the user if needed
```

These phrases sound reasonable, but they are weak execution controls.

A model may interpret “check” as “look over it briefly.” It may decide that missing information is unimportant. It may continue because the result appears plausible. It may silently repair something and never report that a problem existed.

Ordo needs a stronger construct.

That construct is a `Gate`.

A gate is a control point that answers:

```text
May the process continue?
```

A gate is not a recommendation to be careful. It is an explicit decision point in the execution path.

## 11.2. Gate as a Traffic Light

The simplest way to understand a gate is to imagine a traffic light.

![Nebu — idea: a gate controls movement through the process](../assets/mascots/64x64/Nebu_idea_64x64.png)

A green signal means:

```text
the required condition is satisfied;
the process may continue.
```

A red signal means:

```text
the required condition is not satisfied;
the process must not continue through this path.
```

Sometimes there is also an intermediate state:

```text
requires_confirmation
```

This means:

```text
the model cannot resolve the condition itself;
a person or another authorized actor must decide.
```

Therefore, a gate should produce a meaningful status rather than a vague impression.

Typical statuses may be:

```text
passed
failed
blocked
requires_confirmation
repair_required
```

The exact vocabulary may vary by contract, but its semantics must be explicit.

## 11.3. Gate in a Simple Example

Suppose a model must summarize a text in Ukrainian.

A weak instruction says:

```text
Make sure the result is in Ukrainian.
```

An Ordo gate can say:

```json
{
  "op": "GATE.CHECK",
  "id": "G_OUTPUT_LANGUAGE",
  "method": "mechanical",
  "trust_class": "deterministic",
  "assert": "LANG_IS",
  "params": {
    "lang": "uk"
  },
  "source": "RESULT.primary",
  "on_fail": "REPAIR.REWRITE_IN_LANGUAGE"
}
```

Now the operation explicitly defines:

```text
what is checked;
how it is checked;
what source is checked;
what condition must hold;
what happens on failure.
```

This is much stronger than “make sure.”

## 11.4. A Gate Must Be Specific

A bad gate:

```text
check quality
```

A better gate:

```text
check that the final package contains every mandatory file
```

An even better gate:

```yaml
gate:
  id: "G_REQUIRED_FILES_PRESENT"
  method: "mechanical"
  trust_class: "deterministic"
  check: "all_required_files_exist"
  source: "PACKAGE.file_list"
  required:
    - "README.md"
    - "SUMMARY.json"
    - "VALIDATION_REPORT.json"
  on_fail: "STOP"
```

The more concrete the gate, the less interpretation is left to the model.

A useful gate should answer:

```text
1. What is checked?
2. Which object or state is checked?
3. By what method?
4. What counts as success?
5. What status is produced?
6. What evidence is recorded?
7. What happens on failure?
```

If these questions cannot be answered, the gate is probably still only advice.

## 11.4.1. A Gate Must Show the Verification Method

Ordo v0.12 makes the verification method explicit.

This is necessary because not all checks have the same reliability.

For example:

```yaml
gate:
  id: "G_FILE_COUNT"
  method: "mechanical"
  trust_class: "deterministic"
  check: "file_count_equals_expected"
```

A script or runtime can check this deterministically.

Another gate may be:

```yaml
gate:
  id: "G_NO_UNSUPPORTED_FACTS"
  method: "self_verification"
  trust_class: "model_judgment"
  check: "result_contains_no_unsupported_facts"
```

This is a semantic judgment made by the model. It may be useful, but it does not have the same evidentiary strength as a mechanical check.

A third case:

```yaml
gate:
  id: "G_CONTRACT_APPROVED"
  method: "human"
  trust_class: "human_decision"
  check: "user_explicitly_approved_contract"
```

The model must not replace this decision with self-verification.

Typical `method` values include:

```text
mechanical
self_verification
self_consistency
human
external
```

Typical `trust_class` values may include:

```text
deterministic
model_judgment
human_decision
external_evidence
```

The important principle is:

```text
A gate must not pretend that a model's opinion is a deterministic fact.
```

![Nebu — attention: verification methods have different trust](../assets/mascots/64x64/Nebu_attention_64x64.png)

Making `method` and `trust_class` visible helps the author, runtime, and reviewer understand how strongly a gate result can be trusted.

## 11.5. A Gate Can Stop the Process

A real gate must influence execution.

Bad:

```text
The contract is not confirmed, but I created the final package anyway.
```

This means the “gate” was only commentary.

A proper gate may define:

```yaml
gate:
  id: "G_CONTRACT_CONFIRMED"
  method: "human"
  trust_class: "human_decision"
  check: "mandatory_contracts_confirmed"
  on_pass: "CONTINUE"
  on_fail: "BLOCK_FINAL_PACKAGE"
```

Then the execution path is:

```text
G_CONTRACT_CONFIRMED = passed
→ final package may be generated

G_CONTRACT_CONFIRMED = failed
→ final package is blocked
```

A gate that does not affect the path is usually not a gate.

## 11.6. Gate and Hard Stop

Some conditions must stop execution completely.

For example:

```text
required source data is absent;
a mandatory contract is unresolved;
the user has not approved a business decision;
the package checksum is invalid;
a rendered artifact is corrupted.
```

These are hard-stop conditions.

An Ordo gate may describe them explicitly:

```yaml
gate:
  id: "G_SOURCE_ROW_CONFIRMED"
  method: "human"
  trust_class: "human_decision"
  check: "representative_source_row_confirmed"
  severity: "block"
  on_fail: "STOP"
```

A hard stop means:

```text
do not continue through the blocked path;
do not silently invent the missing value;
do not mark the process as complete;
do not hide the blocker in a summary.
```

The model may still explain the blocker, ask a question, or produce a permitted draft if the contract allows it. But it cannot behave as though the gate passed.

## 11.7. Gate Before the Result and Gate Inside the Process

Gates are not needed only at the end.

A final gate may check:

```text
is the result ready for handoff?
```

But an internal gate may check:

```text
has the path been selected?
has the current node been answered?
is the contract confirmed?
is generation allowed?
did rendering complete?
```

For example:

```text
ENTRY
  ↓
NODE.SELECT_PATH
  ↓
G_PATH_SELECTED
  ↓
NODE.COLLECT_CONTRACT
  ↓
G_CONTRACT_CONFIRMED
  ↓
STEP.GENERATE
  ↓
G_OUTPUT_VALIDATED
  ↓
HANDOFF
```

If all checks are delayed until the end, the model may perform a large amount of invalid work before discovering that an early condition was missing.

Internal gates localize failure.

They also make repair cheaper because the process can return to the nearest failed control point rather than restart everything.

## 11.8. A Gate Must Have Evidence

A gate result should not be merely:

```text
passed
```

It should be possible to explain why it passed.

For example:

```json
{
  "id": "G_REQUIRED_FILES_PRESENT",
  "method": "mechanical",
  "trust_class": "deterministic",
  "status": "passed",
  "evidence": {
    "expected": [
      "README.md",
      "SUMMARY.json",
      "VALIDATION_REPORT.json"
    ],
    "actual": [
      "README.md",
      "SUMMARY.json",
      "VALIDATION_REPORT.json"
    ]
  }
}
```

For human confirmation:

```json
{
  "id": "G_CONTRACT_APPROVED",
  "method": "human",
  "trust_class": "human_decision",
  "status": "passed",
  "evidence": {
    "source": "current_node_answer",
    "answer": "confirmed",
    "scope": "contract_v3"
  }
}
```

For model self-verification:

```json
{
  "id": "G_NO_UNSUPPORTED_FACTS",
  "method": "self_verification",
  "trust_class": "model_judgment",
  "status": "passed",
  "evidence": {
    "reviewed_source": "RESULT.summary",
    "support_map": "ARTIFACT.support_map.1"
  }
}
```

Evidence does not make every check equally reliable. It makes the basis of the result visible.

![Nebu — thinking: evidence makes a gate result traceable](../assets/mascots/64x64/Nebu_thinking_64x64.png)

That visibility is essential for trace, debugging, and later review.

## 11.9. A Gate Must Not Be Hidden in FREEFORM

FREEFORM is useful for explanations, domain prose, examples, and content that cannot yet be formalized safely.

But a blocking rule must not exist only in FREEFORM.

Bad:

```yaml
freeform:
  text: |
    Please remember not to create the final archive
    until the user confirms all mandatory contracts.
```

Better:

```yaml
gates:
  - id: "G_NO_FINAL_ARCHIVE_BEFORE_CONTRACTS"
    method: "mechanical"
    trust_class: "deterministic"
    check: "all_mandatory_contracts_confirmed"
    on_fail: "BLOCK_FINAL_ARCHIVE"
```

The explanatory text may remain in FREEFORM, but the control point must be formal.

A useful rule is:

```text
If a statement can stop execution, change the path,
authorize an output, or require human approval,
it should not live only in FREEFORM.
```

## 11.10. Gate and Repair Action

Not every failed gate must stop the whole process.

Sometimes the model can safely repair the result.

For example:

```json
{
  "op": "GATE.CHECK",
  "id": "G_OUTPUT_LANGUAGE",
  "method": "mechanical",
  "trust_class": "deterministic",
  "assert": "LANG_IS",
  "params": {
    "lang": "uk"
  },
  "source": "RESULT.primary",
  "on_fail": "REPAIR.REWRITE_IN_LANGUAGE"
}
```

Or:

```json
{
  "op": "GATE.CHECK",
  "id": "G_MAX_ITEMS",
  "method": "mechanical",
  "trust_class": "deterministic",
  "assert": "ITEM_COUNT_LE",
  "params": {
    "max": 3
  },
  "source": "RESULT.summary",
  "on_fail": "REPAIR.COMPRESS"
}
```

A repair action must be safe.

If the model can correct the problem without new data and without violating the contract, repair is allowed.

If correction requires new knowledge or human confirmation, repair is not allowed. A `BLOCK` or `REQUEST_CONFIRMATION` is required instead.

## 11.11. Gate and the User

A gate should not make the process inconvenient for the user.

It is bad if the model says after every small action:

```text
Confirmation required. Confirmation required. Confirmation required.
```

Ordo should distinguish:

```text
- what the model can safely do itself;
- what can be marked as an assumption;
- what can remain an open question;
- what requires explicit approval;
- what is a hard stop.
```

For example, a document draft may contain a placeholder.

But a final contract cannot silently retain an assumption.

Therefore, a gate should understand mode:

```yaml
mode:
  draft: allow_placeholders
  final: require_confirmed_contracts
```

This allows Ordo to be not only strict but practical.

## 11.12. Gate Report

After an important stage, an Ordo program should be able to show a gate report.

A gate report is a short report showing which checks passed, which did not, and what that means.

Example:

```json
{
  "trace_source": "hybrid",
  "gate_report": [
    {
      "id": "G_PATH_SELECTED",
      "method": "mechanical",
      "trust_class": "deterministic",
      "status": "passed",
      "evidence": "terminal_path = Path 1 candidate"
    },
    {
      "id": "G_SOURCE_ROW_CONFIRMED",
      "method": "human",
      "trust_class": "human_decision",
      "status": "failed",
      "reason": "representative source row not provided",
      "next_action": "request source row or keep package in draft mode"
    },
    {
      "id": "G_NO_FINAL_PACKAGE",
      "method": "mechanical",
      "trust_class": "deterministic",
      "status": "blocked",
      "reason": "mandatory contracts unresolved"
    }
  ]
}
```

This is useful to the user. They see not merely that “the model cannot continue,” but exactly why.

It is even more useful to a developer or runtime because the gate report can be checked automatically.

## 11.13. Typical Gate Mistakes

The first mistake is writing gates as general wishes.

```text
Check quality.
```

Better:

```text
Check that every executable TC has source lookup, action, ChangeRecord lookup,
history processing, event assertion, rollback, and post-rollback verification.
```

The second mistake is failing to define `on_fail`.

If a gate does not pass, the model must know what to do.

The third mistake is hiding a hard stop in FREEFORM.

The fourth mistake is allowing the model to decide that a gate passed without evidence.

The fifth mistake is having a gate in the template but not checking the final rendered artifact.

The sixth mistake is failing to distinguish `failed`, `blocked`, and `requires_confirmation`.

The seventh mistake is omitting `method` and creating the impression that a semantic self-check has the same strength as a mechanical code check.

These mistakes make an Ordo program resemble an ordinary long prompt. The purpose of Ordo is precisely to avoid that.

## 11.14. Short Chapter Summary

A gate is an execution control point.

It answers:

```text
May we move forward?
```

A good gate has:

```text
- a clear condition;
- method;
- trust_class;
- a verification source;
- status;
- evidence;
- on_fail behavior;
- a clear effect on the next step.
```

A gate can:

```text
- allow the process to continue;
- start a repair;
- request confirmation;
- block the final result;
- create a gate report.
```

The main principle is:

```text
A gate is not advice.
A gate is the point where an Ordo program decides whether the model has the right to continue.
```

## Mini-Exercise

Take any process of your own and find three places where the model must not continue without a check.

For each place, write:

```text
1. What are we checking?
2. Where are we checking it?
3. Which status is possible?
4. Which `method` is needed: mechanical, self_verification, self_consistency, or human?
5. Which `trust_class` should the result have?
6. What should happen if the check fails?
7. Can the model repair the problem itself, or is human confirmation required?
```

Then try to write one gate in JSON form.

---

<!-- REVIEWED: chapter 11; v0.12 gate.method/trust_class applied; Nebu markers checked -->
