You are running the **instruction-only benchmark variant** of the Office Opening case.

Use the attached archive:

`OFFICE_OPENING_INSTRUCTION_ONLY_V1_0.zip`

## Important constraints

- Do not use Ordo CLI, compiled IR, runtime engine, playbook gates, or any hidden execution mechanism.
- Follow only the written instructions and files contained in the archive.
- Execute the process autonomously in one chat by logically simulating:
  - `PROCESS_EXECUTOR`
  - `USER_SIMULATOR`
- Read only the answer for the current step from `inputs/full_success_answers.yaml`.
- Do not preload future answers into the working state.
- Process every required step sequentially and record the legal-entity branch.
- Generate substantive business documents, not placeholders.
- Do not claim Ordo validation or deterministic runtime verification.

## Required start

1. Extract the archive.
2. Read `README.md`.
3. Read `instructions/INSTRUCTION_ONLY_PROCESS.md`.
4. Create `outputs/07_MODEL_IDENTITY.json` before Step 1.
5. Begin at `N01_BUSINESS_INITIATION`.

## Required result

Create:

```text
OFFICE_OPENING_INSTRUCTION_ONLY_RESULT/
├── 01_OFFICE_OPENING_BUSINESS_AND_LOCATION_BRIEF.md
├── 02_OFFICE_BUILD_TECHNOLOGY_AND_OPERATIONS_PLAN.md
├── 03_OFFICE_READINESS_AND_OPENING_DECISION_REPORT.md
├── 04_EXECUTION_TRACE.md
├── 05_COLLECTED_ATTRIBUTES.md
├── 06_DIALOGUE_LOG.md
├── 07_MODEL_IDENTITY.json
└── 08_SELF_VALIDATION_REPORT.md
```

Package the directory as a ZIP and provide it in the final response.

## Response language

The prompt and source instructions are in English, but **all user-visible questions, progress updates, explanations, summaries, and the final response must be in Ukrainian**. Keep file names, step IDs, field names, and technical identifiers unchanged.

Start now. Do not ask the user for confirmation.
