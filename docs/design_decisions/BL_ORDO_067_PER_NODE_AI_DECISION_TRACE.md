# BL-ORDO-067 — Full Per-Node AI Interaction and Decision Debug Trace

Status: **design complete; runtime implementation remains a separate approved milestone**

## Problem

The existing session trace links a node, answer, transition, evidence report,
and state snapshot, but it does not reliably preserve the exact rendered
question/model message or a bounded explanation of why a decision was selected.
Without those facts, later analysis has to guess both what the analyst saw and
why the model chose the next transition.

## Goal

For every decision-bearing node, record the observable interaction and enough
context to replay and audit it. The record must distinguish observed facts from
the model's explanatory hypothesis. It must never persist hidden chain-of-thought.

The machine-readable contract is
[`BL_ORDO_067_DECISION_TRACE_CONTRACT.yaml`](../contracts/BL_ORDO_067_DECISION_TRACE_CONTRACT.yaml).

## Per-node record

The future runtime record is an append-only extension of the existing
`runtime/session.ordo.trace` and linked evidence/snapshot files. Each decision
step contains:

- the exact rendered user-facing question or model message;
- a digest of the prompt/context and the generation context/version;
- the analyst response as received, after contract redaction;
- the selected transition and applicable rules/gates;
- evidence references and evidence digests;
- state-before and state-after references plus a structured state diff;
- replay anchors: IR hash, source digest, node, step, prompt-context digest,
  model identity, and generation-parameter digest;
- a bounded `decision_summary` labelled as a hypothesis.

The existing answer, evidence, snapshot, and hash-chain fields remain
authoritative. The summary is explanatory only and cannot override them.

## Capture levels

- **off** — no new decision-interaction payload; existing required trace proof
  remains unchanged.
- **standard** — all observable facts, state references, replay anchor, and a
  bounded redacted summary.
- **diagnostic** — standard plus bounded redacted model-output metadata; no
  hidden reasoning or raw system prompt.

The default level is a deployment decision for the future implementation patch;
this design does not change the current default.

## Privacy and redaction

Before persistence, known secret patterns are redacted and fields are truncated
to contract limits. Credentials, access tokens, API keys, raw system prompts,
private reasoning, and chain-of-thought are forbidden fields. The trace records
the number of redactions and computes digests after redaction so replay and
integrity checks refer to what was actually stored.

## Deterministic replay

Replay uses the compiled IR hash, source digest, node and step identifiers,
prompt-context digest, model identity, and generation-parameter digest. A replay
must compare observable inputs, selected transition, evidence, and state diff;
the decision summary is not a pass/fail authority and may differ between model
runs.

## Implementation boundary

This milestone adds the contract and tests only. It does not alter the runtime,
`session_trace.py`, package profiles, archive contents, or current execution
semantics. A later implementation milestone must explicitly approve:

1. the trace schema/version migration;
2. runtime capture and redaction code;
3. evidence and snapshot integration;
4. replay and verification behavior;
5. migration/backward-compatibility policy.
