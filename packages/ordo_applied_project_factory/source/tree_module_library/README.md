# ARF Reusable Tree Module Library

This optional library provides build-time templates for recurring playbook
subtrees. It does not change an existing playbook at runtime.

Use `ordo tree-module list`, `inspect`, `instantiate`, `validate-instance`,
and `diff-instance` to inspect and materialize a template. Generated instances
are ordinary YAML and retain their source-template provenance.

The first templates cover one-document materialization and final package
handoff. Factory guidance may recommend either template, but the author must
review the generated preview and confirm it before it is inserted.
