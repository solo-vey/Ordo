# Reusable Tree Modules

ARF includes an optional library of reusable process fragments. A template is
expanded before the target playbook runs, so the resulting YAML has no runtime
dependency on the library.

Available templates:

- `DOCUMENT_MATERIALIZATION_LIFECYCLE` — one output document from readiness
  through validation, review, revision, and completion.
- `PACKAGE_HANDOFF_LIFECYCLE` — required-artifact validation, evidence export,
  manifesting, archive-integrity validation, and handoff.
- `IMPLEMENTATION_CHANGE_LIFECYCLE` — application-module baseline intake,
  prompt synchronization, direct-change or developer-handoff selection,
  candidate validation, and return to the host playbook.

## Safe authoring route

1. Run `ordo tree-module list <package>` and inspect the selected template.
2. Prepare the instance parameters, including unique `instance_id` and
   `id_prefix`, plus explicit entry and success-exit nodes.
3. Run `instantiate`; it blocks unresolved placeholders and host conflicts.
4. Review the generated nodes, state fields, gates, bindings, and provenance.
5. Merge the ordinary YAML fragment only after explicit author confirmation.

Factory may recommend a template when an output artifact, final handoff, or
application-code implementation continuation is being designed. Recommendation
is optional: declining it continues the manual authoring route unchanged.

Use `validate-instance` before merging and `diff-instance` to report local
overrides after later editing. Provenance records the template, library version,
parameters digest, generated-fragment digest, and declared local overrides.
