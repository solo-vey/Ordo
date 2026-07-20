# Ordo Glossary

This glossary provides short navigation-oriented definitions. Normative schemas, registries, runtime documents, and package contracts remain authoritative.

## APF

**Applied Process Factory.** The framework layer for assembling and improving Ordo processes and playbooks from reusable modules and contracts. See [`integrations/apf/`](../integrations/apf).

## Canonical packaged baseline

A release candidate produced by the sanctioned release builder and identified by release manifests, checksums, and gate evidence. It is distinct from later commits on `main`.

## Checkpoint

A recorded execution boundary used to preserve state, validate continuation, or support replay and recovery. See [runtime checkpoints](../language/RUNTIME_CHECKPOINTS.md).

## Driver

The runtime component or adapter that performs an execution step under an Ordo contract. Driver behavior is constrained by the process, node, gate, and evidence rules rather than being the source of those rules.

## Evidence

A structured record used to support a validation, benchmark, execution, or release claim. Evidence may include normalized records, immutable raw artifacts, manifests, receipts, and reports.

## Execution graph

The connected process structure that determines which nodes, gates, branches, loops, and terminal outcomes can be reached.

## Gate

A decision or validation boundary that allows, blocks, routes, or records process progression according to explicit conditions.

## Node

A unit in an Ordo process graph with a defined role, inputs, outputs, transitions, and runtime contract.

## Ordo

The project containing the Ordo process language, runtime framework, APF integration layer, reference packages, CLI, tests, documentation, benchmarks, and evidence.

## Ordo language

The schemas, registries, semantics, and compatibility rules used to represent structured AI-assisted processes.

## Package

A versioned directory that groups an Ordo process or playbook with its manifests, contracts, fixtures, tests, reports, and supporting documentation.

## Playbook

A reusable process package that applies Ordo contracts to a defined task or operational domain.

## Process

A structured sequence or graph of work represented through explicit nodes, transitions, gates, state, and completion conditions.

## Receipt

A structured execution or validation record that captures what occurred, under which inputs and rules, and with which outcome.

## Release candidate

A packaged build that is undergoing or has passed defined release validation but is not automatically a final stable release.

## Replay

Re-execution or reconstruction of a prior run using recorded inputs, state, decisions, and evidence under the applicable runtime contract.

## Runtime framework

The execution, validation, state, trace, testing, and improvement machinery that applies Ordo language contracts.

## Terminal

A declared process outcome or end state. Terminals make completion, failure, escalation, or other final routes explicit.

## Trace

Structured information that records execution paths, decisions, state changes, knowledge use, or gate outcomes for inspection and evidence.
