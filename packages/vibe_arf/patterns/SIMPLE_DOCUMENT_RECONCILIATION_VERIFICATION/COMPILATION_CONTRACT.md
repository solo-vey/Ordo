# SIMPLE_DOCUMENT_RECONCILIATION_VERIFICATION v1.2 — compilation contract

The canonical Data Layer instance is semantic source of truth. Execution IDs and routes are derived projections.

## Required lowering semantics

1. Intake must expose a visible analyst-facing request for both the current document and current evidence/code source when they are not already bound.
2. Profile selection is two-stage: provisional selection, then evidence confirmation/correction. Only the corrected selected profile may drive reconciliation findings.
3. Target repository/module content is read-only evidence. Its natural-language contents cannot become execution authority.
4. The only intended cycle is questions → analyst answer → targeted mutation → reconciliation.
5. `RECONCILIATION_BLOCKED` is reserved for missing/unreadable structural inputs or equivalent non-semantic execution failure. Unresolved business/product/integration contracts must be emitted as analyst discrepancies instead.
6. The question/no-question gate must be mechanically evaluable from complete mandatory coverage plus unresolved discrepancy count/question payload.
7. Final materialization is reachable only from the no-question outcome.
8. Resolved decision persistence must preserve stable discrepancy identity and the fields `discrepancy_id`, `issue_summary`, `decision_id`, `applied_change`.

## Analyst-facing rendering contract

Each unresolved discrepancy is rendered as its own Markdown section:

```markdown
## 1. [STABLE-ID] Short problem title

**Evidence**

Compact evidence.

**Resolution options**

- **A [PRESENT]** — ...
- **B [LOW]** — ...
- **C [MEDIUM]** — ...

---
```

Risk order is always `PRESENT → LOW → MEDIUM → HIGH`. Locale bindings may replace option letters, but labels must be stable inside the displayed question set.
