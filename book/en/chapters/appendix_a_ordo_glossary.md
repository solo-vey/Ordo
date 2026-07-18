# Appendix A. Ordo Glossary

This glossary defines the terms used by the current Ordo language, compiler, runtime, package, and governance layers. Definitions are normative unless a referenced specification narrows them further.

## Active node

The single node that currently owns execution focus in a deterministic run.

## Artifact

A declared output produced by a program, playbook, compiler, runtime, or validation process.

## Assertion

A machine-checkable statement that must hold for a run, package, or artifact.

## Canonical source

The authoritative representation from which derived files are generated or validated.

## Contract

A structured declaration of required inputs, fields, outputs, statuses, and acceptance conditions.

## Control level

The degree of formal control applied to execution: light, standard, or strict.

## Derived artifact

A generated representation that must never silently become the source of truth.

## Entry mode

An explicitly authorized way to enter a node, such as root, resume, retry, recovery, or migration.

## Execution trace

An append-only record of node entries, decisions, state changes, gates, and outputs.

## Fail closed

A policy in which missing or invalid evidence blocks progress rather than being treated as success.

## Flow reuse

A first-class reference to a shared continuation or join whose state mapping and return behavior are explicit.

## Gate

A deterministic control point that permits or blocks progress based on declared evidence.

## Graph contract

The declaration of entry, terminal, cycle, provenance, and reachability expectations for a process graph.

## Node context

The bounded state, knowledge, tools, and output contract visible to one active node.

## Opcode

A semantic operation in Ordo IR, such as NODE.DEF, GATE.CHECK, or TRACE.LOG.

## Pattern

A governed reusable process structure with applicability rules, evidence, lifecycle, and composition constraints.

## Process Rail

A structured execution rail that preserves progress, current focus, and controlled deviation handling.

## Prompt registry

A governed registry of prompt assets, stable IDs, checksums, lifecycle, and authority boundaries.

## Provenance

Evidence of where a transition, value, artifact, prompt, or decision came from.

## Runtime checkpoint

A restorable state snapshot with identity, integrity, and continuation information.

## Source construct

A top-level YAML construct accepted by the source language and lowered by the compiler.

## State projection

An explicit subset of state imported into or exported from a node or shared flow.

## Terminal outcome

A declared successful, blocked, cancelled, or otherwise controlled end state.

## Validation profile

A named collection of checks and severities applied to a source or package.

## Canonical capability names

The following capability names are copied from the current capability catalog and should not be replaced with improvised aliases.

# Ordo Capability Catalog

The machine-readable registry is `capability_catalog.yaml`.

## Conversation Scope Guard

- Contract: `ORDO-CAP-CSG-001`
- Source construct: `conversation_scope_guard`
- Core default: disabled
- Status: language-integrated optional specification
- Opcodes: `CONVERSATION.SCOPE.DEF`, `DEVIATION.CLASSIFY`, `DEVIATION.HANDLE`, `DEVIATION.ESCALATE`, `STATE.PROTECT`, `PROCESS.PAUSE`, `PROCESS.RESUME`, `PROCESS.EXIT`
- Trace events: `conversation.deviation.detected`, `conversation.deviation.classified`, `conversation.redirect.emitted`, `conversation.escalation.changed`, `conversation.scope_guard.bypassed_for_control_intent`, `conversation.scope_guard.bypassed_for_safety`, `process.pause.requested`, `process.paused`, `process.resume.requested`, `process.resumed`, `process.exit.requested`, `process.exited`
