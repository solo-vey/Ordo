# APF A2 Interaction, Process Rail, and Conversation Policy

## Status

`A2-applied-working-state`

## Purpose

This policy aligns APF with the Ordo v0.12 M64.2 conventions for `interaction_model`, `process_rail`, and `conversation_semantics` without changing APF's approved playbook-authoring methodology.

## Authority boundary

- The human owns content meaning, process approval, backlog activation, and final release confirmation.
- The AI guides the declared process, drafts artifacts, explains choices, and recommends routing.
- CLI/helper tools perform only declared deterministic or mechanical checks.
- Raw tool output is summarized before presentation unless the user explicitly asks for the raw evidence.

## Deviation and resume

A side question or temporary deviation does not answer the current required checkpoint. After handling it, APF resumes at the earliest unresolved required checkpoint.

## Backtracking

Backtracking is restricted but allowed. Changing an earlier confirmed answer:

1. invalidates dependent downstream state;
2. marks dependent artifacts as not current;
3. preserves them as historical evidence until reconfirmation;
4. requires impact review before progress continues.

## Skip-ahead handling

Information about a future step may be captured as future context, but it does not advance the process or close any current gate.

## Ambiguous input

Ambiguous or unmatched input must be clarified before state mutation. Clarifications do not advance the active node.

## Approval semantics

An approval closes only the explicitly identified gate or artifact. It does not imply approval of unrelated downstream decisions.

## Enforcement boundary

These rules are package-level and AI-guided conventions. A2 does not claim:

- a deterministic natural-language classifier;
- new Ordo opcodes;
- compiler changes;
- generalized runtime-core enforcement;
- automatic state invalidation unless supported by the concrete runtime/package implementation.
