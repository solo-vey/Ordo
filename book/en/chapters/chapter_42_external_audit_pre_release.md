# Chapter 42. External Audit of the Pre-release Package

Ordo is built around a simple idea: it is not enough to say that a process is valid; you must show exactly how to verify it.

That is why, after contract/artifact coverage, rendered artifact validation, the consistency report, and the go/no-go pipeline appeared, one more layer was needed: an external package audit. This is not a new language feature or a new runtime. It is a practical way to hand the package to another person or another AI session and say: “do not trust our reports; verify them yourself.”

## What an external audit package is

An external audit package is a set of instructions for independently checking an Ordo workspace.

It answers:

- what exactly must be in the archive;
- which old directories must no longer exist;
- which CLI commands must be run;
- which reference packages must pass checks;
- how generated artifacts must be verified;
- how consistency and go/no-go must be checked;
- which package limitations must not be hidden.

This matters because Ordo must not turn a validation report into an article of faith. A report must be reproducible evidence.

## Why manual review is not enough

If a reviewer is simply asked to “look at the package,” everyone will review it differently. One person will read the README. Another will run only lint. A third will inspect the book source but not check the CLI.

M46.8 therefore introduces not a new runtime, but a standard verification route:

```text
archive structure
→ CLI install
→ repo-check
→ unit tests
→ active package checks
→ generated artifact validation
→ consistency
→ go-no-go
→ audit verdict
```

This makes external verification repeatable.

## What the reviewer must check

The reviewer must verify not only that the code does not crash, but that promises match behavior.

For example:

- if the README says the legacy site/catalog/playbook root was removed, the archive must not contain those directories;
- if the CLI says `ordo test` is static mode, the output must make that visible;
- if a package has confirmed contracts, they must reach Passport, Jira, QA Package, Implementation Prompt, and JSON reports;
- if `go-no-go` returns `go`, it must be clear which deterministic checks support that result.

## Honest boundary of the Ordo preview

The external audit must also verify honest limitations.

The current Ordo preview does not execute live AI reasoning, REST calls, Mongo checks, or production business runtime. The CLI is a deterministic helper layer. It checks structure, references, coverage, rendered artifacts, consistency, and the go/no-go report.

That is not a weakness when stated clearly. The weakness would be to call static validation a complete production runtime.

## Practical result

After M46.8, an Ordo package can be handed to another session with a ready audit prompt. The reviewer must return a short verdict:

```text
go
no_go
go_with_warnings
```

and explain which commands were run, which artifacts were inspected, and which blocking issues or warnings were found.

This turns pre-release verification from a one-time author action into a reproducible process.

## Important command order

`ordo repo-check` verifies source archive cleanliness. It must therefore run on a freshly unpacked package before `pip install -e .` and before tests, preferably as `PYTHONDONTWRITEBYTECODE=1 ordo repo-check ..`, so Python itself does not create `__pycache__`. After installation or testing, `__pycache__` and `egg-info` may appear and the source-hygiene check may correctly fail. This is not a blocker if generated metadata is removed again before final packaging.

## M46.9: self-running the external audit checklist

M46.9 adds no new language logic. Its task is to take the M46.8 checklist and run the package as a pre-release candidate: archive structure, CLI, active packages, generated artifact validation, consistency, go/no-go, documentation, and book source.

The important M46.9 result is that an audit must not trust `M*_VALIDATION_REPORT.json` by itself. It must either execute the commands or explicitly record that a command was not run. For Ordo, this is fundamental: self-report is not evidence without verification.

M46.9 found a minor documentation-hygiene mismatch: the checklist expected `cli/docs/GO_NO_GO_M46_5.md`, while the canonical CLI document was already named `cli/docs/GO_NO_GO.md`. This was not a runtime blocker, but pre-release audits must fix such issues because a reviewer should not have to guess which document is correct.

The practical rule after M46.9 is:

```text
repo-check → install CLI → tests → active packages → generated artifact flow → go-no-go → audit report
```

If all stages pass, the package may receive a `go` verdict as a source-available pre-release candidate. This still does not mean production runtime: the Ordo CLI checks deterministic structure, contracts, artifacts, and consistency; it does not execute an AI model, REST, Mongo, or a real business backend.
