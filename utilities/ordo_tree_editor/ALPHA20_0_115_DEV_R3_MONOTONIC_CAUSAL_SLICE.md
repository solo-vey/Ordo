# alpha.20.0.115-dev — Monotonic causal slice

Focused Data Flow now renders a directional causal slice rather than unrestricted closure. Upstream traversal can only stay on or move toward earlier semantic data layers; downstream traversal can only stay on or move toward later layers. Transformation nodes act as neutral causal bridges. This prevents downstream documents/packages from pulling sibling variables and their ancestry back into the focused graph.
