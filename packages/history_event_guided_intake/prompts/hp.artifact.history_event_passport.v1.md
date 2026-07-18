# Artifact Helper — History Event Passport generation

Use this helper when generating or reviewing `01_HISTORY_EVENT_PASSPORT_<ALIAS>.md`.

## Goal

Keep the passport as the canonical contract view derived from confirmed state.

## Include from confirmed state

- event goal;
- selected path;
- event alias;
- Ukrainian and English names;
- source field / source contract;
- value semantics and normalization;
- QA and test strategy contract;
- open questions if any remain.

## Do not

- Do not invent requirements, URLs, Jira keys, Confluence links, handlers, or mappings.
- Do not hide open questions.
- Do not let a helper prompt override `program_contract` or approval gates.

## Authority boundary

This helper shapes passport text only. It cannot mark the package ready or replace validation evidence.
