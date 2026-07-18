# Chapter 41. Contract → Artifact Coverage and Go/No-Go

Ordo is needed not only to guide a person through the right questions. Its value appears when confirmed answers are not lost on the way to the final documents.

This is a common problem in ordinary processes: an analyst confirms the alias, event names, source, fields, normalization, payload, and test strategy, but part of this information never reaches the passport, Jira task, or implementation prompt. Formally, the dialogue succeeded, but the package became incomplete.

Ordo therefore introduces a separate layer:

```text
confirmed contracts
→ expected artifact coverage
→ generated artifacts
→ deterministic validation
→ consistency report
→ go/no-go decision
```

## Contract

A `Contract` is not merely an agreement made in chat. It is a structured object with a status.

For example:

```json
{
  "kind": "contract",
  "id": "G_EVENT_IDENTITY_CONTRACT",
  "status": "confirmed",
  "fields": {
    "alias": {
      "value": "LU_CHANGE_CAPITAL",
      "status": "confirmed",
      "required": true
    },
    "name_uk": {
      "value": "Change in company share capital",
      "status": "confirmed",
      "required": true
    }
  }
}
```

A field may be `missing`, `candidate`, `proposed`, `confirmed`, `blocked`, or `not_applicable`. This matters: the model must not present a `candidate` as a confirmed decision.

## Artifact Requirement

An `Artifact requirement` describes exactly where a confirmed contract must appear.

For example, if the `HistoryEvent output contract` is confirmed, its key fields must appear not only in the QA package, but also in the passport, Jira task, implementation prompt, and JSON reports.

```json
{
  "kind": "artifact_requirement",
  "id": "REQ_HISTORY_EVENT_OUTPUT_IN_PASSPORT_AND_JIRA",
  "when": {
    "contract": "G_HISTORY_EVENT_OUTPUT_CONTRACT",
    "status": "confirmed"
  },
  "requires": [
    {
      "artifact": "01_HISTORY_EVENT_PASSPORT",
      "must_include_fields": ["type", "sub_type", "source", "group", "groupPriority", "isEdr"]
    },
    {
      "artifact": "02_JIRA_TASK",
      "must_include_fields": ["type", "sub_type", "source", "group", "groupPriority", "isEdr"]
    }
  ]
}
```

## Why Compile Is Not Enough

`compile` can verify that an Ordo package contains valid references: the contract exists, the artifact exists, and the requirement does not refer to an unknown ID.

But `compile` cannot guarantee that a generated Markdown file actually contains the required field. Rendered artifact validation is needed for that.

## Rendered Artifact Validation

Rendered artifact validation checks files that have already been created:

```text
01_HISTORY_EVENT_PASSPORT_<ALIAS>.md
02_JIRA_TASK_<ALIAS>.md
04_IMPLEMENTATION_PROMPT_<ALIAS>.md
05_QA_PACKAGE_<ALIAS>.md
SUMMARY.json
VALIDATION_REPORT.json
CONSISTENCY_CHECK_REPORT.json
```

This layer must answer:

```text
Are all confirmed contracts actually present in the required documents?
Are there contradictions between Passport, Jira, QA, and JSON reports?
Has any candidate/proposed value been recorded as confirmed?
Has the test strategy been omitted?
```

## Go/No-Go

After all checks, Ordo must produce a short machine-readable decision:

```json
{
  "kind": "go_no_go",
  "status": "no_go_requires_artifact_fix",
  "blocking_issues": [
    {
      "code": "ORDO-COV-002",
      "message": "Confirmed contract field group is missing from Passport"
    }
  ],
  "warnings": []
}
```

For a person, this can be explained simply:

```text
The package is not ready: the confirmed group field did not reach the historical event passport.
```

## What This Changes for the AI Ordo Developer

The AI Ordo Developer no longer merely creates documents from templates. It must prove that:

1. all important contracts are confirmed;
2. every confirmed contract has artifact coverage;
3. rendered documents have not lost confirmed values;
4. the consistency report contains no blocking issues;
5. the go/no-go decision allows the package to move forward.

This makes Ordo not merely an instruction language, but a language for the controlled transfer of decisions into final artifacts.

## M46.2: The First Executable Validation Layer

At M46.1, we described the new concepts as part of the language. At M46.2, they begin to work in the CLI, but in a limited form: Ordo validates not the generated files themselves, but the declarative route from contract to artifact.

This means:

```text
confirmed contract
→ artifact_requirement
→ required artifact
→ required contract fields
```

If a package says that a contract is confirmed but does not specify which artifacts must represent it, `ordo coverage` must fail.

