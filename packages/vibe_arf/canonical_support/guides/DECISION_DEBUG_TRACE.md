# Decision Debug Trace

When the ARF process reaches a decision-bearing node, preserve the complete
interaction rather than only the node identifier and the analyst's answer.

Record:

1. the exact question or model message shown to the analyst;
2. the question/template reference and context/version digest when available;
3. the analyst's response;
4. the selected transition;
5. applicable rules and evidence references;
6. state-before/state-after references and the state diff;
7. a detailed but bounded `decision_summary` explaining why the path was chosen;
8. a replay anchor for the node/state boundary.

The summary may be several sentences when needed for useful debugging, but it
is a redacted explanatory report, not hidden chain-of-thought. Never copy
private reasoning, scratchpads, system prompts, credentials, tokens, or
personal data into the trace. Treat the summary as a hypothesis and verify it
against the recorded question, response, rules, evidence, transition, and
state change.

```text
facts:    rendered interaction + response + evidence + transition + state diff
summary:  model-reported explanation of the decision
replay:   later analysis starting from the preserved node/state boundary
```
