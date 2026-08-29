# alpha.20.0.142-dev

Closes three generic issues demonstrated by runtime debug evidence.

1. `next_target` is accepted as a structural alias of canonical `next_id`.
2. Semantic recovery now receives the exact declared operation variant contract on the first request and repair request. The generic prompt includes all required StatePatch metadata (`basis`, `reason`) and contains no playbook-specific field examples.
3. Provider capability probe evidence is persisted to `~/.ordo_tree_editor/provider_capabilities.json`, keyed by provider/base_url/model/api_style, so strict-schema capability survives Editor process restarts without crossing provider/model boundaries.

No playbook/domain source changed.
