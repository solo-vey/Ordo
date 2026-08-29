# Ordo Tree Editor

Ordo Tree Editor is a local visual companion utility for editing an Ordo
playbook graph. It opens a browser interface on your own computer and does not
send YAML or process data to a hosted service.

## What the 0.2.0 alpha provides

- open an Ordo YAML file and display its nodes, executable gates, terminal
  outcomes, and transitions;
- distinguish interactive nodes, separate top-level gates, and external
  terminal/output targets in the graph;
- select, move, add, edit, and delete complete node and gate records without
  dropping their unknown top-level blocks;
- inspect each node as structured YAML fields or as one live full-YAML view;
- create a transition by hovering a source node, choosing **Add transition**,
  then clicking its target node;
- remove a node or gate route by hovering its line and choosing **Delete
  transition**;
- show both canonical `on_answer` and ARF-style `transitions` routes;
- show canonical list-based `transitions` entries (`to:`) and
  `navigation_contract.allowed_to` routes without duplicating edges;
- show gate `on_pass`/`on_fail` and canonical `pass_to`/`fail_to` routes with
  explicit edge labels;
- show top-level `terminals:` records as terminal targets;
- route visual arrows between the nearest card sides, including same-level,
  backward, and self-loop transitions;
- use question, gate, materialization, and terminal-node starters;
- inspect the reusable ARF tree-module catalog;
- run editor-local structural validation as a set of independent checks with PASS/WARN/ERROR findings;
- export ordinary YAML for further work in a chat or repository.

The graph layout is editor-local: moving nodes changes the canvas only and
does not add visual-layout metadata to the YAML source.

## Run locally

Requirements: Python 3.10+ and the normal Ordo CLI dependencies, including
PyYAML. No Docker, Node, cloud account, or API key is required.

From the repository root:

```bash
python3 utilities/ordo_tree_editor/editor_service.py
```

The editor opens at `http://127.0.0.1:8765`. On macOS, double-click
`start_ordo_tree_editor.command` after making it executable, or run it from a
terminal.

## Run with Docker Compose

The published image is a read-only, unauthenticated local service. From the
repository root:

```bash
docker compose -f docker-compose.tree-editor.yml pull
docker compose -f docker-compose.tree-editor.yml up -d
```

Open `http://127.0.0.1:8765`. Playbook files and session state are kept only
for the lifetime of the container; no persistent volume is required. The
standard image has no organization-specific model or GitLab defaults. For a
local custom provider, set `ORDO_MODEL_PROVIDER`, `ORDO_MODEL_BASE_URL`,
`ORDO_MODEL_NAME`, and (optionally) `ORDO_GITLAB_ROOT` in your shell or an
uncommitted env file before starting Compose.

To choose a different port or avoid opening a browser automatically:

```bash
python3 utilities/ordo_tree_editor/editor_service.py --port 9000 --no-browser
```

## Validation boundary

The editor performs editor-local structural validation only. It does not treat
that result as authoritative full Ordo playbook validation, and it does not
silently repair a graph, materialize a reusable module, invoke a model, or
change package runtime behavior. Use the normal Ordo validation/playbook tooling
for semantic validation, package compilation, full test execution, release
validation, and explicit tree-module instantiation.

## Distribution model

The source utility is shipped in the repository and can be packed into a
versioned ZIP release. Version `0.2.0-alpha.20.0.215-dev` is an experimental alpha test build: use it
to review and edit local copies, then validate the exported YAML through the
normal Ordo controls before relying on it. It requires an installed Python
runtime. A later desktop-distribution phase may bundle Python into a macOS
`.app` or Windows application; that packaging concern is intentionally
separate from the editor and validator contracts.


## 0.2.0-alpha.7

- Added a context menu on empty graph workspace with **Add node** and **Add gate**.
- Context-created nodes and gates are disconnected: no transitions are added automatically.
- New elements are placed at the graph coordinates where the context menu was opened.

## 0.2.0-alpha.4

- Hover over an editable node or gate to preview its complete record as YAML in a floating tooltip.

### 0.2.0-alpha.7

