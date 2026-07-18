# Chapter 28. Rendered Artifact Validation

## Why This Is Needed

In many processes, a model creates more than a chat response. It creates a finished artifact: a document, archive, report, instruction, JSON, YAML, Markdown file, PDF, table, Jira package, QA set, or a set of files for handoff to another team.

At first glance, validating the template may seem sufficient. If the template is correct, the result should also be correct. In real work, this is often not true.

The template may be correct while the generated document is not.

For example:

- a mandatory section exists in the template but is empty in the finished file;
- the package structure expects 11 files, but the archive contains 12;
- README says one thing while the QA file says another;
- JSON contains one alias while Markdown contains another;
- the template defines a gate before the final archive, but the archive has already been created before the gate passes;
- a placeholder accidentally remains in the rendered document;
- an unwanted technical fragment appears in the final file.

This is why Ordo must validate not only intent, source program, and template. Ordo must validate the finished result after rendering.

![Nebu — idea: validate the artifact that was actually created](../assets/mascots/64x64/Nebu_idea_64x64.png)

This is `Rendered artifact validation`.

---

## Simple Explanation

`Rendered artifact validation` means validating the artifact that has already been created, not only the rules that were supposed to create it.

Think of it this way.

A template is a building blueprint.

A rendered artifact is the building after construction.

Checking the blueprint is useful, but insufficient. After construction, the building itself must be inspected: are the doors present, do the stairs lead to the right place, was the roof forgotten, is the electricity connected correctly, and do the rooms match the plan?

The same is true in Ordo:

```text
template validation → validates the plan
rendered artifact validation → validates the actual result
```

---

## Why This Is a Separate Ordo Layer

In ordinary prompt-based processes, a model often says:

```text
I checked the result.
```

But this does not always mean that the actual structure of the finished artifact was inspected.

Ordo should make the process more precise:

```text
1. Generate the artifact.
2. Read or analyze the generated artifact itself.
3. Compare it with the output contract.
4. Check mandatory sections.
5. Check consistency between files.
6. Check forbidden elements.
7. Produce a validation report.
8. Only then allow handoff.
```

Rendered validation is therefore a gate between result creation and delivery to the user.

---

## Main Construct

In Ordo, this mechanism can be described as:

```text
RENDER.VALIDATE
```

This construct means:

```text
validate the already generated artifact as the actual output,
not merely as an expected structure
```

In a simple form:

```yaml
render_validate:
  target: "final_package"
  against:
    - "output_contract"
    - "file_manifest"
    - "mandatory_sections"
    - "consistency_rules"
    - "forbidden_content"
  report: "VALIDATION_REPORT.json"
  blocking: true
```

The key word is `blocking`.

![Nebu — attention: failed validation blocks handoff](../assets/mascots/64x64/Nebu_attention_64x64.png)

If rendered validation does not pass, the result cannot be considered ready.

---

## What Is Validated

Rendered artifact validation may inspect several levels.

### 1. File Presence

For example, a package may be required to contain exactly these files:

```text
README.md
SUMMARY.json
VALIDATION_REPORT.json
CONSISTENCY_CHECK_REPORT.json
01_HISTORY_EVENT_PASSPORT_<ALIAS>.md
02_JIRA_TASK_<ALIAS>.md
04_IMPLEMENTATION_PROMPT_<ALIAS>.md
05_QA_PACKAGE_<ALIAS>.md
07_PROCESS_IMPROVEMENT_FEEDBACK_<ALIAS>.md
08_QA_AUTOMATION_SPEC_<ALIAS>.yaml
09_QA_AUTOMATION_README_<ALIAS>.md
```

Rendered validation must check not only that these files are described in the instruction, but that they actually exist in the final package.

It should also check for extra files when the package is required to be a compact canonical package.

---

### 2. Mandatory Sections

For example, a Jira task may be required to contain:

```text
- a general problem description;
- expected behavior;
- acceptance criteria;
- test scenarios;
- constraints;
- dependencies;
- out-of-scope items.
```

Rendered validation should open the finished Markdown file and verify that these sections are actually present.

---

### 3. Absence of Placeholders

This is a very practical check.

Bad result:

```text
<ALIAS>
<TODO>
<CONFIRM_SOURCE_FIELD>
[insert description here]
```

