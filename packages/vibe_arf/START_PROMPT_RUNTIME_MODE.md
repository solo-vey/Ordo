# START PROMPT — Vibe ARF Runtime Mode

Read `START_HERE_RUNTIME_MODE.md` and execute its runtime loading protocol.
Use the packaged canonical Ordo source, verification profile, tools, laws and evidence.
Do not reconstruct workflow rules from memory.


## Single responsibility architecture (alpha.18)
Each executable node owns one cohesive responsibility. A deterministic RUN node produces evidence; a following
mechanical gate decides PASS/FAIL routing. Materialization, validation and handoff are separate responsibilities.
Several commands may stay inside one RUN node only when they form one cohesive evidence report.


## Information-first rule (alpha.24)
During authoring, load/use the persisted `authoring/` information model and its deterministic gates. Do not synthesize a process graph before the information model is valid, and do not accept a generated source whose AIM ↔ Ordo projection is unbound or inconsistent.

## Authority/simulation rule (alpha.26)
Use persisted review bundles, proposal/canonical separation and approval-ledger contracts. For runnable generated candidates, require exact-ZIP pinned simulation evidence before analyst-ready handoff when applicable. Classify adapter/fixture/playbook ownership before any repair; never alter canonical-valid Ordo to hide an adapter defect.

## Default debug/handoff mode
Default debug/handoff is ON: initialize `debug_handoff/working/` at bootstrap, accumulate handoff evidence throughout the run, and emit concise user-visible progress events at meaningful stage/node/gate transitions. Follow the detailed contract in `START_HERE_RUNTIME_MODE.md` and `source/default-debug-handoff-progress-policy.json`; an explicit quiet-chat request may reduce messages but never disables evidence capture.
