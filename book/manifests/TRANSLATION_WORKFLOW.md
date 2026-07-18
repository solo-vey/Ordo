# Chapter Translation Workflow

For each chapter:

1. Lock the source English version and SHA-256.
2. Translate prose without translating language identifiers, op-codes, schemas, file names, or executable examples unless the example is explicitly natural-language content.
3. Preserve heading hierarchy, code fences, tables, links, anchors, image references, callouts, and normative strength.
4. Run terminology consistency checks.
5. Compare all requirements, prohibitions, conditions, gates, statuses, and examples against the source.
6. Record the translated chapter version and the exact English source version/hash.
7. Set `in_review`, then `synced` only after semantic review.

A translation must not silently simplify, generalize, or omit operational details.
