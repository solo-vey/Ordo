# Chapter 83 — Choosing How a Playbook Is Delivered

Ordo separates **design truth** from **delivery format**. The analyst first completes one canonical playbook. Only after its contracts, paths, gates, state, and tests are stable does ARF ask how it should be delivered.

The choices are `engine_runtime`, `prompt_only`, or `both`. ARF recommends a target from risk, branching, gates, backtracking, enforcement requirements, and measured prompt-only evidence. The analyst confirms the choice.

`prompt_only` is not a cheaper equivalent of the engine. It keeps the structured authoring work but loses mechanical gates, validated runtime state, enforced transitions, CSG protection, and automatic evidence capture. ARF must display those losses before confirmation.

When evidence is missing, the process is regulated, consequences are high, or the decision is unclear, the safe default is `engine_runtime`. Because both outputs come from the same canonical source, a team can start with lightweight instructions and later escalate to the engine without redesigning the process.
