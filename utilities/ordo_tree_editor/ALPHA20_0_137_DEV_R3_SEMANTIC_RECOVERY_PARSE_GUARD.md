# alpha.20.0.137-dev

Closes a remaining semantic-recovery contract leak: invalid `status` / parse / schema errors now enter bounded repair instead of leaking as a raw Execute Playbook error. A second invalid response becomes a controlled `contract_unsatisfiable_by_model` halt. No playbook source changes.
