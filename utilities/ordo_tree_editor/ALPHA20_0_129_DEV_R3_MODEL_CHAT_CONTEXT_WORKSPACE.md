# alpha.20.0.129-dev

Model Chat context handling was hardened for large attachments.

## Adaptive context budget
For OpenAI-compatible chat-completion HTTP 400 context-window errors, Editor parses the provider-reported maximum context and input-token count, reduces `max_tokens` with a safety reserve, and retries once.

Example: 35,000 context / 27,001 input / 8,000 requested output becomes a bounded retry instead of an immediate failure.

## ZIP workspace compaction
ZIP attachments are no longer expanded into up to 24 large text bodies in one prompt.

Instead Model Chat sends:
- an archive index (path, size, text-candidate flag);
- a small set of likely startup/prompt/README/instruction/manifest files;
- workspace summary metadata.

This is a first step toward the local workspace/agent model: package discovery is separated from blindly embedding the entire archive into the model context.
