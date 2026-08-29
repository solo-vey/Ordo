# alpha.20.0.106-dev — Preparation failure modal usability

- The preparation dialog has a bounded viewport height and its content body scrolls independently.
- Scrollbar track/background is transparent; only a neutral thumb is visible.
- Failure diagnostics are separated into adjacent `Human-readable` and `Technical details` tabs.
- Technical tab contains structured diagnostics, raw diagnostics, and `Download diagnostics JSON`.
- Preparation modal actions use delegated click handling because the modal markup is placed after `app.js`; close/download/tab controls therefore work regardless of DOM parse order.
- Escape and backdrop close remain supported.
