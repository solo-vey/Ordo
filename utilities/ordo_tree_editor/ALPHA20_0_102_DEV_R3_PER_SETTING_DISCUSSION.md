# alpha.20.0.102-dev — Per-setting discussion and ordering

- Playbook Settings is split into `Specified settings` and `Not specified settings`, with all explicitly declared values first.
- Logical language groups remain visible inside each status block.
- Every setting has `Discuss in chat` when a model is configured.
- Selecting a setting establishes focused context in the right AI Settings Assistant and immediately requests the first explanation.
- The hidden bootstrap request asks for the setting purpose, current value or absence, all documented alternatives, effects on playbook/chat behavior, and documented interactions with other settings.
- Follow-up conversation remains read-only. The assistant may propose YAML but never edits the playbook.