If a placeholder remains in the final artifact, the result is almost always not ready.

Ordo may have a rule:

```yaml
assert_not:
  rendered_artifact_contains:
    - "<TODO>"
    - "<ALIAS>"
    - "TBD"
    - "insert here"
```

---

### 4. Consistency Between Files

This is one of the most important parts.

In a complex package, the same information often appears in several places:

- alias;
- event name;
- source field;
- status;
- expected output;
- test case id;
- route/path;
- file list;
- change level;
- no-op behavior;
- rollback rules.

Rendered validation should verify that these values do not contradict one another.

![Nebu — thinking: consistency often breaks between files](../assets/mascots/64x64/Nebu_thinking_64x64.png)

For example:

```text
README.md says: alias = LU_CHANGE_STATUS
QA_PACKAGE.md says: alias = LU_CHANGE_CAPITAL
```

This is not a minor mistake. It is a consistency-gate failure.

---

### 5. Compliance with the Output Contract

The output contract defines exactly what must be created.

Rendered artifact validation checks:

```text
whether the result actually matches what was promised
```

If the contract says:

```text
create only an analytical package, without technical implementation
```

the rendered artifact must not suddenly contain:

```text
ready Java code
database migrations
configuration changes
real endpoints
```

If the contract says:

```text
do not include extra files
```

an archive containing extra payload files must be blocked.

---

### 6. Forbidden Actions or Forbidden Content

Rendered validation should check not only what must exist but also what must not exist.

For example:

```yaml
assert_not:
  - "final archive before approval"
  - "invented source row"
  - "unconfirmed alias"
  - "hidden implementation details"
  - "extra YAML with local secrets"
```

This is especially important when a model works with archives, code, configurations, or documentation for other teams.

---

## Example Ordo Source

```yaml
output:
  id: "history_event_package"
  type: "archive"
  required_files:
    - "README.md"
    - "SUMMARY.json"
    - "VALIDATION_REPORT.json"
    - "CONSISTENCY_CHECK_REPORT.json"
    - "01_HISTORY_EVENT_PASSPORT_<ALIAS>.md"
    - "02_JIRA_TASK_<ALIAS>.md"
    - "04_IMPLEMENTATION_PROMPT_<ALIAS>.md"
    - "05_QA_PACKAGE_<ALIAS>.md"
    - "07_PROCESS_IMPROVEMENT_FEEDBACK_<ALIAS>.md"
    - "08_QA_AUTOMATION_SPEC_<ALIAS>.yaml"
    - "09_QA_AUTOMATION_README_<ALIAS>.md"

render_validation:
  id: "G_RENDERED_PACKAGE_VALID"
  target: "history_event_package"
  blocking: true
  checks:
    - required_files_present
    - no_extra_files
    - no_placeholders
    - alias_consistency
    - required_sections_present
    - validation_report_present
    - consistency_report_present
```

---

## Example Semantic JSON IR

```json
{
  "op": "RENDER.VALIDATE",
  "id": "G_RENDERED_PACKAGE_VALID",
  "target": "history_event_package",
  "blocking": true,
  "checks": [
    "required_files_present",
    "no_extra_files",
    "no_placeholders",
    "alias_consistency",
    "required_sections_present",
    "validation_report_present",
    "consistency_report_present"
  ],
  "on_fail": {
    "status": "blocked",
    "handoff_allowed": false,
    "required_action": "fix_rendered_artifact"
  }
}
```

---

## Relationship with Gates

Rendered validation should almost always be a gate.

Not merely a recommendation:

```text
it is advisable to check the result
```

But a gate:

```text
the result cannot be handed off until rendered validation has passed
```

In Ordo, it should therefore be connected to the gate system:

```yaml
gate:
  id: "G_RENDERED_OUTPUT_VALID"
  method: mechanical
  trust_class: deterministic
  type: "rendered_artifact_validation"
  blocking: true
  required_before:
    - "handoff"
    - "archive_delivery"
    - "send_to_developer"
```

---

## Relationship with the Debug Layer

In debug mode, rendered validation should show:

```text
- which files were checked;
- which sections were found;
- which rules passed;
- which rules failed;
- which values were compared;
- exactly where an inconsistency was found;
- which gate blocked handoff.
```

For example:

