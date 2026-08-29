# ARF Playbook Kit (legacy)

> **Deprecation notice:** New playbooks should be created with the Vibe ARF
> package. This lower-level kit remains available for compatibility,
> migration, and engineering workflows and is scheduled for deprecation.

This directory is the legacy source for the lower-level chat-first ARF Playbook Kit.
It is retained for compatibility, migration, and engineering workflows. New users
should download the current Vibe ARF release instead; they do not need to clone
this repository, install Python, or build either archive.

The source files and the active Applied Project Factory runtime are assembled
deterministically by
[`../../tools/build_arf_playbook_kit.py`](../../tools/build_arf_playbook_kit.py).
The next build version is declared in [`VERSION`](VERSION); it is not a
download claim. The historical ARF release pointer is identified by
[`../../manifests/ARF_PLAYBOOK_KIT_CURRENT.json`](../../manifests/ARF_PLAYBOOK_KIT_CURRENT.json).
The current recommended download route is the
[`Vibe ARF release`](../../manifests/VIBE_ARF_CURRENT.json).

[`manifest.json`](manifest.json) records the immutable metadata for the
currently published release. A new version only becomes current after its
GitHub Release assets are published and the current pointer is updated in the
same reviewed change.

The Kit is a chat-first authoring package. Its full ARF build contains the
active factory source, freshly compiled runtime, embedded CLI, local
contracts, templates, integration material, and an empty user workspace. It
helps a user create, review, test, and improve a playbook. It does not claim
that conversational validation is equivalent to deterministic CLI or
release-grade validation.

The next kit build also includes the expanded, English-language candidate
Playbook Regression Harness (PRH) 1.7.0 and Playbook Regression Playbook (PRP)
0.2.0-alpha.1 under `regression/`. PRH is the technical regression utility;
PRP orchestrates baseline-versus-candidate comparison. Their full pilot and
promotion remain candidate-stage work.

The legacy ARF Kit 0.4.10 snapshot also packages the gate-aware graph validation contour, reusable tree-module library, companion utility set including the local Ordo Tree Editor, guided Mode 5 migration
working-artifact templates, and the release-build
tooling described in `source/ARF_PACKAGE_README.md`, so the downloadable
artifact documents both its included capabilities and its deliberate
repository-level exclusions.

It includes the complete package-local `language/` anti-pattern contour so the
ARF integration tests do not need an external language-repository checkout.
