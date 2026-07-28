# Playbook Regression Harness 1.4.0
## Chat-Native Multi-Chat Backend v1

This package formalizes chat-native execution as an official PRH backend.

It supports:
- running scenarios in separate chats;
- declaring the selected chat/model label;
- assigning different repetition counts per model/chat;
- baseline/candidate isolation;
- continuation and resume;
- normalized result packages;
- merging results from multiple chats;
- cross-chat and cross-model comparison;
- strict evidence labeling as `chat_native`.

This backend does not create provider-level API evidence and cannot by itself issue a production `GO`.