- Moved element creation from the left palette into the empty-workspace context menu.
- Added **Add library element** submenu with **Add document materialization** and **Add terminal block**.
- Context-created node, gate, document materialization, and terminal elements are disconnected by default and placed at the invoked graph coordinates.
- Removed the left node/library palette and expanded the graph workspace into that area.

### 0.2.0-alpha.7
- Hover YAML tooltip is interactive: move the pointer into it, scroll vertically, and select/copy text. Long YAML lines wrap to the tooltip width, so horizontal scrolling is not required.
- Added multi-selection with Ctrl/Cmd/Shift-click and drag-marquee selection on empty workspace.
- Right-clicking a selected element shows **Delete selected** instead of creation actions.
- Deleting a selection removes the selected editable nodes/gates and their known incoming/outgoing transition references.


### 0.2.0-alpha.8
- YAML loading is now the explicit empty-state starting action: **Upload YAML** is shown in the graph workspace only while no YAML is loaded.
- Removed **Open YAML** and **Download YAML** from the header after a document is loaded.
- Added **Download YAML** to the empty-workspace context menu.
- The header **Validate** action is hidden until a YAML document is loaded.

### 0.2.0-alpha.9
- Fixed the empty-state **Upload YAML** control: marquee-selection pointer capture no longer intercepts clicks on the empty state or interactive controls.

### 0.2.0-alpha.10
- Added top-level **Inspection** and **Validate** tabs to the right-side panel; node inspection/editing remains under Inspection and validation has its own workspace.
- Moved the **Validate** button and validation results out of the header/inspection flow into the Validate tab.
- Replaced the standalone canonical graph/lint calls with editor-local structural validation to avoid false positives caused by missing full-repository context.
- Structural validation now runs nine independent checks: YAML structure, graph element IDs, entry point, transition targets, reachability from entry, terminal reachability, dead-end branches, paths to terminal outcomes, and cycle discovery.
- Each validation check reports its own PASS/WARN/ERROR status and detailed findings; cycle discovery is informational rather than an automatic failure.
- Fixed context-menu behavior so **Delete selected** is not shown for an empty selection or when the menu is invoked on free workspace.
- Full Ordo semantic validation remains explicitly outside the editor-local validation boundary.

### 0.2.0-alpha.11
- Added a third right-side **Dialog** tab for a text-oriented pseudo-conversation view of a concrete graph path.
- Right-clicking a single node or gate can now preview the dialog from the graph entry to that element.
- Added a reachable-ending submenu that lists terminal/output destinations reachable from the current element and opens a dialog from the current element to the chosen ending.
- Dialog previews use one shortest structural path and show node questions, expected analyst response shape, gate conditions, selected transition/outcome labels, terminal outcomes, and declared dynamic-route hops.
- `declared_dynamic_routes` participate in dialog pathfinding as declared runtime possibilities without executing `$...` expressions.
- Node IDs inside dialog steps are clickable and center/focus the corresponding graph element.
- Validation findings that reference graph elements expose clickable IDs that center/focus the corresponding node or gate.
- Editor-local structural validation recognizes `declared_dynamic_routes`, preventing false DEAD_END / NO_TERMINAL_PATH findings for declared runtime routers.

### Interactive dialog branching (alpha.11 refresh)
- Dialog steps with more than one structural outgoing route now show inline branch-choice buttons.
- The currently previewed route is highlighted; selecting another route keeps the transcript above that step unchanged and rebuilds the transcript below it.
- The editor first tries to preserve the originally selected ending. If the chosen branch cannot reach that ending, the preview switches to the nearest reachable terminal/output and marks the fallback in the Dialog header.
- Declared dynamic routes appear as selectable runtime possibilities without evaluating `$...` expressions.


### 0.2.0-alpha.11.1 — experimental voice playback

- Adds optional browser-native speech playback (`speechSynthesis`) to Dialog playback.
- When Voice is enabled, the 1/2/3/5 second delay is disabled and progression waits for speech completion.
- Pause cancels current speech; Restart begins again from the first step.
- Branch choices still pause playback for user input; Auto-pass gates continues to prefer OnPass.
- Voice availability and quality depend on browser/operating-system speech synthesis support and installed voices.
- Voice language can be `Auto` (default), English (`en-US`), or Ukrainian (`uk-UA`). In Auto mode, each spoken step is classified independently by comparing Cyrillic/Ukrainian letters with Latin letters; Cyrillic-majority text uses `uk-UA`, otherwise `en-US`. The editor prefers an installed matching system voice and otherwise falls back to the browser's available voice.


