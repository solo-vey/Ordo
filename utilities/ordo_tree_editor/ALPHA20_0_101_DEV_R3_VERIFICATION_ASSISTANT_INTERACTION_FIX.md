# alpha.20.0.101-dev — Verification Assistant interaction fix

- `Discuss in chat` now immediately asks the configured model for the first explanation.
- The bootstrap question is included in model context but hidden from the visible transcript.
- Verification Assistant now reuses the proven `explanation` structured-output field used by one-shot model explanations.
- Empty or malformed assistant responses become a visible chat error instead of an invisible empty assistant message.
- Enter sends a message.
- Ctrl+Enter inserts a new line.
- Follow-up questions continue in the same selected-verification conversation.
