# alpha.20.0.125-dev

Focused Data Flow selection is now a pure directed graph slice.

Double-clicked root:
- recursively follows incoming edges only for upstream;
- recursively follows outgoing edges only for downstream;
- never changes traversal direction;
- expands each node at most once per direction, so cycles terminate;
- renders the union of upstream ancestors, root, and downstream descendants;
- renders only edges actually traversed in those two directed cones.

Semantic layers are now presentation/layout only and do not control focused membership.
