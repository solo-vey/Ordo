# Expected deliverables

Return a compact playbook package containing:

- `README.md` with purpose and chat-start instructions;
- `source/program.ordo.yaml` with the process, state, steps, gates, assertions, and outputs;
- `START_PROMPT_RUNTIME_MODE.md` for starting the finished playbook in a new chat;
- `tests/test_cases.yaml` with the agreed positive and negative cases;
- `EXAMPLE_OUTPUT.md` from the successful dry-run;
- `VALIDATION_SUMMARY.md` distinguishing conversational checks from optional deterministic checks.

Package these files as a ZIP when the chat supports file creation. Otherwise return each file in a separate clearly named block.
