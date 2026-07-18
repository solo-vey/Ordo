# Chapter 32. Package Generation

## Why This Is Needed

In previous chapters, we examined Ordo as a language that controls dialogue, collects state, selects a path, and passes gates. But in large workflows, the final result is almost never just a single chat response.

Often, the result must be a package:

```text
a set of Markdown documents;
a JSON report;
a YAML specification;
a README;
a QA package;
a Jira description;
a validation report;
an archive for handoff to implementation.
```

This is where `Package generation` appears.

Package generation is not the moment when a model “simply creates files.” It is a separate stage of Ordo execution with its own contract, gates, output definitions, validation, and handoff.

If this stage is not formalized, the model may:

```text
- create extra files;
- omit mandatory files;
- mix business and technical documentation;
- fail to align the README with the actual package contents;
- create a validation report that does not validate the real package;
- place intermediate files in the archive;
- deliver the package before contract gates are confirmed.
```

Ordo must make package generation a controlled action.

---

## Simple Explanation

Imagine that an Ordo program is not merely an instruction but a production line.

First it collects requirements. Then it checks the contract. Then it creates documents. Then it validates them. Then it assembles an archive. Then it hands the result to a person.

Package generation is the final production section of this line.

It must answer:

```text
what exactly is being created;
which files make up the package;
which files are mandatory;
which files are forbidden;
which formats are allowed;
which gates must pass before generation;
how package consistency is checked;
what exactly is handed to the user.
```

---

## Package as an Ordo Output

In a simple task, output may look like this:

```yaml
output:
  type: "message"
  format: "text"
```

For package generation, however, the output must be much more precise:

```yaml
output:
  type: "package"
  id: "history_event_analysis_package"
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
  forbidden_files:
    - "drafts/*"
    - "tmp/*"
    - "raw_notes/*"
```

This structure means the model does not have to guess what belongs in the package.

---

## Package Generation Must Not Start Immediately

One of the main mistakes in large playbooks is creating the final package too early.

Ordo should have a rule:

```text
The final package is not created until all gates that affect its content have passed.
```

For example:

```yaml
gates_before_package_generation:
  - "G_INTENT_CONFIRMED"
  - "G_CONTRACT_CONFIRMED"
  - "G_PATH_SELECTED"
  - "G_REQUIRED_VALUES_CONFIRMED"
  - "G_OUTPUT_SET_CONFIRMED"
  - "G_QA_SCOPE_CONFIRMED"
```

If even one gate has not passed, Ordo must stop:

```yaml
package_generation:
  status: "blocked"
  blocked_by:
    - "G_REQUIRED_VALUES_CONFIRMED"
  message: "The package cannot be generated yet because the required values have not been confirmed."
```

This is an important difference between a prompt and Ordo. A prompt often tries to fulfill a request immediately. Ordo first checks whether it is allowed to do so.

---

## Package Plan

Before creating files, Ordo must build a package plan.

```yaml
package_plan:
  package_id: "PKG_HISTORY_EVENT_LU_CHANGE_STATUS"
  alias: "LU_CHANGE_STATUS"

  files:
    - path: "README.md"
      purpose: "explains package contents and order of use"
      required: true

    - path: "01_HISTORY_EVENT_PASSPORT_LU_CHANGE_STATUS.md"
      purpose: "analytical passport of the history event"
      required: true

    - path: "05_QA_PACKAGE_LU_CHANGE_STATUS.md"
      purpose: "manual testing and QA scenarios"
      required: true

  validation:
    required: true
    reports:
      - "VALIDATION_REPORT.json"
      - "CONSISTENCY_CHECK_REPORT.json"
```

The package plan is a contract between the Ordo program and the final artifact.

If the package plan contains 11 files, the final archive must contain exactly the expected set of files unless a separately confirmed exception exists.

---

## Rendered Artifact Validation

Package generation is closely connected to `Rendered artifact validation`.

It is not enough to validate the template. The already-created result must be validated.

Bad:

```text
The README template contains a "Package Contents" section, so everything is fine.
```

Good:

```text
The actual README contains a file list that matches the real archive.
```

Ordo must check:

```text
- whether all required files were created;
- whether forbidden files are absent;
- whether the README describes the actual contents;
- whether SUMMARY.json matches the package files;
- whether the validation report refers to real checks;
- whether all aliases and file names are consistent;
- whether placeholders remain;
- whether documents contradict one another.
```

---

## Self-Check Before Handoff

Before the package is handed to the user, a self-check must run.

