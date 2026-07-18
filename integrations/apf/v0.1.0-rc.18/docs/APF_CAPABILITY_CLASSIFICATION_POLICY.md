# APF A6 Capability Classification Policy

APF shall classify every Ordo-related capability using these exact levels:

- `runtime-supported` — implemented by CLI/runtime and covered by tests;
- `helper-supported` — deterministic command/report exists but does not itself enforce process progression;
- `package-local` — APF may implement evidence or policy locally without claiming Ordo core support;
- `policy-only` — accepted behavior contract without verified runtime implementation;
- `pilot-only` — experimental protocol/evidence, not production readiness;
- `blocked` — known blocker prevents adoption.

No APF release may replace these statuses with an undifferentiated `supported`.
