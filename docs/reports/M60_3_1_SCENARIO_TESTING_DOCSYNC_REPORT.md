# M60.3.1 Scenario Testing Documentation Sync Report

## Scope

This documentation-only patch adds a stable place for PathWalk-style scenario testing in the Ordo documentation set and book source.

## Added

```text
docs/testing/ORDO_PATHWALK_SCENARIO_TESTING.md
language/SCENARIO_TESTING_COMPATIBILITY.md
cli/docs/SCENARIO_TESTING_WITH_RUNTIME_CLI.md
book/source/chapters/chapter_57_scenario_testing_i_pathwalk.md
```

## Updated

```text
README.md
CHANGELOG.md
language/README.md
language/CURRENT_VERSION.md
book/source/README.md
book/source/book_manifest.json
book/source/STRUCTURE_AUDIT.json
book/source/chapters/appendix_a_slovnyk_ordo.md
```

## Explicitly not included

```text
PathWalk utility source code
runtime CLI behavior changes
new Ordo compiler target
restore-session implementation
compiled all-in-one book
PDF generation
```

## Compatibility intent

The new documents define how external scenario-testing utilities should interact with M60 runtime packages:

```text
use ./cli_embedded/ordo in enforced mode
support runtime_view=json and runtime_view=ordo-code
run verify-targets and verify-session
inspect session.ordo.trace and evidence reports
score runtime artifacts, not model claims
treat model direct access to compiled/* as a protocol violation
```
