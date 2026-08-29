# Alpha20.0.148-dev R3 — Model Chat attachment context hardening

Generic Model Chat/runtime fix. No playbook/domain semantics changed. Release 1 unchanged.

## Fixed

- Files attached to the latest free-chat turn are now exposed explicitly to the model as `current_attachments` after successful workspace ingestion.
- `current_attachments` carries the actual workspace path and ZIP extraction path, so a model can inspect newly supplied material even when an older large workspace dominates `workspace_head.entrypoint_candidates`.
- The agent contract now forbids claiming that no file was attached when `current_attachments` is non-empty.
- If the browser preserves a file in the newest user message but omits the parallel `attachments` transport field, the backend falls back to that newest message file list.
- Prior user-message file metadata is retained in conversation context without embedding file bodies.
- Model Chat send and debug export now use the same workspace/session identity.
- Debug export now discovers attachment metadata from conversation messages and strips attachment bodies from `conversation.json`; this both makes diagnostics truthful and prevents Base64 payload duplication.

## Regression coverage

- second/subsequent ZIP attachment in a persistent free-chat workspace;
- explicit latest-turn attachment context;
- browser transport fallback from message file-card;
- common Model Chat send/export session identity;
- debug-export body exclusion.
