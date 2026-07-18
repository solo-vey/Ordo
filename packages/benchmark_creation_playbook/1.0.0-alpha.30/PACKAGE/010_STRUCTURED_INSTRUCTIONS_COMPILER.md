# 010. Structured Instructions Compiler Contract

**Backlog:** BL-BENCH-010  
**Output variant:** `PV-STRUCTURED`

## Goal

Compile an immutable YAML playbook release into explicit human-readable instructions while preserving the executable semantics of the source graph. The output must not expose Ordo/YAML implementation details as requirements to the executor.

## Mapping contract

| YAML concept | Structured representation |
|---|---|
| node ID | stable instruction/step ID retained in provenance metadata |
| capture node | exact question, expected answer shape and completion rule |
| execution node | imperative action, allowed outputs and evidence requirement |
| validator node | deterministic checklist and pass/fail transition |
| state update | visible working-state consequence or internal driver state |
| transition | next-step rule, including fail/return path |
| terminal | explicit completion/block/exhaustion result |

## Compiler rules

- preserve all mandatory nodes and transitions;
- preserve question grouping only when semantics remain identical;
- never merge nodes that have different gates, evidence or correction behavior;
- never omit negative/failure paths;
- render exact allowed and forbidden outputs;
- retain stable source-node provenance without requiring the executor to understand YAML;
- separate executor instructions from Driver-private and evaluator-only content;
- do not improve, reinterpret or simplify the source contract during compilation.

## Required outputs

- ordered structured instruction corpus;
- source-node mapping table;
- state/terminal mapping table;
- compiler manifest with YAML source hash;
- parity validation report;
- checksum manifest.

## Parity gates

1. Node coverage = 100% for mandatory executable semantics.
2. Terminal mapping exact.
3. Correction and invalidation behavior exact.
4. Required output sets exact.
5. No evaluator leakage.
6. No newly invented domain rule.
7. Every compiled instruction traces to one or more source node IDs.

## Current implementation status

The compilation contract is defined; the executable transformer remains future implementation work.
