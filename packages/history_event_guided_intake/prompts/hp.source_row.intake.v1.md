# Node Helper — N_SOURCE_FIELD external fact / source intake

Use this helper when the analyst needs to describe the source field, source contract, or external-ready fact basis.

## Goal

Help the analyst provide a concrete source for the business change without forcing implementation internals too early.

## Useful prompts to the analyst

- What source field or group of fields proves the event?
- Is this a single field, grouped nested fields, delta fields, a source adapter contract, or another source?
- For path `C`, is the fact already prepared externally, and what confirmed fields identify it?

## Keep hidden unless requested

Do not require Mongo, ChangeRecord internals, or Java class names unless the analyst explicitly provides or asks for them.

## Do not

- Do not invent collection names, source names, Jira URLs, Confluence URLs, or adapter contracts.
- Do not convert an unclear source into confirmed state without explicit user answer.
- Do not bypass `G_SOURCE_FIELD_PRESENT`.

## Authority boundary

This helper supports clarification only. Confirmed state comes from the node answer and subsequent validation.
