# Ordo Tree Editor alpha.20.0.162-dev R3

## Language-first control-flow projection and semantic-recovery route preservation

External Simulation Kit testing exposed two shared runtime/compiler defects in `.161-dev`.

### Fixed: arbitrary payload strings could become routes

The shared semantic classifier previously recursively scanned arbitrary source values for strings equal to known node IDs. A package-tool argument such as:

```yaml
args: [--step, N_ART01_PASSPORT]
```

could therefore manufacture a false runtime route `args.[1] -> N_ART01_PASSPORT`.

`.162-dev` derives runtime routes only from formal route-bearing source structures already handled by `declared_routes` (`next`, gate outcomes, `on_answer`, transitions, navigation contract, declared dynamic routes, artifact missing behavior). Tool arguments, resource paths, templates, bindings and other payload strings are not control-flow merely because they equal a node ID.

### Fixed: semantic recovery `next` alias could be lost

Safe semantic recovery accepts a bounded structured envelope whose runtime continuation field is `next_id`. Compatibility normalization already handled `next_node` / `next_target`; `.162-dev` also normalizes `next -> next_id` and removes the alias before route application.

This prevents a valid recovery decision from committing state while later surfacing as `missing_route` merely because the response used the common `next` alias.

### TDD

On `.161-dev` the new regression reproduces both failures:

- false `args.[1]` execution route is present;
- recovery candidate retains `next` but has no `next_id`.

On `.162-dev`:

- only declared `next -> G_VALIDATE` remains;
- recovery normalization produces `next_id=G_VALIDATE` with `next_to_next_id` evidence.

Canonical Ordo language/schema and playbook sources are unchanged.
