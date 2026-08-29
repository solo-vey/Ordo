# alpha.20.0.77-dev — Replay print grid isolation

UI/print-only regression fix.

Root cause:
- print replay used `<main class="replay-print-shell">`;
- global Editor `main { display:grid; ... }` workspace rules applied inside the print window;
- the transcript was therefore squeezed into a workspace grid column.

Fix:
- print shell is now a neutral `<div>`;
- print shell explicitly uses `display:block`, `width:100%`, and `box-sizing:border-box` in print mode;
- workspace grid layout can no longer affect Replay PDF geometry.

No runtime, compiler, or playbook semantic changes.
