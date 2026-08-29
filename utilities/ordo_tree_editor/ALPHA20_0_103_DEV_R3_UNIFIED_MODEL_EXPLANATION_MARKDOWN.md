# alpha.20.0.103-dev — Unified model explanation Markdown rendering

All persistent model-generated explanation surfaces now use the same safe Markdown renderer:
- node Behavior explanation;
- reference/Python resource explanation;
- verification one-shot explanation;
- Verification Assistant;
- AI Settings Assistant.

The renderer escapes source HTML before applying supported Markdown constructs, so model Markdown is presented as formatted HTML without allowing raw model HTML injection.
