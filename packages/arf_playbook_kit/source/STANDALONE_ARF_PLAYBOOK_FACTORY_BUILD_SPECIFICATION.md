# Specification — Build a Standalone ARF Playbook Factory Package

## 1. Role and objective

Use the complete source contour at `packages/ordo_applied_project_factory/` to build a minimal but fully autonomous ARF runtime package. A new chat must be able to use that package to create a new Ordo playbook without access to the rest of the repository.

This is not:

- a copy of the entire repository;
- a developer bundle;
- a historical archive;
- a simplified starter that omits required runtime behavior.

The target is one self-contained artifact:

`Self-contained ARF Playbook Factory Runtime Package for chat-based creation of new Ordo playbooks.`

The package must enable the full lifecycle:

`intake → design → validation → dry run → improvement → final package`

## 2. Required result

Produce one ZIP archive that a user can upload to a new language-model chat. The model must be able to read the ARF package, follow its runtime instructions, create a playbook, validate it, perform a dry run, improve it, and return a final deliverable without downloading or reading any additional repository content.

The package must include:

- the complete active process;
- runtime instructions and a startup prompt;
- a compiled representation of the process;
- controlled modular source;
- the smallest embedded runtime CLI required by the process;
- output contracts and templates;
- validation and test contracts;
- the minimal required antipattern subset;
- the visual graph utility when the process requires it;
- a manifest, checksums, and integrity data;
- an empty, writeable workspace for the user's new playbook.

## 3. Source of truth and scope selection

Treat `packages/ordo_applied_project_factory/` as the source of truth. Before assembling the archive, inventory its runtime entries, source modules, manifests, configuration, external dependencies, templates, laws, tests, question registry, and utilities.

Separate active runtime material from development-only and historical material. Include only the current, canonical implementation and the dependency closure required for autonomous execution.

Do not select files by filename alone. Establish why each included file is required, and why each omitted file is safe to exclude.

## 4. Canonical runtime core

### 4.1 Runtime entry files

The archive must contain canonical runtime entries, including:

- `START_PROMPT_RUNTIME_MODE.md`;
- `START_HERE_RUNTIME_MODE.md`;
- `ordo.yml`;
- `ordo.runtime.json`.

If package-facing aliases are required, include `START_PROMPT.md` and `START_HERE.md` and make them point unambiguously to the canonical runtime entry files.

`START_HERE_RUNTIME_MODE.md` must explain:

1. the required reading order;
2. how to verify package integrity;
3. how to invoke the embedded runtime CLI;
4. that compiled IR must not be edited directly;
5. the question-and-answer protocol;
6. session state and checkpoints;
7. quality gates;
8. dry-run and improvement behavior;
9. session verification and the fallback route if verification fails.

### 4.2 Canonical modular source

Include the canonical source program and its active modules:

- `source/program.ordo.yaml`;
- `source/module_manifest.yaml`;
- current `source/modules/*.ordo.module.yaml` files only.

The archive must include a module-coverage list showing which module files are required by the program and confirming that every required active module is present.

Exclude superseded, experimental, draft, duplicate, or historical source modules unless the active program explicitly depends on them.

### 4.3 Compiled runtime

Build the compiled runtime from the included source, rather than copying a stale generated artifact. Include:

- `compiled/program.ir`;
- a targets manifest;
- source and output hashes;
- enough provenance to identify the source version used to create the compiled output.

The compiled output must be reproducible from the package-local source and embedded builder/runtime components. Do not treat compiled IR as a hand-edited authoring surface.

### 4.4 Embedded runtime CLI

Embed only the smallest CLI/runtime contour required for the package to operate. It must support the package's runtime entry, validation, dry-run, integrity, and output needs.

The embedded runtime must not depend on paths outside the archive. It must not require `../../` traversal, a parent repository checkout, or an undeclared Python package.

## 5. External dependencies and antipatterns

