# Chat-first onboarding

Chat-first is the primary creation and learning route for Ordo. A language model guides the user from a natural-language process description to a reviewed playbook package. CLI and Python tooling remain optional deterministic helpers for automation, reproducibility, CI, and release validation.

## Canonical starter

- [`starter ZIP`](../examples/chat_first_playbook_starter/ORDO_CHAT_FIRST_PLAYBOOK_STARTER.zip)
- [`starter source and manifest`](../examples/chat_first_playbook_starter/)
- [`five-step quickstart`](QUICKSTART.md)

## Required interaction contract

The AI Ordo Developer must:

1. read the complete starter before asking questions;
2. preserve the user's process intent and authority;
3. ask only the questions needed to close material gaps;
4. produce an explicit playbook draft with inputs, steps, gates, outputs, and failure behavior;
5. run a conversational validation and dry-run without overstating deterministic enforcement;
6. explain defects and apply approved improvements;
7. return a complete, clearly inventoried package.

## Tooling boundary

Conversational validation is useful for learning and drafting but is not release evidence. The CLI and delivery gates provide mechanical validation when the user needs automation or a release-grade result.

## Completion criteria

A new user succeeds when they can download one archive, upload it to a chat, paste one prompt, create a first playbook, review a dry-run, request an improvement, and receive a final package without installing Python.
