# Decision Registry and Cross-Chat Handoff

Use the decision registry to retain accepted and pending decisions outside a
chat transcript. Each accepted decision is bound to the current canonical
source digest, a rationale, the package files that implement it, and one or
more declared test-case IDs.

```json
{
  "schema_version": "ordo.decision_registry.v1",
  "package_identity": {
    "package": "example.package",
    "package_version": "1.0.0",
    "source_sha256": "<canonical-source-sha256>"
  },
  "decisions": [
    {
      "id": "D_ROUTE_ACCEPTED",
      "node_id": "N_ROUTE",
      "lifecycle_status": "accepted",
      "rationale": "The analyst approved the selected route.",
      "implementing_files": ["source/program.ordo.yaml"],
      "tests": ["TC_ROUTE"]
    }
  ]
}
```

Validate the registry before creating a handoff:

```text
ordo validate-decision-registry PACKAGE --registry decision_registry.json
```

Create an explicit context file with the active node, completed artifacts,
open backlog, and pending decisions. Empty lists are valid, but every field
must be present so a receiving chat never guesses missing context.

```json
{
  "active_node": "N_ROUTE",
  "completed_artifacts": ["A_INVENTORY"],
  "open_backlog": ["BL-ORDO-103"],
  "pending_decisions": ["D_REVIEW"]
}
```

Export and restore the handoff:

```text
ordo export-cross-chat-handoff PACKAGE --registry decision_registry.json --state handoff_context.json --out handoff.json
ordo restore-cross-chat-handoff PACKAGE --registry decision_registry.json --handoff handoff.json
```

The exported handoff is hash-bound to the canonical source and registry. The
restore command is context-only: it verifies the handoff and writes a report,
but it does not replay execution, roll back a session, or mutate runtime state.
It rejects missing context, unknown active nodes, stale canonical digests,
changed registry revisions, conflicting accepted-decision sets, and modified
handoff content.
