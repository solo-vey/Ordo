# DD-APF-PMP-001 — Downstream Playbook Mini-Prompts Before Internal APF Mini-Prompts

**Status:** accepted  
**Date:** 2026-07-10  
**Decision owner:** process owner

## Context

Ordo v0.12 and APF rc.13 provide the technical foundation for semantic prompt identities, manifests, checksums, controlled attachment phases and package-level application evidence. APF, however, does not yet contain a complete authoring workflow for deciding when a newly created playbook needs a local mini-prompt, obtaining human approval, and packaging that prompt with the playbook.

Applying mini-prompts directly to APF's own internal nodes before validating the design on a real downstream playbook would mix two different concerns and would make it difficult to evaluate whether the mechanism itself is useful.

## Decision

Implement mini-prompt authoring support first as an APF capability for **playbooks created by APF**.

The first implementation line is `BL-APF-002A — Playbook-authored mini-prompt support`.

The internal APF node review is separated into `BL-APF-002B — Internal APF node mini-prompt applicability review` and remains deferred until a real playbook pilot and retrospective are completed.

## Required design properties

- Contract first, prompt second.
- Human approval before activation.
- Semantic `prompt_id` independent of `node_id`.
- Separate registry for each generated playbook.
- No prompt-owned navigation or gate authority.
- Validation and test scenarios for every approved prompt.
- Conditional prompt artifacts: simple playbooks must not receive an empty prompt subsystem unnecessarily.

## Consequences

- APF authoring flow will gain a Prompt Sufficiency Review phase.
- Generated playbook package contracts and templates will gain optional prompt artifacts.
- Human confirmation discipline will include prompt necessity, text, scope, use phase and test scenarios.
- No APF internal mini-prompts are introduced by this decision.
- BL-APF-001 remains independent and deferred.