If the active process uses an antipattern layer, include a minimal local subset under a package-local dependency path. The subset must include only the patterns, rules, metadata, and tests required by the active runtime.

The package must:

- localize every required dependency;
- document each localized dependency in the manifest;
- verify that no runtime reference escapes the package root;
- validate the local antipattern subset before release.

Do not include a broad historical antipattern archive merely because it is available in the repository.

## 6. Runtime contracts

Include the current runtime contracts required to create a playbook safely:

- playbook laws;
- question registry and intake protocol;
- output contracts;
- templates;
- validation contracts;
- test and dry-run contracts;
- applicable runtime profiles;
- expected deliverables.

The package must preserve the distinction between mandatory rules, optional guidance, generated output, and user workspace content.

## 7. Visual graph utility

If the current APF/ARF process requires visual graph generation, include a package-local copy of the canonical visual graph utility and the minimal dependencies it needs.

The packaged utility must:

- run from inside the archive workspace;
- use package-local paths only;
- generate the expected graph representation;
- be named and documented as a utility, not as a hidden runtime dependency;
- have an explicit contract test or smoke test.

## 8. Documentation included in the package

Include only current documentation that a new chat or package user needs to operate the runtime correctly. Documentation must explain package purpose, startup order, runtime boundaries, expected outputs, testing, and improvement.

Do not include:

- historical session notes;
- migration reports;
- transfer packages;
- old release notes;
- superseded plans;
- developer-only repair logs;
- broad repository navigation material that is not necessary for the standalone package.

## 9. Version and identity model

Use clear, separate identities for:

- the source package version;
- the ARF runtime version;
- the generated ZIP artifact version;
- the release tag, if one exists.

The package manifest must identify:

- package name and version;
- source baseline or commit;
- build timestamp policy;
- included runtime components;
- checksums;
- required external dependencies, if any;
- expected archive root directory;
- workspace location;
- validation status.

Avoid ambiguous names such as “latest”, “current”, “developer bundle”, or “starter” when they refer to different artifacts.

## 10. Package-local path rules

Before release, scan all package text, configuration, source, compiled output, and scripts for:

- absolute local paths;
- parent-directory traversal;
- references to repository-only directories;
- references to excluded historical material;
- missing package-local files;
- untracked external dependencies.

The final archive must be self-contained. A path is valid only when it resolves inside the archive root or is explicitly declared as a user-provided workspace input.

## 11. Workspace

Provide an empty workspace intended for the user's new playbook. It must be separate from runtime source, compiled artifacts, immutable contracts, and generated evidence.

The workspace must have a short README that states:

- what the user may create there;
- what the runtime may generate there;
- what files must not be edited;
- how to preserve the user's work between chat sessions.

Do not pre-populate the workspace with an unrelated completed playbook.

## 12. Startup prompt

The package startup prompt must instruct the language model to:

1. inspect the package and verify its manifest before beginning;
2. read the canonical runtime entry files in their prescribed order;
3. use the question protocol before designing a playbook;
4. create outputs only in the designated workspace;
5. follow the playbook laws and runtime gates;
6. validate before claiming completion;
7. perform or explain the dry-run path;
8. use the improvement cycle when defects or unmet requirements are found;
9. report missing inputs, broken integrity, or unavailable capabilities rather than inventing results.

The prompt must not tell the model to inspect the parent repository or to substitute a simplified process for the packaged process.

## 13. Recommended archive structure

```text
ORDO_ARF_PLAYBOOK_FACTORY/
  START_HERE.md
  START_PROMPT.md
  ordo.yml
  ordo.runtime.json
  README.md
  KIT_MANIFEST.json
  SHA256SUMS.txt
  source/
  compiled/
  runtime/
  contracts/
  templates/
  validation/
  antipattern/
  utilities/
  workspace/
```

The exact layout may vary only when the manifest and startup documentation describe it clearly. Every executable or referenced path must remain inside this root.

## 14. Required build procedure

### Step 1 — Inventory

