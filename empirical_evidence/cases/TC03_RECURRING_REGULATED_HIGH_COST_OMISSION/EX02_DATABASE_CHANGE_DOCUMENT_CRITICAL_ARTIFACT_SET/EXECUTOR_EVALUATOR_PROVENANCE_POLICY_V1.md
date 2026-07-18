# Executor–Evaluator Provenance Policy v1

## Purpose

This policy records whether RUN execution and scoring were performed in the same or different chats/models. It supplements scoring evidence and does not alter Process, Documents, or Final scores.

## Current retrospective status

For every currently accepted result in TC03-EX02:

- executor model: `GPT-5.6 Thinking`;
- evaluator model: `GPT-5.6 Thinking`;
- relation: `different_chat_same_model`;
- different chat: `true`;
- different model: `false`;
- verification level: `user_attested_not_cryptographically_verified`.

The different-chat claim is based on the user's attestation and the transfer of returned RUN archives into the evaluation chat. No execution/evaluation chat identifiers or cryptographic session attestations are available. Therefore this evidence supports chat-level separation, but not model-level independence or cryptographically verified independence.

## Required values

- `different_chat_different_model`
- `different_chat_same_model`
- `same_chat`
- `unknown`

## Future evidence requirement

Future runs should record executor/evaluator model identifiers, chat/session identifiers when available, timestamps, input archive SHA-256, and the SHA-256 of the exact archive evaluated.
