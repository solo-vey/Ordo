# alpha.20.0.146-dev

Fixes a first-page startup crash introduced when the standalone Upload YAML control was removed.

Root cause:
`app.js` still executed an unconditional
`document.querySelector("#file-input").addEventListener(...)`.
With the control absent, initialization aborted on `null.addEventListener`,
so all later button bindings on the first page were skipped.

Changes:
- legacy YAML input listener is optional-safe;
- legacy canvas "open YAML" action is optional-safe;
- regression test prevents optional DOM controls from aborting initialization.

No runtime/playbook semantics changed.
