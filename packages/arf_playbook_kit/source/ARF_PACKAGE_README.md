# ARF Playbook Factory

This is the standalone ARF package for creating a new Ordo playbook in a language-model chat.

## Start in chat

1. Upload the complete ZIP without unpacking or changing it.
2. Ask the model to read `guides/START_PROMPT.md`.
3. Follow the guided intake and create your new playbook in `workspace/`.
4. Use the included validation and improvement instructions before accepting the result.

## Package boundaries

The archive contains the active Applied Project Factory source, a freshly compiled runtime representation, the embedded runtime CLI, local integration contracts, output templates, tests, and chat-facing guides.

The archive intentionally excludes repository history, previous validation reports, release evidence, generated examples, and unrelated developer material. The package is a standalone ARF product artifact, not a repository snapshot.

## Authoring and runtime rules

- Use `guides/START_HERE.md` and `guides/START_PROMPT.md` as the chat-facing entry route.
- Use `START_HERE_RUNTIME_MODE.md` for the runtime protocol.
- Do not edit files under `compiled/` directly.
- Put all new user work under `workspace/`.
- The embedded CLI is an optional deterministic verification route; it is not required for the initial chat-first creation route.

## Build provenance

The canonical builder is `tools/build_arf_playbook_kit.py` in the Ordo repository. The source package is `packages/ordo_applied_project_factory/`. The build specification remains source-only and is not shipped in the user ZIP.
