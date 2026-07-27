# Recommendations for Building Playbooks on ARF

Document version: 0.6
Status: complete working guidance

These recommendations describe a disciplined authoring route for creating a
new playbook on the Applied Runtime Framework (ARF). They are authoring
guidance, not a replacement for deterministic CLI and release validation.

## 1. Start with a domain model

Give the model a short description of the domain, or provide existing
instructions, documentation, and examples. Ask it to create a separate file
describing the main entities, relationships, important events, terms, and
process boundaries.

Use this file as the shared basis for all later templates, parameters, and
nodes. If the model finds contradictions or gaps, record them separately and
ask only questions that affect playbook construction.

## 2. Define the resulting artifacts

Describe which files the playbook must create and save the list separately.
For each artifact record its name, format, requiredness, and creation
condition.

This list becomes the basis for templates, materialization nodes, and final
package validation. Do not add artifacts that are not created, do not affect a
route, or are not checked at the end.

## 3. Create templates for the resulting artifacts

Ask the model to create and save a separate template for each resulting
artifact. A template may be created from a description, from scratch, or from
an existing completed document.

When a completed document is supplied, ask the model to distinguish permanent
structure from values that must become parameters or placeholders. Review the
result together and refine it until it can be materialized repeatedly.

Keep each template separate from examples of a particular run.

## 4. Define materialization parameters for each template

Ask the model to analyze each template and create a nearby file listing the
parameters needed to materialize it. For each parameter record its name, type,
meaning, and possible source: input artifact, analyst answer, or derived value.

The model must also identify fields whose source is not yet known and record
them as gaps. Do this before building the tree; otherwise materialization may
invent missing values or stop only at a late stage.

## 5. Create one playbook parameter registry

After analyzing all templates, ask the model to merge their parameters into a
single registry. A value used by several documents must be one canonical
parameter, not several independent copies.

Record the parameter name, type, source, collection method, and artifacts that
use it. Show duplicate names, naming conflicts, and parameters without a
source separately.

Keep this registry as a working file rather than only in chat context. It is
the basis for primary/derived classification, dependency mapping, and node
creation.

## 6. Separate primary and derived parameters

Classify primary parameters as facts obtained from input artifacts or the
analyst, and derived parameters as values formed from confirmed data.

For every derived parameter record the primary parameters it depends on. For
example, test scenarios may be formed only after trigger rules, normalization,
and skip rules are confirmed.

The tree should collect facts and decisions first, then create tests, prompts,
and other derived outputs. Keep this classification in the parameter registry.

## 7. Identify input artifacts and automatic extraction

List the materials available at the start: documents, archives, modules,
structured examples, or links. Ask the model to create an input-artifact
registry and state which parameters can be extracted from each artifact
reliably.

Distinguish values that can be extracted from values merely inferred from
context. Critical assumptions must not be recorded automatically as confirmed
parameters.

This prevents questions about data already present in input files without
turning automatic analysis into uncontrolled speculation.

## 8. Identify data that must come from the analyst

Compare the parameter registry with reliably extractable input data and create
a list of parameters that still lack a confirmed source.

Include only questions required to build derived parameters, pass a gate, or
materialize a required artifact. For each question provide the known context
and, where possible, a proposed answer for confirmation or correction.

## 9. Build parameter dependencies

Create and save a dependency map showing which values are immediately
available, which need confirmation, and which are formed only after other
decisions.

Use it to order nodes. If a document uses a parameter, all of its dependencies
must be closed before the materialization node.

Find cyclic dependencies, parameters without sources, and values created too
late before building the YAML tree.

## 10. Create a decision-tree prototype

Based on the registry and dependency map, create a first tree prototype with
the main nodes, their purpose, input and output parameters, and transitions.

Do not begin with detailed wording for every question. First verify that the
tree collects all primary parameters, creates all derived values, and reaches
materialization nodes for every required artifact.

Keep the prototype in YAML or another structured file. Every parameter must
have a source node and every required document must have a reachable
materialization node.

## 11. Add gates before document materialization

For each resulting artifact create a gate that checks readiness of all
template parameters. State which values are required, which may be absent, and
which conflicts block creation.

The gate should return to the node that can repair the specific gap, rather
than merely reporting that the document is not ready. Keep gates synchronized
with template parameter specifications.

## 12. Materialize documents from templates

After a gate passes, materialize the document only from confirmed parameters.
Do not introduce facts that are absent from the registry during generation.

Record the template version, playbook version, and parameters used for each
materialized file. Keep drafts separate from confirmed versions and record the
state of every artifact explicitly.

## 13. Validate materialized documents with the model and scripts

For each important document create two related checks: a semantic review for
completeness, clarity, contradictions, and consistency with confirmed
decisions; and a precise Python or CLI check for required sections,
placeholders, identifiers, duplicates, and allowed values.

Create executable validators and negative tests that prove incorrect
documents are rejected. Do not leave the validation as YAML prose only.

## 14. Validate the complete package end to end

Separate documents may pass individually and still contradict one another.
Create a package-level validator that compares shared canonical parameters
across resulting artifacts.

Check canonical values, identifier formats, relative paths, package contents,
and checksums according to each document's role. This validation is blocking
before final archive creation.

## 15. Detail the main branch in small groups

Once the prototype is sound, detail the main branch in small groups of nodes.
After each group show the analyst-facing description, exact question, possible
answer, recorded parameters, and next node.

Generate this view from the current YAML through ARF. Do not create an
independent dialogue example disconnected from the tree.

## 16. Handle alternate routes and missing inputs

Walk every node where an input artifact, confirmation, or check may be
unavailable. Classify each case as an error, an allowed omission, or an
inapplicable route.

An allowed omission must not loop forever or terminate early. Record its
status and reason, then return to the main route after the skipped block. Check
all terminal nodes separately and keep only genuine completions.

## 17. Use ARF for versions, checkpoints, and state persistence

From the beginning, ask ARF to keep execution state, create checkpoints before
changes, and preserve versions of YAML, templates, validators, and registries.

The active node, completed steps, parameter values, gate results, artifacts,
allowed omissions, and blockers must exist in structured runtime files, not
only in chat history.

Before packaging, verify that canonical and versioned YAML agree and that
reports and checksums match actual files.

## 18. Test the playbook on a realistic example

Run the complete process on real or representative input. Check not only that
the route reaches the end, but also that questions are understandable,
parameters are stored correctly, and resulting documents are usable.

Keep the route, analyst answers, artifacts, and validator reports separately so
the run can be reproduced. Test the main route, allowed omissions, and several
negative scenarios.

## 19. Record antipatterns and improvement rules

After testing, maintain a separate generalized record of problems. For each
problem note how it appeared, why it occurred, and what change removed it.

Useful examples include mixed responsibilities, missing transitions,
inconsistent parameters, formal gates without executable checks, and branches
that terminate too early. Keep generalized rules rather than case-specific
data.

## 20. Define readiness criteria

Create a final checklist for deciding whether a playbook is ready. It should
verify primary parameters, derived values, required artifacts, local and
package-level validation, supported routes, and checkpoint resume behavior.

Turn these criteria into an automated pre-release check that runs before a
versioned package is created.

## Relationship to ARF and the CLI

This document describes the recommended authoring discipline. The ARF Kit is
the chat-first route for designing and reviewing a playbook; the CLI provides
deterministic validation, reproducibility, and release enforcement. A
conversational review must not be presented as equivalent to a release gate.
