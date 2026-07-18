# APF Current State Snapshot — Transfer Package

Generated: 2026-07-09T15:06:52+00:00
Purpose: перенос поточного стану діалогу в новий чат без втрати рішень, backlog, packaged utility, compile/startup gates і актуальних пакетів.

## Current baseline

```text
module_id: ordo.applied_project_factory
current_version: v0.1.0-rc.4-post-svg
parent_line: Ordo v0.12 / M63.9 APF integration
status: ready / go
blocking_issues: 0
latest_patch: COMPILE_AND_START_PROMPT_PACKAGING_GATES
```

## Current package sequence

```text
N_EXECUTION_MODE_DECLARATION
→ N_COMPILED_RUNTIME_USAGE_GATE
→ N_RUNTIME_COMPILATION_GATE
→ N_FACTORY_MODE_SELECTION
→ ... APF creation/refinement process ...
→ FINAL_COMPLETION_ARTIFACTS_GENERATION
→ COMPILE_UTILITY_DISCOVERY_GATE
→ PACKAGE_PROFILE_GATE
→ DERIVED_ARTIFACT_SYNC_GATE
→ DELTA_BACKLOG_CONVENTION_GATE
→ SVG_GRAPH_GENERATOR_PACKAGING_GATE
→ START_PROMPT_PACKAGING_GATE
→ README_STARTUP_SECTION_GATE
→ PACKAGE_COMPOSITION_GATE
→ FINAL_ARCHIVE_ASSEMBLY
```

## Implemented release-candidate line

```text
rc.2               PACKAGE_COMPOSITION_GATE
rc.3-p1            explicit execution mode declaration
rc.3-p2            COMPILED_RUNTIME_USAGE_GATE
rc.3-p3            RUNTIME_COMPILATION_GATE
rc.3-p4            hybrid mode preferred and non-intrusive
rc.3-p5            DERIVED_ARTIFACT_SYNC_GATE
rc.3-p6            DELTA_BACKLOG_CONVENTION_GATE
rc.4-svg           SVG_GRAPH_GENERATOR_PACKAGING_GATE
rc.4-post-svg      COMPILE_AND_START_PROMPT_PACKAGING_GATES
```

## rc.4-post-svg summary

Implemented:

```text
docs/COMPILE_AND_START_PROMPT_PACKAGING_POLICY.md
tools/compile_with_bundled_ordo.py
N_SHARED_TAIL_COMPILE_UTILITY_DISCOVERY_GATE
N_SHARED_TAIL_PACKAGE_PROFILE_GATE
N_SHARED_TAIL_START_PROMPT_PACKAGING_GATE
N_SHARED_TAIL_README_STARTUP_SECTION_GATE
G_COMPILE_UTILITY_DISCOVERY_GATE_EVALUATED
G_COMPILE_UTILITY_LOCATION_DOCUMENTED
G_COMPILE_UTILITY_COMMAND_DOCUMENTED
G_COMPILE_UTILITY_OUTPUT_TARGETS_DOCUMENTED
G_PACKAGE_PROFILE_DECLARED
G_PACKAGE_PROFILE_MATCHES_CONTENTS
G_RUNTIME_CAPABLE_PROFILE_REQUIRES_RUNTIME_COMPILATION_EVIDENCE
G_START_PROMPT_FILE_INCLUDED
G_HUMAN_START_GUIDE_INCLUDED
G_START_PROMPT_REFERENCES_RUNTIME_OR_SOURCE_PROFILE
G_README_STARTUP_SECTION_PRESENT
G_README_STARTUP_SECTION_NAMES_ACTUAL_FILES
A_COMPILE_CAPABILITY_DISCOVERABLE
A_PACKAGE_PROFILE_MUST_MATCH_CONTENTS
A_FINISHED_PACKAGE_MUST_INCLUDE_START_PROMPT
```

## Future improvement captured

The uploaded improvement prompt was preserved for future implementation, not applied now:

```text
source_reference/APF_BASE_PROCESS_PROGRAM_LEVEL_METADATA_IMPROVEMENT_PROMPT.md
backlog item: FUTURE-PROGRAM-CONTRACT-01
scope: program-level metadata / interaction semantics / approval gates
```

## Latest validation status

```text
lint: passed
compile: passed
test: passed
coverage: passed
validate-state: passed
validate-output: passed
validate-artifacts: passed
consistency: passed_with_warnings / non-blocking
verify-targets: passed
runtime-status: ready
runtime-entry: ready → N_EXECUTION_MODE_DECLARATION
go/no-go: go
package build: passed
blocking_issues: 0
```

## Latest artifacts included in this transfer package

```text
artifacts/ordo_applied_project_factory_v0_1_0_rc_4_post_svg_dev.zip
artifacts/ordo_applied_project_factory_v0_1_0_rc_4_post_svg_runtime.zip
artifacts/ordo_github_workspace_v0_12_m63_9_apf_v0_1_0_rc_4_post_svg.zip
artifacts/ordo_github_workspace_v0_12_m63_9_apf_v0_1_0_rc_4_post_svg_clean_source.zip
reports/APF_V0_1_0_RC_4_POST_SVG_VALIDATION_REPORT.json
reports/APF_V0_1_0_RC_4_POST_SVG_COMPILE_STARTUP_PACKAGING_REPORT.json
reports/M63_9_APF_RC4_POST_SVG_COMPILE_STARTUP_PACKAGING_REPORT.md
backlog/APF_DELTA_BACKLOG_REGISTER.md
```

## Next recommended implementation step

```text
FUTURE-PROGRAM-CONTRACT-01 — program-level metadata, interaction semantics and approval gates
```
