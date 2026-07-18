# Book Localization and Versioning Policy

## Canonical language

English (`en`) is the canonical language for future book development. Ukrainian (`uk`) is a maintained translation.

## Chapter identity

Every chapter has a stable `chapter_id`. File names may evolve, but the identifier must remain stable across locales.

## Chapter versioning

Each locale records `content_version` per chapter using semantic versioning:

- PATCH — editorial correction that does not change meaning;
- MINOR — new explanation, example, or compatible methodological extension;
- MAJOR — changed contract, meaning, structure, or recommendation that requires deliberate translation review.

## Synchronization states

- `synced` — the translation matches the canonical chapter version;
- `outdated` — the canonical English chapter is newer;
- `translation_required` — no complete target-language chapter exists;
- `in_review` — translation exists but semantic parity is not confirmed;
- `blocked` — synchronization cannot proceed because the source is unstable or ambiguous.

A translation is synchronized only when its recorded source version and source hash match the canonical English chapter.

## Change flow

1. Change the English chapter.
2. Increment the English chapter version.
3. Update the English hash.
4. Mark affected translations as `outdated`.
5. Translate only changed chapters or changed semantic sections.
6. Review terminology, examples, code, links, and meaning.
7. Update the target version and source reference.
8. Mark the pair `synced`.

## Rendered artifacts

PDF and other rendered books are derived artifacts. The currently approved Ukrainian PDF is frozen and must not be regenerated until explicitly requested.


## Improvement-task documentation impact rule

Every language or ARF improvement task must include a documentation and book impact assessment. When canonical book changes are required, the English source, manifest, hashes, and translation freshness status must be updated within the same improvement task. PDF generation remains explicit and is not automatic.
