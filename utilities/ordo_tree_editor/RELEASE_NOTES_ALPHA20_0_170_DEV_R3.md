# Ordo Tree Editor 0.2.0-alpha.20.0.170-dev

## Shared chat message copy action

- Added one compact message-level clipboard action to every UI surface that supports direct conversation with the configured model:
  - Execute Playbook;
  - Model Chat;
  - Playbook Settings assistant;
  - Data Flow Inspector assistant;
  - Verification assistant.
- Left-aligned assistant messages show the 18×18 px copy action immediately below the message on the left.
- Right-aligned analyst/user messages show it immediately below the message on the right.
- The action copies the original message text only; UI chrome, token badges, tool/activity indicators, attachments and file cards are excluded.
- Clipboard handling uses `navigator.clipboard.writeText` with a DOM `execCommand("copy")` fallback for local browser contexts where the modern clipboard API is unavailable.
- Existing specialized `Copy YAML` behavior in the Playbook Settings assistant now shares the same clipboard fallback.
- No runtime/compiler/canonical Ordo semantics changed.

## Verification

- Added `test_r3_chat_message_copy_button.js` to guard shared coverage across all five model-conversation surfaces and left/right alignment behavior.
