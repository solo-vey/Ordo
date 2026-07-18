# Production Repo Hygiene Policy Design

Status: `M70.0 accepted design / no production policy file yet`

## Purpose

M70.0 classifies the actual top-level roots of the Ordo language repository before a production `repo_hygiene.yml` is introduced.

The goal is to prevent a false enforcement claim. A root may be release-critical without being directly compatible with package-level `ordo clean-check`.

## Core decision

`language/` and `cli/` are release-critical repository roots, but they are not package roots in the M68 clean-check sense: neither root currently contains an `ordo.yml` manifest declaring a source YAML. Therefore M70.0 does not classify them as `required` clean-check roots.

They are classified as `not_applicable` for the current package-level engine, with an explicit migration requirement for a repo-root hygiene adapter or root-specific contract.

## Root classification

| Root | Role | Current treatment | Release critical | Reason |
|---|---|---|---:|---|
| `language/` | language core | `not_applicable` | yes | no root `ordo.yml`; requires language-root contract |
| `cli/` | CLI implementation/docs/tests | `not_applicable` | yes | no root `ordo.yml`; requires CLI-root contract |
| `cli/examples/history_event_guided_intake/` | canonical example package | `optional` | no | clean-check compatible example root |
| `packages/` | applied packages | `delegated` | no | ownership remains package-local and opt-in |
| `utilities/` | companion utilities | `not_applicable` | scope-dependent | mixed utility layout; no common package contract |
| `ordo_pathwalk/` | companion utility | `not_applicable` | scope-dependent | Python utility, not an Ordo package root |
| `book/` | book source and compiled publication | `not_applicable` | scope-dependent | governed by publication checks, not package clean-check |
| `docs/` | repository documentation | `not_applicable` | yes for release docs | governed by docs/link/schema checks, not package clean-check |
| `.github/` | CI workflow definitions | `ignored` by clean-check | yes | already covered by repo workflow validation |
| `reports/` | generated/historical evidence | `ignored` | no | should not become a package root |
| repository root metadata | release/index/license metadata | `not_applicable` | yes | covered by repo-level integrity checks |

## Production policy phases

### Phase A — safe initial policy

A first production policy may declare only roots whose current treatment is truthful:

- applied packages as `delegated`;
- canonical package examples as `optional`;
- release-critical non-package roots as `not_applicable` with documented adapter backlog;
- generated and historical areas as `ignored`.

This phase improves observability without pretending that `language/` or `cli/` were package-clean checked.

### Phase B — root contracts

Add root-specific checks for:

- language schemas, examples, registry and spec consistency;
- CLI source, tests, docs and workflow contract consistency;
- documentation/publication integrity;
- companion utility scope when included in a release.

These checks should be exposed as repo-level reports, not forced through an artificial `ordo.yml` package wrapper.

### Phase C — enforcement

Only after Phase B passes should production policy classify `language/` and `cli/` as release-blocking repo hygiene roots.

## Non-goals

M70.0 does not:

- add `repo_hygiene.yml`;
- add synthetic `ordo.yml` files to `language/` or `cli/`;
- change `clean-check` or `repo-check` implementation;
- opt applied packages into central enforcement;
- modify runtime, compiler, opcode, IR or lockfile behavior.
