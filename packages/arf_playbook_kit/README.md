# ARF Playbook Kit

This directory is the canonical source for the chat-first ARF Playbook Kit.
Users download the reviewed ZIP from the current GitHub Release; they do not
need to clone this repository, install Python, or build the archive.

The source files and the active Applied Project Factory runtime are assembled
deterministically by
[`../../tools/build_arf_playbook_kit.py`](../../tools/build_arf_playbook_kit.py).
The next build version is declared in [`VERSION`](VERSION); it is not a
download claim. The current downloadable release is identified by
[`../../manifests/ARF_PLAYBOOK_KIT_CURRENT.json`](../../manifests/ARF_PLAYBOOK_KIT_CURRENT.json).

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
