# DD-ORDO-M65-001 — Prompt Registry Standard

Status: Accepted
Date: 2026-07-09
Milestone: M65.0

## Context

Applied process packages increasingly need small helper prompts for package startup, node explanation, clarification, artifact generation, validation help, and repair flows. Before M65.0 these prompts could exist as ad-hoc files or inline node text, but they were not a first-class package contract element.

This creates drift: prompt files may be useful but undiscoverable, unversioned, not referenced from nodes, missing from manifests, and not validated against process authority.

## Decision

Add `prompt_registry` and `prompt_refs` as Ordo/APF package-level source/schema conventions.

A prompt registry records prompt id, type, audience, path, attachment target, required status, language, lifecycle, visibility, state-change policy, and validation policy.

Nodes and other package elements may reference prompts through `prompt_refs`.

## Authority boundary

Prompt files are supportive guidance only. They may guide explanation, clarification, formatting, artifact drafting, and repair communication. They must not override gates, transitions, state requirements, runtime evidence, program contracts, or human approval.

## Scope

M65.0 is docs/schema/lint-profile design only.

It does not add runtime core behavior, compiler enforcement, CLI commands, opcodes, deterministic prompt interpretation, or an APF source YAML rewrite.

## Consequences

Future package validators can check prompt path existence, prompt ref resolution, manifest coverage, quick-start discoverability, and prompt authority safety.

Applied factories such as History Event Analysis Package Factory can gradually add `prompts/QUICK_START_PROMPT.md`, node helper prompts, artifact helper prompts, and repair helper prompts without mixing conversation guidance into structural node logic.
