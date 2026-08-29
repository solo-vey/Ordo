# alpha.20.0.126-dev

Focused Data Flow layout is now based on directed graph distance from the double-clicked node.

- root = 0;
- upstream ancestors = -1, -2, -3... by shortest incoming-edge BFS distance;
- downstream descendants = +1, +2, +3... by shortest outgoing-edge BFS distance;
- larger negative distance is placed higher; larger positive distance lower;
- fixed semantic layers are not used for focused placement;
- full/unfocused graph still uses semantic operation/data lanes;
- each directional traversal has its own visited set;
- an edge is rendered only if it actually discovered a new node during that directional traversal;
- if a node occurs in both cones, both traversed branch sets remain; its single visual row uses shortest absolute distance, with upstream winning an exact tie.
