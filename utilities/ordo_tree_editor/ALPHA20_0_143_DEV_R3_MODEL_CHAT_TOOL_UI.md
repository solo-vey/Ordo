# alpha.20.0.143-dev

Fixes Model Chat tool-call leakage into the visible conversation.

Observed evidence:
the model returned the generic envelope
`{"tool_call":{"name":"workspace.list","arguments":{...}}}`.
The parser did not recognize that structural form, classified it as `final`,
and the frontend rendered the raw JSON to the user.

Changes:
- recognizes canonical `type: tool`, top-level `tool_call`, and `call_tool`;
- tool calls/results remain inside the agent loop;
- the visible conversation receives only final model responses;
- tool activity is optionally surfaced as quiet status rows;
- full internal trace remains in Export Chat Debug.

No playbook behavior is involved.
