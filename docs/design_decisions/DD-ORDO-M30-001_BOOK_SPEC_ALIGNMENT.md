# DD-ORDO-M30-001 — Book and Specification Alignment for Process Rail

## Статус

Accepted

## Milestone

M30 — Book/spec alignment під Process Rail модель

## Context

Після M26–M29 Process Rail, Project Builder, Hybrid Execution і CLI helper commands були описані в окремих концептуальних і language documents. Проте книга, entry-point специфікації і compiled book artifacts ще могли виглядати як попередня CLI/runtime-first модель.

## Decision

M30 фіксує Process Rail як наскрізну модель у книзі та специфікації:

- книга має містити Process Rail у manifest і compiled all-in-one;
- вступ і базові пояснювальні розділи мають пояснювати Ordo як AI-first / Process-Rail-centered мову;
- language overview, Semantic JSON IR і execution model мають явно показувати AI-led authoring/execution;
- CLI описується як deterministic helper layer, а не як головний conversational runtime.

## Consequences

Після M30 майбутній GitHub cleanup має спиратися на нову модель як на canonical direction. Старі CLI-first формулювання потрібно вважати legacy wording і виправляти під час cleanup.
