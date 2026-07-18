# Book Localization Bootstrap Report

## Completed

- Created separate English and Ukrainian book source trees.
- Preserved the complete Ukrainian M72 baseline.
- Added the atomic-steps and micro-prompts chapters to the Ukrainian chapter source.
- Declared English as the future source of truth.
- Introduced stable chapter identifiers, chapter-level semantic versions, SHA-256 hashes, and synchronization states.
- Added localization and translation workflow policies.
- Froze the approved Ukrainian PDF without regenerating it.
- Added an English-only repository documentation policy and a machine-readable migration audit.

## Translation state

The English translation tree is initialized but not falsely marked complete. Every untranslated chapter is explicitly listed as `translation_required`. This preserves publication integrity while enabling controlled chapter-by-chapter translation.