If an `artifact_requirement` refers to a field that does not exist in the contract, `ordo compile` must fail. This is important: an error in the coverage model must be caught before an analyst or PM receives attractive but incomplete documents.

M46.2 does not yet read rendered Markdown or JSON. That is the next layer. The current layer answers a simpler question: does the Ordo package itself know which confirmed contracts must reach which artifacts?

The practical pipeline now looks like this:

```text
lint
→ compile       # reference checks for the contract/artifact model
→ coverage      # completeness checks for confirmed contracts
→ validate-state
→ generate-output
→ validate-artifacts   # next layer
→ consistency          # next layer
→ go-no-go             # final decision
```

## M46.3: Validation of Already Generated Artifacts

At M46.3, the first executable command for rendered artifact validation appears:

```bash
ordo validate-artifacts <package>
```

It reads not only Ordo Source but also the actual files in `generated_outputs/`. This matters because `compile` and `coverage` can prove that the `contract → artifact` route is described, but they still cannot prove that the finished Markdown or JSON actually contains the confirmed value.

Example problem:

```text
G_EVENT_IDENTITY_CONTRACT.event_alias = LU_CHANGE_CAPITAL
but 02_JIRA_TASK_LU_CHANGE_CAPITAL.md does not contain LU_CHANGE_CAPITAL
```

In this case, `validate-artifacts` must return a blocking issue with code `ORDO-COV-002`.

The current M46.3 layer is not yet a full semantic consistency engine. It performs deterministic checks for the presence of confirmed values in the required rendered files. The next layer, `consistency`, must check contradictions between Passport, Jira, QA, Prompt, and JSON reports.

## M46.4: Consistency Report Between Generated Artifacts

After `validate-artifacts`, Ordo needs another validation layer: `consistency`.

`validate-artifacts` answers the question: “Is the confirmed value present in the required document?”

`consistency` answers a different question: “Do all generated documents say the same thing about the same confirmed contract?”

A typical example:

```text
alias = LU_CHANGE_CAPITAL
```

If the Passport contains `LU_CHANGE_CAPITAL`, but the Jira task contains another alias or no alias at all, the package cannot be considered ready for developer handoff. In this case, `ordo consistency` must generate `CONSISTENCY_CHECK_REPORT.json` with a blocking issue.

The minimum pipeline for an analytical package is now:

```text
lint
→ compile
→ coverage
→ intake/run
→ generate-output
→ validate-output
→ validate-artifacts
→ consistency
```

This does not replace analyst review, but it removes a class of errors in which a confirmed contract exists in the process yet is represented incompletely or inconsistently across final documents.

## M46.5: Final Go/No-Go Helper

After `validate-artifacts` and `consistency`, one short answer is needed: can the generated package be handed off? The following command is added for this purpose:

```bash
ordo go-no-go <package>
```

It does not replace the individual checks. Instead, it collects them into one pipeline:

```text
lint → compile → coverage → validate-state → validate-artifacts → consistency → go/no-go
```

The result is `reports/GO_NO_GO_REPORT.json`. If there is at least one blocking issue, the command returns a no-go status and a non-zero exit code.

Importantly, this is a deterministic helper, not AI model execution or a business runtime. The command answers only one question: are the Ordo source, confirmed contracts, generated artifacts, and consistency report aligned?

## M46.6: Pre-Release Audit and State Reuse

M46.6 does not add another major language layer. It is a pre-release audit after M46.1–M46.5. The main check is whether the entire new `contract → artifact → consistency → go/no-go` line works as one helper pipeline.

A practical M46.6 clarification is that if guided intake has already been executed and the package contains `reports/intake_report.json`, the `ordo go-no-go <package>` command may reuse that state without requiring `--answers` again. This better matches the real process:

```text
intake → generate-output → validate-artifacts → consistency → go-no-go
```

This does not change the principle: `go-no-go` remains a deterministic helper and does not execute an AI model or business runtime. It only verifies whether confirmed contracts reached generated artifacts and whether the artifacts contradict one another.

## M46.7: Clean Pre-Release Candidate

M46.7 introduces no new language semantics. It is a consolidation step before pre-release: the source archive must contain source files, documentation, tests, and package definitions, but it must not carry old results from local runs.

The practical M46.7 rule is:

```text
compiled/          generated by ordo compile
reports/           generated by helper commands
runtime/           generated by intake/run flows
generated_outputs/ generated by ordo generate-output
```

In the source archive, these directories may contain only `.gitkeep`. Real reports, compiled IR, runtime snapshots, and generated documents must be created by the current CLI run. This supports Ordo's central principle: do not trust an old self-report; reproduce evidence from the current source state.
