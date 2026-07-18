# Chapter 43. Final Handoff: How to Transfer Ordo for External Review

Final handoff is not a new language feature. It is the point at which the package is stable enough for another developer, analyst, or AI session to review without the author's participation.

This is especially important for Ordo because the language is built around trust in verification. If a package claims to be a release candidate, an external reviewer must quickly understand three things: what to check, how to run it, and where to see the machine-readable result.

In M48, handoff adds no new CLI commands and does not change the Process Rail. It only assembles a verification route around existing layers: `lint`, `compile`, `coverage`, `validate-state`, `validate-artifacts`, `consistency`, and `go-no-go`.

The main final-handoff rule is simple: the reviewer should not reconstruct the history of every milestone. They need a short route:

```text
README → final_handoff → external_audit → active packages → go-no-go report
```

The handoff package should therefore contain separate documents explaining:

- where to start;
- what is in scope;
- which commands to run;
- which results are expected;
- which questions to ask after review.

Final handoff also records honesty boundaries. If `ordo test` is a static runner, that must be visible. If the package is source-available rather than open-source, that must be visible. If the book PDF was not regenerated, that must also be stated explicitly.

Ordo must not look more complete than it is. The strength of the Process Rail is not in hiding incompleteness, but in showing exactly what has passed verification and what still requires a decision.
