# ARF Reusable Tree Module Library

This optional library provides build-time templates for recurring playbook
subtrees. It does not change an existing playbook at runtime.

Use `ordo tree-module list`, `inspect`, `instantiate`, `validate-instance`,
and `diff-instance` to inspect and materialize a template. Generated instances
are ordinary YAML and retain their source-template provenance.

The templates cover one-document materialization, final package handoff, and
application-code implementation changes. Factory guidance may recommend a
template, but the author must review the generated preview and confirm it
before it is inserted.

Available templates:

- `DOCUMENT_MATERIALIZATION_LIFECYCLE` — materialize and review one output
  document.
- `PACKAGE_HANDOFF_LIFECYCLE` — validate, archive, and hand off a package.
- `IMPLEMENTATION_CHANGE_LIFECYCLE` — inspect an application-module baseline,
  synchronize an implementation prompt, choose direct change or developer
  handoff, validate the candidate, and return to the host playbook.

The implementation-change template includes usage, integration, and mapping
notes under `docs/`, plus a domain-neutral instance and generated example under
`examples/`.
