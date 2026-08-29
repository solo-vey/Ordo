# alpha.20.0.110-dev — Model Chat and authoritative graph reference badges

## Graph reference badges
Graph badges now use the same resolved package-resource authority as the References inspector. Paths merely mentioned in commands or prose (for example generated outputs or reports) no longer create false MD/JSON badges unless they resolve to actual package resources.

## Model Chat
Adds an independent Model Chat workspace that calls the configured model directly without executing a playbook runtime. It supports conversation history, text-file attachments, ZIP text-resource unpacking for model context, generated text files, deterministic source-package ZIP assembly, and a right-side Ordo tree preview for generated/uploaded YAML or ZIP playbooks.

Model Chat is intentionally separate from playbook execution: no execution pointer, state patch, gate traversal, or playbook runtime semantics are applied.
