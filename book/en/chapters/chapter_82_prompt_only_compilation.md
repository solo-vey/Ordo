# Chapter 82. One Playbook, Two Execution Targets

Ordo can now treat a playbook as an intermediate representation. The same canonical source can produce a full engine-runtime package or a lightweight prompt-only package.

Prompt-only compilation preserves authoring discipline, explicit structure, and a single source of truth. It does not preserve mechanical gates, enforced state transitions, CSG protection, or automatic runtime evidence. These losses are always declared in a machine-readable manifest.

The choice is empirical rather than ideological: use prompt-only when repeated tests, including branch and backtrack cases, meet the configured threshold. Escalate to the engine when they do not, and revalidate after model, provider, source, compiler, or policy changes.
