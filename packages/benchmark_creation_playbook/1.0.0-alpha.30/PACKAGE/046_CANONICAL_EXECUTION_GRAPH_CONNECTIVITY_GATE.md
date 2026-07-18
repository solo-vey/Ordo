# BL-BENCH-046 — Canonical Execution Graph Connectivity and Reachability Gate

**Status:** OPEN  
**Priority:** High  
**Type:** Architecture / Validation / Release gate

## Problem

The current playbook contains 72 declared execution nodes, but they are not assembled into one canonical connected execution graph. Several epic subgraphs terminate locally, newer runtime nodes are detached, and some nodes are orphaned, unreachable from the canonical entry point, or have no valid outgoing route despite not being terminal.

This allows documentation, backlog and source nodes to grow while the executable graph silently diverges from them. A graph renderer may therefore show only a small reachable fragment even though many nodes exist in the source.

## Required result

Assemble all route-authorized playbook nodes into one explicit canonical execution graph and add a fail-closed connectivity gate that blocks release when structural graph defects exist.

## Mandatory scope

1. Define one canonical entry node and explicit supported terminal nodes.
2. Connect epic boundaries with explicit transitions instead of ending each epic in an isolated local terminal.
3. Integrate all currently detached runtime and governance nodes, including BL-BENCH-041 through BL-BENCH-045.
4. Classify every node as reachable execution node, explicitly optional branch, reusable subgraph entry, or terminal.
5. Reject undeclared disconnected components.
6. Reject orphan nodes, dangling transition targets, unreachable nodes, accidental dead ends and nonterminal nodes without outgoing transitions.
7. Detect cycles and require every intentional cycle to be explicitly declared and bounded.
8. Produce machine-readable graph evidence: node count, edge count, entry points, terminals, components, unreachable nodes, dead ends, cycles and branch coverage.
9. Generate full SVG/text graph only after connectivity validation passes.
10. Add the connectivity result to the mandatory release gate.

## Fail-closed gate

Release MUST be blocked unless all of the following are true:

- exactly one canonical entry point exists;
- every required node is reachable from it;
- every transition target exists;
- every reachable path ends in an allowed terminal or a declared bounded loop;
- no orphan or accidental dead-end node exists;
- all optional branches are explicitly classified;
- graph evidence and rendered graph are generated from the same source revision.

On failure, the playbook must return `BLOCKED_GRAPH_CONNECTIVITY` with exact node IDs and defect classes. It must not publish or hand off the playbook as execution-ready.

## Acceptance criteria

- 72/72 current nodes are classified and accounted for.
- All mandatory nodes are reachable from the canonical entry.
- Zero dangling targets.
- Zero undeclared orphan nodes.
- Zero accidental dead ends.
- Every gate has explicit pass/fail routing.
- Every nonterminal node has at least one valid outgoing transition.
- Intentional loops are declared with exit and iteration bound.
- A machine-readable connectivity report is produced.
- A complete SVG graph is generated from the validated graph.
- Negative tests prove release rejection for orphan, unreachable, dangling-target and accidental-dead-end cases.

## Expected implementation artifacts

- `tools/validate_execution_graph_connectivity.py`
- `EXECUTION_GRAPH_POLICY.yaml`
- `schemas/execution_graph_report.schema.json`
- `reports/EXECUTION_GRAPH_CONNECTIVITY_REPORT.json`
- `reports/EXECUTION_GRAPH_CONNECTIVITY_ACCEPTANCE_TESTS.json`
- updated `source/program.ordo.yaml`
- regenerated full SVG graph
- release-gate integration evidence

## Definition of Done

The task is DONE only when the graph is materially connected, the validator and negative tests pass, the release gate consumes the report, and the generated SVG proves the same validated graph revision. Merely documenting missing links is insufficient.


## Implementation closure — alpha.11

- All 72 route-authorized nodes are reachable from `N001_FOCUSED_SCOPE`.
- All 16 gates are reachable and have explicit routes.
- Epic completion gates now continue to the next epic instead of terminating the global route.
- BL-BENCH-041–045 runtime nodes are connected into the same canonical route.
- `tools/validate_execution_graph_connectivity.py` fails closed on unreachable/orphan/dangling/dead-end topology.
- Connectivity report and SVG are generated from the same YAML revision and bound by SHA-256.
- Acceptance tests: 5/5 PASS.
