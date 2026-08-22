Execute this playbook in Model Mode from the canonical graph. Follow current_node exactly, apply state diffs, follow declared gates/recovery, and persist state. Do not assume CLI authority.

Context discipline: do not recursively read package contents; do not preload the full graph, prompts, or knowledge. Search for the active node/gate and load only its declared contract/references. Never read `authoring/` or `design/` during normal execution.
