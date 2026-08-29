# alpha.20.0.53-dev — browser chat layout fix

- Playbook load always activates `Execute Playbook`.
- Fixed an escaped-newline serialization defect that prevented the .52 browser stylesheet from applying.
- Rebased live transcript to a white ChatGPT-style flow: assistant content unframed, analyst bubbles right-aligned, system/runtime rows subdued.
- Composer is rendered as one rounded shell with attach/send-stop controls inside.
- No runtime/playbook semantics changed.
