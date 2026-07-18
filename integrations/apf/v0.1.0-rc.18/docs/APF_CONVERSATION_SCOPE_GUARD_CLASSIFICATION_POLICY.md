# CSG-1 — Deviation Classification Policy

Before any redirect or state mutation, the generated playbook must classify the user message against the active process context. A message that does not directly answer the active question is not automatically unrelated.

## Priority

Safety and emergency messages have highest priority. Controlled process intents—exit, pause, resume, correction, backtracking, requirement change, process-meta questions, and clarification—must remain available in every guard mode.

## Ambiguity

Low-confidence classification becomes `unclassifiable_input`. The runtime asks a clarifying question and preserves node, path, collected state, and confirmation status.

## State boundary

`unrelated_topic` and `unclassifiable_input` cannot complete a node, change path, confirm state, or erase collected data. Classification itself is evidence, not a business decision.
