# Development and Release Hygiene Scopes

Ordo repository hygiene uses two explicit evidence scopes.

## Development scope

`ordo repo-check . --hygiene-scope development`

This mode is intended for an installed or actively tested working tree. Generated Python metadata is blocking only when it is tracked by Git. Local `__pycache__`, `.pyc`, and `.egg-info` paths are reported as observations but do not fail the gate.

This prevents normal operations such as `pip install -e ./cli`, imports, and test execution from creating false release failures.

## Release scope

`ordo repo-check <candidate-tree> --hygiene-scope release`

This mode strictly scans the supplied candidate tree. Any `__pycache__`, `.pyc`, or `.egg-info` path blocks the gate.

The release workflow must not run this mode against the installed checkout. It first creates a clean candidate using `git archive HEAD`, then validates the extracted tree. Thus the gate evaluates release content, not local development side effects.

## Trust boundary

```text
development worktree
→ tracked-source hygiene
→ local transients are observable but non-blocking

clean source export
→ release-tree hygiene
→ generated metadata is strictly forbidden
```

The two reports must preserve the selected `hygiene_scope` and evidence mode so that a development PASS cannot be presented as release evidence.
