# ARF Playbook Factory

This is the standalone ARF package for creating a new Ordo playbook in a language-model chat.

## Start in chat

1. Upload the complete ZIP without unpacking or changing it.
2. Ask the model to read `guides/START_PROMPT.md`.
3. Follow the guided intake and create your new playbook in `workspace/`.
4. Use the included validation and improvement instructions before accepting the result.

## Package boundaries

The archive contains the active Applied Project Factory source, a freshly compiled runtime representation, the embedded runtime CLI, local integration contracts, output templates, tests, and chat-facing guides.

It also contains `language/`, the package-local anti-pattern language contour:
the active registries, schemas, runtime, integration adapter, fixtures, and
test dependencies. The included anti-pattern integration suite therefore runs
from the extracted Kit without a separate Ordo repository checkout.

The archive intentionally excludes repository history, previous validation reports, release evidence, generated examples, and unrelated developer material. The package is a standalone ARF product artifact, not a repository snapshot.

## Included capabilities

The 0.4.9 kit contains these optional capabilities in addition to the core ARF
authoring and runtime contract:

- `source/tree_module_library/` — build-time reusable document-materialization
  and package-handoff tree templates, with provenance-preserving CLI support.

- `utilities/ordo_pathwalk/` — graph path exploration, terminal-path
  enumeration, clean/noise testcase generation, review cards, and benchmark
  helpers.
- `utilities/ordo_visual_graph_generator/` — Mermaid/SVG/PNG graph rendering,
  subtree and path views, and annotation overlays.
- `utilities/playbook_lifecycle/` — checkpoint management, upgrade-impact
  review, and verified rollback helpers.
- `utilities/playbook_regression_harness/` — the versioned regression-harness
  companion utility.
- `utilities/ordo_tree_editor/` — a local browser-based Ordo YAML graph editor
  with canonical Python graph and lint validation.
- `release_tools/` — the ARF Kit builder, project release-archive builder,
  release-integrity verifier, and English-only policy validator.

These utilities are optional advanced tooling. They do not replace the
chat-first route and are not required to create a first playbook.

## Guided legacy migration artifacts

Mode 5 (legacy-instruction migration) includes a complete intermediate-artifact
template set under `migration/`. The route records scope, domain model, output
artifacts, templates, parameters, dependencies, traceability, tree design,
materialization gates, validation gates, replay, improvements, and readiness.
Copy these templates into `workspace/migration/` and use the lifecycle
`collect -> save -> review -> gate -> checkpoint -> next`; the route must not
advance while a blocking gate or unresolved required field remains.

## Not included

The kit does not include the full Ordo repository, Git history, CI workflows,
repository evidence archives, or unrelated maintenance/audit tools. The
release tools are included for inspection and reproducible-build guidance;
their repository-level commands may require a full Ordo checkout.

## Authoring and runtime rules

- Use `guides/START_HERE.md` and `guides/START_PROMPT.md` as the chat-facing entry route.
- Use `START_HERE_RUNTIME_MODE.md` for the runtime protocol.
- Do not edit files under `compiled/` directly.
- Put all new user work under `workspace/`.
- The embedded CLI is an optional deterministic verification route; it is not required for the initial chat-first creation route.
- For every decision-bearing node, preserve the exact rendered interaction and analyst response, then write a bounded decision summary as described in `guides/DECISION_DEBUG_TRACE.md`.
- For every document materialization, define the required document fields and validate their state declarations, producers, path coverage, and collection requiredness as described in `guides/DOCUMENT_FIELD_PROVENANCE.md`.
- For every active graph edge, keep the source transition and target `allowed_from` declaration symmetric; the package compiler rejects asymmetric, dangling, duplicate, unreachable, and illegal terminal transitions as described in `guides/GRAPH_TRANSITION_CONTRACT.md`.
- Reuse the optional document-materialization and package-handoff modules through the build-time library in `source/tree_module_library/`; inspect `guides/TREE_MODULE_LIBRARY.md` before generating an instance. Factory recommendation is optional and requires an explicit preview and confirmation.

## Build provenance

The canonical builder is `tools/build_arf_playbook_kit.py` in the Ordo repository. The source package is `packages/ordo_applied_project_factory/`. The build specification remains source-only and is not shipped in the user ZIP.
