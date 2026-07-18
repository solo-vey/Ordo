# Production `repo_hygiene.yml` Adoption

Status: `M70.1 safe initial policy adopted`

## Purpose

The repository now contains a production `repo_hygiene.yml` that makes root ownership explicit without claiming package-level enforcement for incompatible roots.

## Safe Phase A behavior

- `language/` and `cli/` are declared `not_applicable` for package-level `clean-check`.
- `packages/` is declared `delegated`; child packages are not centrally clean-checked.
- `cli/examples/history_event_guided_intake/` is an `optional` compatible root and is actually checked.
- `.github/` and `reports/` are `ignored` by the package clean layer because existing repo-level checks govern them.
- no root is falsely marked `required`.

## Current expected result

Running:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=cli python -m ordo.cli repo-check . --clean --profile standard --json
```

must produce a `repo_package_hygiene` section with:

- policy path `repo_hygiene.yml`;
- one checked optional root;
- one delegated root;
- eight not-applicable/ignored roots in the summary;
- no package child promoted to a required root;
- overall hygiene status `passed` when the canonical example is clean.

## Enforcement boundary

This adoption improves observability and makes CI/release execution applicable. It does not yet enforce `language/` or `cli/`. Dedicated root contracts are required before those roots can become release-blocking.

## M74.2 development/release separation

The previous guidance requiring `PYTHONDONTWRITEBYTECODE=1` is no longer the trust boundary. It may still reduce local noise, but correctness does not depend on it.

Development checks use:

```bash
ordo repo-check . --clean --profile standard --hygiene-scope development
```

Release checks use an isolated candidate tree:

```bash
git archive --format=tar HEAD | tar -xf - -C <candidate>
ordo repo-check <candidate> --clean --profile strict --hygiene-scope release --fail-on-warning
```

This ensures that normal editable installation cannot create a false release failure, while the release candidate remains subject to strict filesystem inspection.
