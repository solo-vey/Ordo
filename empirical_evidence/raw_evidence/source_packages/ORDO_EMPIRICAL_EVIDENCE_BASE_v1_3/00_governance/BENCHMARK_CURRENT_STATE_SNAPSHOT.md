# Benchmark Current State Snapshot

Date: 2026-07-15

## Scientific objective

Identify task classes in which Ordo is measurably better than an instruction-only model under fair, comparable conditions.

## Current task-class status

- TC01 Complex Multi-Step Process: one completed five-scenario comparative case.
- TC02 Interrelated Artifact Set: candidate example defined; comparative execution pending.
- TC03 Recurring Regulated Task with High Omission Cost: candidate example defined; comparative execution pending.

## TC01 / EX01 result

Across S01–S05, Ordo scores 98.8 and instruction-only scores 86.8, a mean difference of 12.0 points. The strongest observed differences are branch/loop routing and restore/backtrack behavior.

## Methodological constraints

- Do not expose future scenario events to the executor.
- Give instruction-only execution the full process rules but not future test values.
- Preserve raw evidence unchanged.
- Record both successes and failures.
- Present composite scoring before evidence admission.
