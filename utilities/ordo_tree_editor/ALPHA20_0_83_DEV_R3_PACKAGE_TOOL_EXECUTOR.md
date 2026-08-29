# alpha.20.0.83-dev — deterministic package-tool executor

Generic R3 runtime/compiler capability.

- Nodes that explicitly declare a package-local deterministic helper in `node_context.allowed_tools` and return a structured machine result compile to `runtime_executor=package_tool`.
- Such nodes no longer become analyst `human_interaction` nodes merely because explanatory `question` / `answer_type` fields are present.
- Package tools execute without an LLM fallback, with shell disabled, an argv-only invocation, package-relative tool allowlisting, path validation, a 120 s timeout, and run-local output storage.
- Structured stdout is used as `$answer.*`; `on_answer.update_state` is committed mechanically before routing.
- `answer_type: file_ref` now stores the durable run-workspace path of the uploaded attachment, allowing deterministic helpers to consume the exact analyst file.
- Invalid validator exit codes are still accepted as machine evidence when structured output is produced; crashes/unparseable output become machine status `ERROR`.

Security boundary: package tools are code from the user-loaded local playbook package. The Editor executes only the explicitly allowlisted package tool and never invokes a shell.

Exact regression: JSON_VALIDATION_WORKING_PLAYBOOK_V2 — all six N_RUN_*_VALIDATOR nodes compile and execute as `package_tool` without analyst respond.