Inventory the active source package and identify runtime entries, modules, compiled outputs, contracts, utility dependencies, and all active references.

### Step 2 — Dependency closure

Construct a dependency closure for the canonical program. Include only files that are necessary to operate, validate, test, or explain the current runtime.

### Step 3 — Compile

Build fresh compiled IR from the selected source. Record the source and output hashes and reject stale or mismatched compiled output.

### Step 4 — Localize

Copy or generate the required runtime, CLI, utility, antipattern, template, and contract files into package-local paths. Remove parent-repository assumptions.

### Step 5 — Assemble

Create the archive tree, including an empty workspace. Generate aliases only where they improve the user-facing entry route without creating a second source of truth.

### Step 6 — Manifest and checksums

Generate the package manifest and checksums after all content is assembled. Include an inventory of every shipped file and an explicit exclusion policy.

### Step 7 — Validate

Run all required structural, integrity, path, compilation, runtime, and dry-run validations against the assembled package, not merely against the source repository.

### Step 8 — Reproducible ZIP

Create the ZIP deterministically. A repeated build from the same source baseline must produce the same logical file set, manifest data, and checksum results according to the repository's reproducibility policy.

## 15. Required validation

Validation must cover at least the following.

### Structural validation

- required files exist;
- the archive root has the expected name;
- no unexpected root files appear;
- every manifest entry resolves to a shipped file;
- every shipped file is accounted for by the manifest or an explicit allowlist.

### Integrity validation

- `SHA256SUMS.txt` verifies;
- manifest hashes verify;
- compiled output matches the selected source;
- no duplicate or conflicting runtime entries exist.

### Path and dependency validation

- no absolute local paths;
- no `../` escape paths;
- no references to excluded repository contours;
- all runtime dependencies are local or explicitly declared;
- antipattern and graph dependencies are package-local when required.

### Runtime validation

- startup instructions are complete and internally consistent;
- the embedded CLI can run the required commands;
- the question protocol, laws, contracts, validation, and improvement flow are reachable;
- a minimal dry run works from the package workspace;
- the graph utility works when included.

### Reproducibility validation

- rebuild the package from the same baseline;
- compare the expected artifact contents and checksums;
- document any permitted non-deterministic metadata;
- fail closed when an unexplained difference is found.

## 16. Acceptance criteria

The work is complete only when all of the following are true:

1. A user can download one ZIP and upload it to a new chat.
2. The chat can start by following the packaged prompt and instructions alone.
3. The package contains the full active playbook-creation process, not a simplified substitute.
4. Canonical modular source and freshly compiled runtime are both included.
5. The package contains all required contracts, templates, laws, validation, and test material.
6. Required utilities and antipattern dependencies are localized.
7. No runtime path reaches outside the archive.
8. The workspace is empty and clearly separated from immutable runtime material.
9. Manifest and checksum verification pass.
10. A package-local dry run passes.
11. The ZIP can be rebuilt reproducibly from the selected source baseline.
12. Historical, developer-only, and unrelated repository material is excluded.

## 17. Deliverables

Provide:

- the canonical source directory for the standalone ARF package;
- one canonical builder;
- the generated ZIP artifact;
- a SHA-256 file for the ZIP;
- the package manifest;
- validation evidence;
- a short release note explaining the user download route and the developer build-from-source route.

## 18. Prohibitions

Do not:

- package the whole repository;
- rely on a parent checkout;
- copy stale compiled output without verifying it;
- include historical records merely to preserve convenience;
- include an undeclared external dependency;
- leave relative paths that escape the archive;
- present a developer build as the default user route;
- claim autonomous operation unless the assembled archive has passed package-local validation.

## 19. Final principle

The resulting ZIP is a product artifact, not a source dump. It must be small enough to understand, complete enough to operate, explicit enough to validate, and autonomous enough for a new chat to create, test, improve, and deliver a new Ordo playbook without access to the rest of the repository.
