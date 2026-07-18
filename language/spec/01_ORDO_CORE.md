# 01. Ordo Core

Ordo Core — це мінімальний набір понять, без яких Ordo-програма не є керованою.

## Core objects

```text
INTENT.DEF
CONTRACT.DEF
CONTEXT.DEF
STATE.SCHEMA
ENTRY.DEF
NODE.DEF
PATH.DEF
STEP.RUN
GATE.DEF
ASSERTION.DEF
OUTPUT.DEF
HANDOFF.DEF
TRACE.LOG
EXECUTION_TRACE.DEF
```

## Core rule

Core не має містити доменну логіку. Він визначає форму керованого виконання, а доменні правила мають жити в Domain Packs або Libraries.

## v0.12 additions to Core

До Core додаються:

```text
gate.method
trust_class
trace_source
execution_mode
control_level
ASSERTION
on_unmatched_input
namespaced IDs
```

## Minimal valid Core program

```yaml
program:
  id: quick_summary
  ordo_version: "0.12"
  control_level: light
  execution_mode: freeform_only

intent:
  goal: "Summarize provided text."

contract:
  output_type: "bullet_summary"
  max_items: 3
```

У `light`-режимі gates можуть бути відсутні. У `standard` і `strict`-режимах потрібна формальніша структура.


## EXECUTION_TRACE core artifact

`EXECUTION_TRACE.DEF` defines the canonical append-only history of one `RUN`. See `33_EXECUTION_TRACE_MODEL.md` and `schemas/execution_trace_schema.yaml`. The legacy `TRACE.LOG` remains a diagnostic opcode and does not replace the full execution artifact.
