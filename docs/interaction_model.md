# Interaction Model Schema Convention

Status: `M64.2 accepted-docs-schema-convention`

M64.2 documents `interaction_model` as a source-level convention for describing who does what while an Ordo program is being authored, executed, reviewed, or validated.

It is **not** a new opcode, not a deterministic runtime classifier, and not a compiler rewrite.

```text
interaction_model
  → declares the human role
  → declares the AI role
  → declares the CLI/helper role
  → declares what may be shown to the human
  → declares which decisions require human approval
```

## Canonical source shape

```yaml
interaction_model:
  human_role: content_decision_owner
  ai_role: guided_process_driver
  cli_role: deterministic_validator
  raw_tool_output_policy: summarize_before_user
  decision_authority:
    content_decisions: human
    routing_suggestions: ai
    deterministic_checks: cli
    final_release_decision: human
  review_points:
    - approve_program_contract
    - approve_runtime_profile
    - approve_output_templates
    - approve_final_package
```

## Attribute semantics

### `human_role`

- Type: `enum or convention string`
- Required: recommended for `standard` and `strict` program contracts.
- Known values:
  - `content_decision_owner`: human approves domain meaning, scope, outputs, and release decisions.
  - `approval_owner`: human owns approval gates, even if AI drafts the content.
  - `process_owner`: human owns process shape, branching, and acceptance criteria.
  - `reviewer`: human reviews generated artifacts but may not own the whole process.
- Validation behavior: unknown values are allowed only when documented as package-local conventions.

### `ai_role`

- Type: `enum or convention string`
- Required: recommended.
- Known values:
  - `guided_process_driver`: AI leads the conversation along the declared process rail.
  - `ordo_executor`: AI executes a compiled Ordo process under runtime discipline.
  - `ordo_developer`: AI helps author or improve an Ordo package.
  - `summarizer`: AI summarizes or reformats but does not own routing.
- Validation behavior: values should be consistent with `program_contract.execution_mode`.

### `cli_role`

- Type: `enum or convention string`
- Required: recommended for runtime packages.
- Known values:
  - `deterministic_validator`: CLI/helper tools validate mechanical checks.
  - `artifact_builder`: CLI/helper tools build package or output artifacts.
  - `graph_renderer`: CLI/helper tools render graph artifacts.
  - `none`: no CLI/helper role is claimed.
- Validation behavior: claiming CLI validation without reports or commands should become a M64.3 lint/profile warning.

### `raw_tool_output_policy`

- Type: `enum`
- Required: recommended.
- Allowed values:
  - `summarize_before_user`: AI summarizes raw tool output before presenting it.
  - `show_on_request`: raw output is hidden unless the user asks for it.
  - `show_full`: raw output may be shown directly.
  - `never_show_raw`: raw output is never shown directly; only interpreted summaries are allowed.
- Runtime meaning: determines whether raw CLI/tool output can be copied into the user-facing conversation.

### `decision_authority`

- Type: `map[string,string]`
- Required: optional but recommended for standard applied modules.
- Known keys:
  - `content_decisions`
  - `routing_suggestions`
  - `deterministic_checks`
  - `final_release_decision`
- Known values:
  - `human`
  - `ai`
  - `cli`
  - `shared`
- Validation behavior: if `final_release_decision` is not `human` or `shared`, the package should document why.

### `review_points`

- Type: `list[string]`
- Required: recommended for standard applied modules.
- Common convention values:
  - `approve_program_contract`
  - `approve_runtime_profile`
  - `approve_branch_contract`
  - `approve_output_templates`
  - `approve_final_package`
- Validation behavior: convention list in M64.2; M64.3 may define lint/profile checks.

## Typical mistakes

- Letting AI approve content decisions that the package says belong to the human.
- Dumping raw CLI output into the conversation when `raw_tool_output_policy` requires a summary.
- Claiming `cli_role: deterministic_validator` without declaring validation commands or evidence.
