# M70.0 — Production Repo Hygiene Policy Design and Root Classification

Status: `accepted-design / passed-scope-validation`

This milestone classifies actual repository roots without adding production enforcement.

Key result: `language/` and `cli/` are release-critical but currently `not_applicable` to package-level clean-check because they have no root `ordo.yml`. Applied packages remain delegated.