### 0.2.0-alpha.11.2 — adaptive node height

Node and gate cards now expand vertically to fit their display label instead of clipping it to two lines. Edge anchors and automatic/Dialog layouts use measured card heights so connections stay attached to the resized cards.

### Replay tab (alpha.11.4)

The inspector now includes a read-only **Replay** tab. Upload an Ordo replay ZIP containing `run_trace.json` (optionally with `playbook/source/program.ordo.yaml`) or a standalone `run_trace.json`. The editor renders the actual traversed node path and recorded accepted decisions as a chat-like run history. If the package includes the playbook source, node questions and gate descriptions are taken from that exact source version. Replay packages do not currently contain the raw verbatim analyst/assistant chat, so the UI explicitly labels the view as a reconstruction from run evidence rather than a word-for-word transcript.

## Live Run mode (0.2.0-alpha.12)

The editor can execute one playbook element at a time with an OpenAI model while the local Python process remains the graph orchestrator. The model never receives authority to jump to an arbitrary destination: the Python runtime derives allowed routes from the current YAML element and accepts only a returned route key that maps to one of those routes.

Run mode is disabled by default. Enable it either with environment variables:

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-5"
./utilities/ordo_tree_editor/start_ordo_tree_editor.command
```

or by launching the Python service directly:

```bash
python3 utilities/ordo_tree_editor/editor_service.py \
  --openai-api-key "..." \
  --openai-model "gpt-5"
```

For security, prefer `OPENAI_API_KEY` so the key is not saved in shell history. The API key stays in the Python process and is never returned to the browser. If either the key or model is absent, the **Run** tab is disabled and all pre-existing editor, Dialog, Validate, and Replay functionality continues to work normally.

The first alpha.12 implementation sends the current element, allowed routes, current runtime state, recent live history, analyst input, and the loaded playbook source to the configured model. The model returns structured per-element work (`assistant_message`, `route_key`, `state_updates`, `rationale_short`); the local runtime validates the route and performs the transition.

## 0.2.0-alpha.12.1 — playbook ZIP execution package

Live Run now requires two independent readiness conditions: a complete playbook ZIP package must be loaded in the browser and the local Python editor must have OpenAI credentials/model configured. Loading a standalone YAML remains the editing/visualization path and intentionally does not enable Live Run even when API credentials are present.

The empty state offers both **Upload YAML** and **Upload playbook ZIP**. A ZIP upload is inspected by the local Python backend, which locates the executable Ordo YAML (preferring `program.ordo.yaml`), builds the graph from it, indexes package files, and retains bounded UTF-8 text resources for node execution. The Run panel reports package, execution YAML, model, API, and overall readiness. The API key remains server-side.

During a live step, the Python runtime still owns orchestration and allowed transitions. The model receives the current element, runtime state/history, playbook source, a package resource index, and bounded text resources resolved from file references in the current element. If the element does not explicitly reference supporting text files, the runtime supplies a bounded subset of package text resources as contextual fallback. Binary resources are indexed but are not sent as text.

For safety, package loading is fail-closed for invalid ZIPs, unsafe paths, excessive entry counts, excessive expanded size, or packages where no Ordo playbook YAML can be identified. The current implementation keeps one loaded execution package in the local editor process; starting a new package upload replaces that package context.


## Live Run startup

Prefer environment variables so the API key is not stored in shell history:

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-5.6-terra"
python3 utilities/ordo_tree_editor/editor_service.py
```