```yaml
trace_source: "model_self_report"
render_validation_trace:
  target: "final_archive"
  checks:
    - id: "required_files_present"
      status: "passed"
    - id: "no_extra_files"
      status: "failed"
      evidence:
        extra_files:
          - "payload_update.json"
    - id: "alias_consistency"
      status: "passed"

result:
  gate: "G_RENDERED_PACKAGE_VALID"
  status: "blocked"
```

---

## Relationship with the Test Layer

Rendered artifact validation also needs to be tested.

For example:

```yaml
test:
  id: "TC_RENDER_BLOCKS_EXTRA_FILE"
  method: mechanical
  trust_class: deterministic

fixture:
  package_files:
    - "README.md"
    - "SUMMARY.json"
    - "payload_update.json"

expected:
  gate:
    id: "G_RENDERED_PACKAGE_VALID"
    status: "blocked"

  reason:
    - "extra_file_detected"
```

Or:

```yaml
test:
  id: "TC_RENDER_BLOCKS_PLACEHOLDER"
  method: mechanical
  trust_class: deterministic

fixture:
  file_content:
    path: "02_JIRA_TASK.md"
    content: "Alias: <ALIAS>"

expected:
  gate:
    id: "G_RENDERED_OUTPUT_VALID"
    status: "blocked"

  violation:
    - "placeholder_detected"
```

---

## Relationship with the Feedback & Improvement Loop

If a user receives an artifact and says:

```text
README contains one event name, while the QA file contains another.
```

Ordo should create an improvement record:

```yaml
improvement_record:
  classification:
    type: "rendered_artifact_inconsistency"
    severity: "high"

  affected_unit:
    kind: "render_validation_rule"
    id: "alias_consistency"

  proposed_patch:
    - "add consistency check between README.md and QA_PACKAGE.md"
    - "add regression test for mismatched event display name"

  suggested_tests:
    - "TC_RENDER_BLOCKS_DISPLAY_NAME_MISMATCH"
```

Every defect in a final artifact should therefore become a source of improvement for validation rules.

---

## Typical Mistakes

### Mistake 1. Validating Only the Template

The template may be correct while the result is wrong.

Ordo must validate the rendered artifact.

---

### Mistake 2. Treating Self-Check as a Textual Promise

The phrase:

```text
I checked the result
```

is not a validation report.

A structured gate report is required.

---

### Mistake 3. Not Checking Consistency Between Files

In large packages, major defects often exist not inside one file but between files.

---

### Mistake 4. Allowing Handoff After Failed Validation

If validation failed, handoff must be blocked.

---

### Mistake 5. Not Testing Validation Rules

Validation rules can also be incomplete. They must be tested as part of the Ordo program.

---

## Mini-Exercise

Take any document or file package that a model is expected to create.

Try to answer:

```text
1. Which files or sections are mandatory?
2. Which placeholders must not remain?
3. Which values must be identical in different locations?
4. Which extra files or sections must not exist?
5. Which gate should block delivery of the result?
6. Which validation report should be produced?
```

If you can answer these questions, you already have the basis for `RENDER.VALIDATE`.

---

## Short Summary

Rendered artifact validation is the validation of the actual result after it has been created.

In Ordo, this matters because a model may understand the template correctly but still make a mistake in the finished document or package.

The main rule is:

```text
an unvalidated rendered artifact cannot be handed off as a finished result
```

For complex processes, `RENDER.VALIDATE` should be a blocking gate before handoff.

---

<!-- REVIEWED: chapter 28; Nebu markers checked -->

---

## Independent validation and atomic-unit coverage

A producer cannot validate its own output by declaring `passed`. The producer and validator must be separate runtime responsibilities, even when the same underlying model is used in two isolated invocations.

A machine-checkable validation result should identify:

```yaml
validation_result:
  validator_id: "V_PACKAGE"
  target_id: "package"
  target_revision: 3
  target_sha256: "..."
  validation_contract_id: "package_contract.v1"
  mandatory_units:
    - unit_id: "README"
      status: passed
    - unit_id: "runtime_contract"
      status: passed
  aggregate_status: passed
```

For a composite artifact, document-level success cannot hide a failed mandatory unit. Aggregate `passed` is allowed only when every mandatory atomic unit passes. Validation instructions that are missing or ambiguous produce a blocking state rather than inferred criteria.