```yaml
self_check:
  required: true
  before:
    - "handoff"
    - "archive_delivery"

  checks:
    - id: "SC_REQUIRED_FILES"
      description: "all mandatory files are present"

    - id: "SC_NO_FORBIDDEN_FILES"
      description: "no forbidden or intermediate files are present"

    - id: "SC_README_MATCHES_PACKAGE"
      description: "README matches the actual package"

    - id: "SC_VALIDATION_REPORT_PRESENT"
      description: "validation report has been created"

    - id: "SC_CONSISTENCY_REPORT_PRESENT"
      description: "consistency check report has been created"
```

If the self-check does not pass, the package must not be handed off.

```yaml
handoff:
  status: "blocked"
  reason: "self_check_failed"
```

---

## Package Generation in Compiled IR

In compiled IR, this may look like:

```json
[
  {
    "op": "OUTPUT.DEF",
    "id": "OUT_ANALYTICAL_PACKAGE",
    "output_type": "package",
    "required_files": [
      "README.md",
      "SUMMARY.json",
      "VALIDATION_REPORT.json"
    ]
  },
  {
    "op": "GATE.REQUIRE",
    "id": "G_BEFORE_PACKAGE",
    "requires": [
      "G_CONTRACT_CONFIRMED",
      "G_OUTPUT_SET_CONFIRMED"
    ]
  },
  {
    "op": "PACKAGE.PLAN",
    "id": "PKG_PLAN_1",
    "from_output": "OUT_ANALYTICAL_PACKAGE"
  },
  {
    "op": "PACKAGE.GENERATE",
    "id": "PKG_GENERATE_1",
    "allowed_after": "G_BEFORE_PACKAGE"
  },
  {
    "op": "RENDER.VALIDATE",
    "id": "VALIDATE_RENDERED_PACKAGE"
  },
  {
    "op": "GATE.REPORT",
    "id": "G_PACKAGE_VALIDATED"
  }
]
```

This again shows that package generation is not simple text generation but an execution phase.

---

## Package Generation and Debug Mode

In debug mode, Ordo must explain:

```text
- why the package may or may not be created;
- which gates allowed package generation;
- which outputs were expected;
- which files were actually created;
- which checks passed;
- which warnings remain;
- which artifact was handed off.
```

For example:

```yaml
package_debug:
  generation_allowed: false
  blocked_by:
    - "G_QA_SCOPE_CONFIRMED"
  reason: "QA scope was not confirmed by user"
```

Or:

```yaml
package_debug:
  generation_allowed: true
  required_files_expected: 11
  required_files_created: 11
  forbidden_files_found: 0
  validation_status: "passed"
```

---

## Package Generation and the Improvement Loop

Package generation often produces useful feedback.

A user may say:

```text
the package is missing a runbook for the tester
```

or:

```text
the README does not explain which file to open first
```

Ordo should create an improvement record:

```yaml
improvement_record:
  type: "package_structure_improvement"
  affected_unit:
    kind: "output_definition"
    id: "OUT_ANALYTICAL_PACKAGE"
  proposed_patch:
    - "add 10_ANALYST_RUNBOOK.md to required_files"
    - "update README required sections"
  suggested_test:
    id: "TC_PACKAGE_README_START_HERE"
```

This allows package structures to improve through a controlled improvement cycle.

---

## Typical Mistakes

### Mistake 1. Creating a Package Without a Package Plan

Without a plan, the model may create an attractive but incorrect set of files.

### Mistake 2. Validating the Template Instead of the Created Artifact

The template may be correct while a specific file is empty or contradictory.

### Mistake 3. Failing to Separate Draft and Final

Intermediate notes must not accidentally enter the final package.

### Mistake 4. Failing to Block Handoff After Failed Validation

If validation failed, the package is not ready.

### Mistake 5. Considering an Archive “Ready” Because It Exists

An archive is ready only after self-check, validation, and consistency check.

---

## Mini-Exercise

Take any process whose result is a set of files.

For example:

```text
A document package for changing a monitoring event.
```

Try to determine:

```text
1. Which files should be required?
2. Which files should be forbidden?
3. What README is needed?
4. Which gates must pass before generation?
5. What validation report is needed?
6. What should block handoff?
```

---

## Short Summary

Package generation is a separate execution phase in Ordo. It must be controlled, verifiable, and blocked until the required gates have passed.

Ordo does not simply create files. It first defines the package contract, builds a package plan, generates required artifacts, validates the rendered result, performs a self-check, and only then hands the package to the user.

This makes it possible to work with large playbooks not as chaotic document generation but as controlled artifact production.
