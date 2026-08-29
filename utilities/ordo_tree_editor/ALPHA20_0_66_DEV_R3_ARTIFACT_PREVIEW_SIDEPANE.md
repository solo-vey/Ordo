# alpha.20.0.66-dev — stable Markdown preview side pane

UI-only R3 fix.

- Markdown artifact preview no longer lives inside the scrollable tree workspace.
- Preview occupies the stable right-side grid area, so tree scroll/zoom cannot place it outside the visible viewport.
- Clicking the Markdown file card opens the preview side pane.
- Closing preview restores the tree side pane.
- Download controls use compact neutral line icons instead of blue heavy arrows.
- No playbook, Compiler, or runtime execution semantic changes.
