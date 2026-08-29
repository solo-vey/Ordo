# alpha.20.0.105-dev — Detailed compilation diagnostics

- Integrated runtime-plan validator preserves structured compiler diagnostics instead of reducing them to generic strings.
- Diagnostics include code, affected element, element kind, current routes, unreachable elements, source file and best-effort YAML line/column, expected invariant, and remediation.
- Failure dialog shows each blocking issue separately.
- Technical details show the structured diagnostics first and raw validator JSON as a nested fallback.
- `Download diagnostics JSON` exports the complete failure snapshot for debugging, CI, or another chat.
- The contract is generic: diagnostics without Ordo-specific metadata still render with code/message/source/evidence when available.
