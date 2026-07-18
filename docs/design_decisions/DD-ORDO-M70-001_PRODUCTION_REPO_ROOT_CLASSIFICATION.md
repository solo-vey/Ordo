# DD-ORDO-M70-001 — Production Repository Root Classification

Status: accepted

## Decision

Do not introduce a production `repo_hygiene.yml` that marks `language/` or `cli/` as `required` package clean-check roots.

Both roots are release-critical, but neither currently satisfies the package contract expected by `ordo clean-check`.

M70 will proceed in two stages:

1. truthful policy adoption using `delegated`, `optional`, `ignored` and `not_applicable` classifications;
2. root-specific repo check contracts before release-blocking enforcement.

## Consequences

- no synthetic manifests are added merely to satisfy the checker;
- applied packages remain delegated;
- M70.1 may add a production policy only if it preserves this classification;
- M70.2 should implement or connect real root-specific checks rather than wrapping non-package roots as fake packages.
