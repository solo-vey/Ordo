# DD-ORDO-M55-001 — Runtime Mode start files standard

Decision: Runtime Mode rules are package content, not repeated prompt content.

Every runtime-ready subject package has `START_HERE_RUNTIME_MODE.md` with the full protocol and `START_PROMPT_RUNTIME_MODE.md` with a minimal prompt. This prevents oversized prompts and keeps the runtime standard versioned with the package.

Consequences:

- AI/runner starts by reading package-owned runtime rules.
- `compiled/program.ir.json` remains the runtime source for guided order when current.
- CLI truthfulness is recorded explicitly.
- New package templates include `reports/CLI_VALIDATION_SUMMARY.md`.
