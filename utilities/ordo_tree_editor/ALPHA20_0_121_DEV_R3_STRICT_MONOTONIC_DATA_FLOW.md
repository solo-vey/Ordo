# alpha.20.0.121-dev

Data Flow focused traversal now uses a strict five-rank causal order:
0 Analyst input → 1 Transformation → 2 Derived state → 3 Document → 4 Archive/package.

Downstream traversal cannot decrease rank. Upstream traversal cannot increase rank.
Transformations are no longer neutral bridges.

Edge hover now uses a separate 16px transparent SVG hit path placed above the node canvas. The visible edge remains thin; hovering the hit path highlights the visible edge and its two endpoints.
