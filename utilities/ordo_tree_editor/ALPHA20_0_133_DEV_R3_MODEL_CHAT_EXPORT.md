# alpha.20.0.133-dev

Adds two Model Chat exports.

## Export Chat
Downloads a human-readable Markdown transcript.

## Export Chat Debug
Downloads a ZIP containing:
- conversation.json
- agent_trace.json
- tool_calls.json
- usage_history.json
- workspace_head.json
- workspace_index.json
- attachments.json (metadata only)
- generated_files.json (metadata only)
- provider_info.json (allowlisted non-secret fields)
- errors.json
- session.json
- README.md

The browser accumulates agent trace, usage and errors across the current Model Chat session. API keys and attachment bodies are excluded from the debug archive.
