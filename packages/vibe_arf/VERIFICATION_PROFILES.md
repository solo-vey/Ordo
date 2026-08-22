# Vibe ARF verification profiles

- `BASE` is the default repository-native profile. It validates source, graph,
  authoring inputs, current Ordo language/CLI bindings, and deterministic
  package construction. It does not require Editor or Simulation Kit assets.
- `EDITOR` adds the separately distributed Tree Editor and its visible
  architecture projection.
- `SIMULATION` adds the separately supplied Playbook Simulation Kit and its
  strict replay/evidence checks.

The Vibe release builder must generate production evidence in an isolated
staging directory. Generated evidence is never committed as package source.