Or pass CLI arguments on consecutive continued lines (do not insert blank lines after a trailing `\`):

```bash
python3 utilities/ordo_tree_editor/editor_service.py \
  --openai-api-key "sk-..." \
  --openai-model "gpt-5.6-terra"
```

The Run tab is always visible. It shows package/API/model readiness and keeps **Start dialog** disabled until a complete playbook ZIP package and live-model configuration are both present.

## Live Run node execution (0.2.0-alpha.12.4)

Live Run now treats a node as executable work, not as a static prompt. On entry the model must first perform all work possible from the current runtime state and package resources. If analyst confirmation/correction/input is required, the model returns the concrete result/proposal and one specific question; the runtime waits on the same node. Nodes that require no human input may advance automatically. Gates remain automatic and never require analyst input.

## Alpha 12.5 — per-analyst OpenAI settings

The Run panel now owns model selection and, when no shared server key was supplied, personal API-key configuration. Supported OpenAI GPT-5.6 models are `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna`. A key supplied with `--openai-api-key` or `OPENAI_API_KEY` remains a shared fallback; otherwise each browser session can submit its own key to the local Python service. Personal keys are held only in Python process memory, scoped by a browser-session identifier, and are never returned to the browser after submission.


## 0.2.0-alpha.12.6 — scoped live context and compact token telemetry

- Token badges in Live Run are clickable and open a full **LLM step debug modal**.
- The modal has **Summary / Input / Output / Runtime** tabs with the actual scoped request payload, OpenAI usage counts, raw/parsed response, state updates, route decision, and downloadable debug JSON.
- Per-section token figures in Summary are explicitly marked as approximate; authoritative Input/Output/Total values come from the OpenAI API usage object.

Live execution no longer sends the complete playbook YAML or an arbitrary package-resource slice on every model call. The backend compiles a per-element execution packet containing the current element, allowed routes, bounded runtime state, a short recent-history window, small playbook identity metadata, and only package resources explicitly referenced by the current element. Package ZIP remains the source of truth, but it is now a resource repository rather than a wholesale prompt.

Token telemetry in the Run UI is intentionally compact: each model message and the Run summary show total tokens as one number; clicking a token badge opens the full LLM-step debug modal. Context section character sizes are included there for diagnostics and are not presented as authoritative token counts.


## Live LLM providers (alpha.12.7)
Run supports OpenAI (Responses API), Local MLX (`http://127.0.0.1:8080/v1`, `/models` + `/chat/completions`), and a Custom OpenAI-compatible provider. Local/custom models are discovered from `/models`; Local MLX never silently falls back to OpenAI.


### 0.2.0-alpha.12.7 context tightening
Package resources are now **explicit-reference-only** during Live Run. If the current element contains no path-like reference to a package resource, no package resource content is sent to the model. Automatic fuzzy filename matching was removed. LLM execution records also omit editor/graph bookkeeping such as `incoming_from` and `allowed_from`; package identifiers and source ZIP/YAML paths remain runtime/debug metadata and are not inserted into the model prompt.

### Optional compiled LLM execution plan
A playbook ZIP may include `compiled/llm_execution_plan.json`. When present, valid, and its `source_sha256` matches the canonical YAML file bytes, Live Run uses the compiled phase prompt plus its declared `required_state` / `required_resources` for LLM calls. YAML remains authoritative for graph routing and deterministic runtime behavior. If the compiled plan is absent, stale, invalid, or has no executable prompt for the current element/phase, Live Run falls back to the existing YAML-to-JSON execution path. Token/debug traces expose `execution_mechanism` as `compiled_llm_plan` or `yaml_fallback`.

### Compiled LLM element fail-safe validation

Even when `compiled/llm_execution_plan.json` is globally valid, Live Run validates each compiled element against the authoritative YAML/runtime semantics before using it. If the compiled element's `required_state` omits state dependencies that the YAML execution path would project, or if a compiled `route_key_allowlist` differs from the actual YAML/runtime route keys, that element is rejected and the call automatically uses `yaml_fallback`. The debug trace records `compiled_element_rejection_reasons` so stale or semantically incomplete compiled elements are visible without inspecting the raw request manually.

## alpha.20.0 experimental runtime contracts

alpha.20.0 introduces the non-breaking foundation for model-heavy orchestration:
`StatePatch` validation/atomic application and structured `GateFailure` objects.
Legacy playbooks still execute through their existing `state_updates`; every such update is
projected into an alpha.20 `StatePatch` in debug so migration can be observed before recovery
semantics change in alpha.20.1+. Semantic recovery/detours are intentionally not implemented
in this version.

## alpha.20.0.1 foundation hardening

The alpha.20 StatePatch contract is now on the real model-update commit path rather than debug-only. Writes are fail-closed against the compiled/YAML-declared allowlist and commit atomically. Legacy updates are marked `legacy_unknown`, object compatibility writes use `merge_deep`, `merge_row` is available for keyed table corrections, `base_revision` is mandatory, and deterministic gate failures expose structured alpha.20 `GateFailure` diagnostics. Persistent run revisions are deliberately not claimed yet; the current bridge enforces revision 0 until the run-journal milestone. Recovery routing behavior is otherwise unchanged.


## alpha.20.0.2 V7 semantic-plan compatibility foundation

- Adds first-class loading of `compiled/runtime_semantic_plan.json` (`ordo.runtime_semantic_plan` 1.x-alpha20) alongside legacy V6 plans.
- Adds runtime semantic Context/Instruction Assembler: semantic task content is separated from graph mechanics, broad canonical state is supplied, resources/output contract/patch template are explicit, and V7 never silently drops to YAML LLM execution.
- Uses shared `ordo_yaml_semantics` rules for recursive write extraction so branch-specific `on_answer.*.update_state` paths are not lost.
- Compiled write allowlists are authoritative; YAML cannot widen an active compiled contract.
- StatePatch commit canonicalizes mixed dotted/nested state and `merge`/`merge_deep` can initialize schema-default `null` objects.
- Runtime-semantic model output gets up to 3 structured repair attempts on parse/StatePatch validation failure.
- Enter/resume UI errors restore analyst input availability instead of freezing the run.
- V7 semantic execution remains intentionally separate from alpha.20.1 recovery behavior.


## alpha.20.0.6 — V7.7 execution compatibility
This release pairs with Runtime Semantic Compiler V7.7 / format `1.4-alpha20`. The shared YAML semantics module now exposes phase-aware model execution and an explicit `runtime_executor`. Semantic history is always bounded and included, state truncation is explicit and blocks semantic gate PASS, and legacy `state_updates` are converted into validated StatePatch operations instead of being silently dropped.

## alpha.20.0.6 — regression hardening
Paired with Runtime Semantic Compiler V7.7. Runtime StatePatch validation now enforces compiler-provided `value_schema_by_path` for collection/table writes. Incomplete semantic gate context becomes an immediate structured GateFailure rather than three identical retries. Gate PASS and FAIL are both analyst-visible, repeated live-path visits retain step numbers, and semantic revisits receive a formal `revisit_context` preserving the previous answer and changed dependency paths.


## alpha.20.0.11 — Conversational Recovery
Validation-recovery nodes now support free-form analyst/model dialogue while remaining on the recovery node. Auto-answers pause on entry. Recovery chat may commit fail-closed StatePatch operations only under gate-declared affected_state roots, can re-run the failed gate on request, or enter a grounded repair target in manual mode.

## alpha.20.0.12 — Gate UX & Coverage Recognition

- Runtime technical IDs preserve underscores in transcript rendering.
- Assistant/model messages are expanded by default; only long analyst messages collapse automatically.
- Human-decision gates provide prepared actions plus an inline `Other / clarification` field that is carried into the repair route as analyst correction context.
- Deterministic test-coverage detection recognizes Ukrainian negative-case wording (`негатив*`, `відсутн*`) as evidence for the `negative` requirement.


## Replay to checkpoint (alpha.20.0.13)

The Run tab can load a debug-run JSON or reproduction ZIP and replay both recorded analyst responses and accepted model outputs until a recorded checkpoint. Model outputs are passed through the current runtime validator before StatePatch commit. At the checkpoint the replay mode turns off and execution continues live.


## alpha.20.0.16 — Release 1 Runtime Correctness

Adds V7 projection defaults, typed context-status classification, bounded per-check model-gate accounting, operation-aware collection validation, import-only legacy collection normalization, touched-path collection invariants, provider/API-style strict-schema compatibility, typed contract-unsatisfiable stops, technical recovery UX, and the thin Release-1 run verifier.


## alpha.20.0.19 — Operation Variant Enforcement

StatePatch validation now enforces compiler-declared `operation_variants` in addition to write allowlists and value schemas. Added as a RED→GREEN regression from the Preflight Harness v1.0 mutation matrix.

## Startup parameters and Upload Playbook home

The Editor starts on the **Upload Playbook** tab. Load a local YAML/ZIP package or use the optional public GitLab catalog. After a successful load, the Editor opens **Execute Playbook** automatically. Returning to Upload Playbook replaces the current playbook with the newly selected package.

Optional startup configuration can be supplied as command-line parameters or environment variables:

```text
--model-provider / ORDO_MODEL_PROVIDER
--model-name / ORDO_MODEL_NAME
--model-base-url / ORDO_MODEL_BASE_URL
--model-api-key / ORDO_MODEL_API_KEY
--gitlab-root / ORDO_GITLAB_ROOT
```

For a local installation, edit `ordo_editor_defaults.env`. These values are runtime parameters; they are not embedded into Editor logic.

On macOS, executable permission is not required when the launcher is invoked through the shell:

```sh
cd "/Users/test/Downloads/ORDO_TREE_EDITOR/utilities/ordo_tree_editor" && sh ./start_ordo_tree_editor.command
```

## Language-first package authority (alpha.20.0.156-dev)

Canonical Ordo is the semantic source of truth. Editor discovery and adapter behavior must not create hidden language rules from filenames, UI conventions, transport details, or runtime heuristics.

For any Editor behavior that can reject or reinterpret a package:

1. identify the supporting canonical Ordo rule;
2. if no language rule exists, classify the behavior as Editor-adapter behavior;
3. ensure adapter behavior cannot invalidate an otherwise valid Ordo package;
4. if Editor behavior contradicts canonical Ordo, fix Editor rather than requiring a playbook workaround;
5. never globally reserve a basename across arbitrary ZIP resources unless canonical Ordo explicitly defines such a namespace.

Runtime Semantic Plan authority is therefore resolved only from the canonical package-relative location `compiled/runtime_semantic_plan.json`, or the equivalent path beneath the ZIP's single enclosing package-root directory. Nested tests, fixtures, examples, archived samples, developer evidence, and synthetic packages may contain same-named files; those are ordinary resources and cannot become the active runtime plan merely because of their basename or a nested `compiled/` directory. If no authoritative precompiled plan exists, Editor follows the source-first integrated compilation path. If an authoritative plan exists but is invalid, stale, or unsupported, loading remains fail-closed.

## Declared outputs in Show Tree (alpha.20.0.157-dev)

Declared `outputs` are external result declarations, not execution branches merely because they are named `OUT_*`. Show Tree therefore derives a view-only producer association from exact structured artifact/output references when a unique materializer can be proven. The association is rendered as a dashed `declares output` relation and never becomes a runtime transition or gets written back to Ordo source.

Producer resolution does not use description/prompt text or similarity between node/output IDs. Unresolved and ambiguous cases remain visible through the Editor diagnostic `DECLARED_OUTPUT_PRODUCER_TRACEABILITY` rather than being guessed by layout heuristics.

## Runtime executor authority and deterministic route closure (alpha.20.0.161-dev)

When an authoritative Runtime Semantic Plan exists, its `execution_traits.runtime_executor` owns dispatch. Legacy source-action compatibility shortcuts may not reclassify or intercept a semantic executor selected by the compiled plan. In particular, `DOCUMENT.GENERATE` presentation/action metadata cannot override an authoritative `package_tool` executor.

Successful non-terminal deterministic package-tool execution must close onto a runtime-selectable declared route. Runtime records `DETERMINISTIC_EXECUTION_ROUTE_CLOSURE`; unknown machine route keys, ambiguous route selection, or unresolved graph targets fail closed with a structured diagnostic instead of being deferred to a UI-level `missing_route`. A tool may omit `route_key` only when the canonical source still determines one unambiguous continuation (`next`, a sole route, or explicit `on_answer.next`).

## Formal route authority and semantic-recovery aliases (alpha.20.0.162-dev)

Runtime control-flow is projected only from formal route-bearing Ordo structures. Arbitrary strings in tool arguments, resources, templates, bindings or other payload fields never become execution routes merely because they match a node/terminal identifier. This is an Editor/compiler conformance boundary: data is not control-flow without a declared routing construct.

Safe semantic recovery preserves the common compatibility alias `next` by normalizing it to runtime `next_id` before validation/application. The runtime does not silently commit a recovery state patch and then discard its declared continuation.


## Generated-playbook profile adapter (alpha.20.0.163-dev)

Canonical Ordo remains unchanged. A supported Vibe/generated-playbook authoring profile may declare editor/runtime adapter metadata such as `execution_contract.runtime_executor: package_tool` together with `tool_ref` and optional `args`. This profile metadata is not treated as canonical language syntax by the runtime.

The integrated compiler owns the adaptation boundary. For supported profile declarations it emits explicit Runtime Semantic Plan `execution_traits` plus an `execution_adapter` payload. Runtime dispatch then consumes only that compiled projection. Materialization metadata such as `template`, `bindings` and `output` cannot reclassify an adapted `package_tool` node as `document_generate`.

Current v1 profile adapter support is intentionally narrow and fail-closed:

- `execution_contract.runtime_executor: package_tool`;
- deterministic node ownership;
- one safe package-relative Python `tool_ref`;
- flat scalar `args`;
- tool result fields `route_key`, `state_updates`, and `status`;
- machine `state_updates` restricted to Runtime Semantic Plan declared writes;
- declared artifact/output files copied from the isolated package-tool workspace into the run workspace.

Unsupported or contradictory profile declarations produce compiler diagnostics instead of silently becoming new Ordo semantics.

### Deterministic artifact/archive validation authority (alpha.20.0.164-dev)

`method: mechanical` + `trust_class: deterministic` is never reclassified into LLM semantic recovery. The runtime either executes a supported deterministic rule/profile adapter or halts with a structured deterministic capability/contract diagnostic.

For the supported generated-playbook/Vibe profile, artifact/archive validation may be compiled from formal producer artifact metadata and `verification/ARTIFACT_MATERIALIZATION_REGISTRY.json`. Runtime does not parse prose such as “validator reports PASS” or “archive membership/hash validation is PASS” to invent checks. Archive member/hash validation is credited only when the profile structurally declares the required evidence; otherwise `PROFILE_ARTIFACT_VALIDATION_CONTRACT_INCOMPLETE` is surfaced.

## Deterministic gate state-contract diagnostics (alpha.20.0.165)

Editor/compiler derives `GATE_PRODUCER_CONSUMER_STATIC_ALIGNMENT` evidence for deterministic gates. A gate's explicit `state.*` condition references are checked against upstream state writers. The diagnostics distinguish exact producers from ancestor-object writes and from model/tool write allowlists that do not guarantee an exact field will be emitted on every valid execution.

This does **not** create aliases or infer semantic equivalence between similarly named fields. A compatibility alias is executable semantics and must come from an explicit canonical/profile derivation contract, not Editor heuristics.


## Gate guarantee and revisit-state safety (alpha.20.0.166-dev)

Deterministic gate inputs are not considered safe merely because an upstream model is allowed to write the exact leaf. Under `graph_contract.dependency_strictness: strict`, an exact producer must be statically guaranteed; otherwise compilation reports `GATE_INPUT_PRODUCER_NOT_GUARANTEED`.

Required-state survivability is checked across reachable revisits. A writer on a `consumer -> writer -> consumer` cycle may not remove a required path or destructively overwrite one of its ancestors with `set`, `replace`, shallow `merge`, or unsafe `merge_deep`. The compiler emits `REQUIRED_PATH_ANCESTOR_DESTRUCTIVE_OVERWRITE` unless the operation value schema proves the required descendant is preserved.

## Fast verification entrypoint

For normal development use `python verify_editor.py fast`. Use `affected --changed <path>` for subsystem regressions and reserve `python verify_editor.py full` for the final exhaustive pre-release pass. See `PERFORMANCE_VERIFICATION_PIPELINE.md`.

## REST API reference

While the Editor server is running, open `/api-docs/` for the grouped local REST API reference. Machine-readable OpenAPI 3.1 files are available at `/api-docs/openapi.yaml`, `/api-docs/openapi.json`, and the Swagger-compatible alias `/api-docs/swagger.yaml`. The same links are available from **Help → REST API**.
