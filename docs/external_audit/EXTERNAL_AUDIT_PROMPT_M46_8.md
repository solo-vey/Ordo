# Ordo v0.12 M46.8 External Audit Prompt

Use this prompt when an independent reviewer or a fresh AI session receives the Ordo pre-release archive and needs to verify it as a practical package, not only as documentation.

```text
You are working as an external Ordo pre-release auditor.

I uploaded the Ordo v0.12 M46.8 pre-release candidate archive. Do not assume the validation reports are correct. Verify the package by actually inspecting files and, when tools are available, running commands.

Your task is to audit whether this package is ready to be treated as a source-available pre-release candidate for Ordo as an AI-agent Process Rail language.

Focus areas:

1. Repository structure
   - Confirm the archive contains only the active workspace: language, CLI, docs, book source, and active reference packages.
   - Confirm obsolete registry-site/dashboard/publication/playbook/template-registry roots are absent.
   - Confirm generated package outputs are not carried in source directories except .gitkeep placeholders.

2. CLI install and basic health
   - Run `PYTHONDONTWRITEBYTECODE=1 ordo repo-check ..` on the clean extracted source archive before install/tests, or clean generated metadata before running it later. Then install the CLI from cli/ using editable mode if the environment allows it, run `ordo --version`, and run the CLI unit tests.

3. Active package checks
   - For packages/ordo_project_builder, packages/ordo_hybrid_executor, and packages/history_event_guided_intake run lint, compile, test, and coverage.
   - Confirm test output clearly indicates static mode.

4. Contract/artifact validation layer
   - Confirm language docs define contracts, artifact requirements, rendered artifact assertions, consistency reports, and go/no-go decisions.
   - Confirm compile/coverage fail on invalid contract-artifact mappings where negative tests exist.
   - Confirm validate-artifacts checks rendered markdown/json/yaml content.
   - Confirm consistency generates CONSISTENCY_CHECK_REPORT.json.
   - Confirm go-no-go generates GO_NO_GO_REPORT.json and returns no_go on blocking issues.

5. History Event regression
   - Use packages/history_event_guided_intake as the regression package.
   - Confirm the flow can run intake, generate output, validate artifacts, run consistency, and go-no-go.
   - Confirm test strategy appears in Passport, Jira, QA package, and Implementation Prompt outputs.

6. Documentation and book source
   - Confirm README and CLI docs mention the current M46 validation pipeline.
   - Confirm book/source markdown is updated for Process Rail, contract/artifact coverage, rendered validation, consistency, and go/no-go.
   - Do not require regenerated PDF; markdown source is the canonical book update for this pre-release.

7. Release honesty
   - Confirm the package does not claim to be open source.
   - Confirm known limitations are stated: CLI checks deterministic structures/artifacts; it does not execute live AI, REST, Mongo, or production business code.

Return your audit as:

- Verdict: go / no_go / go_with_warnings
- Blocking issues
- Warnings
- Commands run
- Evidence snippets
- Suggested next fixes

Do not trust self-reported validation files unless they match the actual package contents and command results.
```

