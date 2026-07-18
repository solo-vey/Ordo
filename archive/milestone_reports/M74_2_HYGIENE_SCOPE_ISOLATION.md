# M74.2 — Development and Release Hygiene Scope Isolation

## Problem

The former repository metadata gate scanned the installed working tree as if it were a release candidate. Normal operations such as `pip install -e ./cli`, imports, and test execution create `__pycache__`, `.pyc`, or `.egg-info`, causing false release failures.

## Accepted model

```text
development worktree
→ inspect Git-tracked source hygiene
→ report local transients without blocking

isolated release candidate tree
→ inspect the full filesystem strictly
→ block generated Python metadata
```

## CLI contract

```bash
ordo repo-check . --hygiene-scope development
ordo repo-check <candidate-tree> --hygiene-scope release
```

The report uses `ordo.repo_check.report.v2` and preserves `hygiene_scope`, `profile`, and `clean_enabled`. A development PASS cannot be reused as release evidence.

## Workflow contract

- pull-request and main-branch clean gates explicitly use `development`;
- the release workflow creates `.ordo-release-candidate` from `git archive HEAD`;
- strict release validation runs only against that isolated export.

## Enforcement rules

- untracked local Python metadata: visible, non-blocking in development;
- Git-tracked Python metadata: blocking in development;
- any Python metadata in release candidate: blocking in release;
- release-tree checks do not depend on `PYTHONDONTWRITEBYTECODE`.

## Compatibility

Package-level `clean-check`, repository root contracts, delegated package ownership, and generated package artifact checks remain unchanged.
