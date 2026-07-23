# History Event Guided Intake Ordo Package

The first substantial practical Ordo package for guided intake of a new historical-event contract.

## Purpose

The package guides an analyst through guided intake:

1. business goal of the event;
2. path selection;
3. alias;
4. Ukrainian and English display names;
5. source field;
6. value semantics;
7. QA scope;
8. explicit approval before final package output.

## Ordo v0.12

The package uses:

- `gate.method`;
- `trust_class`;
- `execution_mode: chat_internal`;
- `ASSERTION`;
- `CLARIFY.REQUEST`;
- `FREEFORM.maturity`;
- release validation through `ordo validate-release`.

## Commands

```bash
ordo lint packages/history_event_guided_intake
ordo compile packages/history_event_guided_intake
ordo test packages/history_event_guided_intake
ordo coverage packages/history_event_guided_intake
ordo run packages/history_event_guided_intake --answers packages/history_event_guided_intake/run_inputs/answers_success.yaml
ordo intake packages/history_event_guided_intake --answers packages/history_event_guided_intake/run_inputs/intake_success.yaml --non-interactive
ordo validate-release packages/history_event_guided_intake
```

## MVP Boundaries

This package does not yet generate a complete final History Event analytical package. It validates the first controlled part of the process: contract intake and validation.
