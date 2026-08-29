# Multi-chat design

## Dimensions

PRH separates three dimensions:

1. **Playbook version**
   - baseline
   - candidate

2. **Declared model label**
   - the model selected or stated by the user in the chat UI;
   - not provider-verified.

3. **Chat instance**
   - a separate conversation and context;
   - used as an approximate isolation boundary.

## Metrics

- Within-chat stability: repeated runs in one chat/model assignment.
- Cross-chat reproducibility: same model label and scenario in separate chats.
- Cross-model portability: same scenario and playbook version across different model labels.

## Recommended campaign

For a fast pilot:
- one main scenario;
- two playbook versions;
- one run in each of two model chats.

For stability:
- at least three repetitions per version within each model/chat.

For cross-chat reproducibility:
- use at least two separate chats with the same declared model label.

## Evidence limitation

The UI model label is user-declared metadata. It is not equivalent to provider API provenance.
