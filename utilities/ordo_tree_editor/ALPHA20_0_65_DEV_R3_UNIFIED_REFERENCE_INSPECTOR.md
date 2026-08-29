# alpha.20.0.65-dev — unified reference inspector

UI-only R3 inspector simplification.

## Changes
- The node inspector now has one top-level tab set:
  - Parameters
  - YAML
  - References
- Removed the nested Overview / Template / Parameters / References / Raw tab set.
- Template, bindings, validator, schema, specification, resource, and reference files are all shown through the References tab.
- Resolved package references reuse the same inline Resource Preview mechanism.
- Derived `OUT::...` nodes now make the parent inspector form visible.
- Output nodes expose:
  - Parameters: output identity and producer nodes;
  - YAML: derived/raw producer record;
  - References: aggregated package references from producer nodes.

No playbook, Compiler semantic, or runtime execution semantic changes.
