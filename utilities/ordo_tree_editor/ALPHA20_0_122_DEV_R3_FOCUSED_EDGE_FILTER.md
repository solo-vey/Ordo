# alpha.20.0.122-dev

Focused Data Flow now filters the rendered edge set itself, not only the selected node set.

Only causal edges following the semantic order are rendered:
Analyst input -> Transformation -> Derived state -> Document -> Archive/package.

A visible node pair no longer implies that every relation between them is drawn. Reverse edges such as Derived state -> Transformation or Document -> Transformation are suppressed in focused view.

Edge hover hit-testing is enabled only while a focused subtree is active. The full graph does not highlight endpoints on edge hover.
