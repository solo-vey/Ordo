# Playbook regression

Ordo now includes two versioned, candidate regression contours:

- [Playbook Regression Harness (PRH) 1.7.0](../../utilities/playbook_regression_harness/versions/1.7.0/README.md) — deterministic, semantic, stability, provenance, and behavioral-package preparation utilities.
- [Playbook Regression Playbook (PRP) 0.2.0-alpha.1](../../packages/playbook_regression/versions/0.2.0-alpha.1/docs/QUICKSTART.md) — the orchestration playbook that controls the regression journey and invokes PRH.

## Dependency

PRP `0.2.0-alpha.1` depends on PRH `1.7.0`. The PRP directory contains an expanded dependency snapshot for self-contained review; it is not a ZIP binary and is not an independent source of truth.

## Vibe ARF authoring use

Use this contour after a Vibe ARF playbook has a baseline and candidate package. Run deterministic checks first, then select `provider_api`, `chat_native`, or `skip_behavioral`. Behavioral runs occur in a separate chat or provider environment, and returned evidence is imported for differential and stability analysis. Chat-native evidence remains bounded by its provenance policy and cannot by itself produce a production `GO`.

The full pilot, re-evaluation of the existing trace set, and promotion from candidate remain backlog work.
