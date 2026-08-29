# Semantic Projection & Specification Diff v1

## Goal
Detect semantic regressions that raw file and graph diffs can miss.

## Projections
- Behavioral Specification
- Decision Table
- Invariant Catalogue

## Rules
- Baseline and candidate are extracted independently.
- The same extraction prompt and schema are used.
- Every proposition cites source evidence.
- Comparison is proposition-based, not prose-based.
- Weakening or removal of a mandatory baseline invariant is blocking.
- Missing evidence or disagreement between projections yields REVIEW_REQUIRED.
