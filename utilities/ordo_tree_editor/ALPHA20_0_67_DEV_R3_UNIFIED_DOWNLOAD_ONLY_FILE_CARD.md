# alpha.20.0.67-dev — unified download-only file cards

UI-only R3 polish.

- Non-preview artifacts (ZIP and other files) now use the same compact file-card
  visual language as Markdown artifacts.
- The file card itself is not interactive for non-preview artifacts.
- Only the neutral download icon on the right performs download.
- The legacy blue/text `Download <filename>` renderer is removed.
- File type metadata is shown in the card (for example `ZIP archive`).

Markdown preview behavior is unchanged.

No playbook, Compiler semantic, or runtime execution semantic changes.
