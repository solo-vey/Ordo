"""Tree generator for the PathWalk determinism benchmark.

Produces a pure-data tree spec: every node has 2-6 labeled options, every
option leads to a genuinely distinct child node, and every path of length D
(depth) reaches END. No dead ends by design (per explicit product decision:
there is no "wrong" direction, only a path the user actually took).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

DIRECTIONS = ["forward", "back", "left", "right", "up", "down"]
END_SENTINEL = "END"


@dataclass
class MazeNode:
    id: str
    depth: int  # 0-indexed; depth == tree.depth means this node's answers lead to END
    options: list[str]
    children: dict[str, str] = field(default_factory=dict)  # option -> child node id or END_SENTINEL


@dataclass
class MazeTree:
    seed: int
    depth: int
    branching_range: tuple[int, int]
    start: str
    nodes: dict[str, MazeNode]

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "depth": self.depth,
            "branching_range": list(self.branching_range),
            "start": self.start,
            "nodes": {
                nid: {"id": n.id, "depth": n.depth, "options": n.options, "children": n.children}
                for nid, n in self.nodes.items()
            },
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "MazeTree":
        nodes = {
            nid: MazeNode(id=n["id"], depth=n["depth"], options=n["options"], children=n["children"])
            for nid, n in data["nodes"].items()
        }
        return MazeTree(
            seed=data["seed"],
            depth=data["depth"],
            branching_range=tuple(data["branching_range"]),
            start=data["start"],
            nodes=nodes,
        )


def _new_id(rng: random.Random, depth: int) -> str:
    suffix = "".join(rng.choice("0123456789abcdef") for _ in range(6))
    return f"STEP_{depth}_{suffix}"


def generate_tree(
    *,
    seed: int,
    depth: int,
    branching_range: tuple[int, int] = (2, 6),
    max_options: int = len(DIRECTIONS),
) -> MazeTree:
    """Generate a complete tree of exact depth `depth`.

    Every node at depth < `depth` has between branching_range[0] and
    branching_range[1] distinct labeled options (subset of DIRECTIONS),
    each leading to a genuinely distinct child node. Nodes at depth ==
    `depth` - 1 have children pointing to END_SENTINEL instead of a real
    child (their answer is the final forward move that completes the path).
    """
    if branching_range[1] > max_options:
        raise ValueError(f"branching_range upper bound {branching_range[1]} exceeds available directions {max_options}")
    rng = random.Random(seed)
    nodes: dict[str, MazeNode] = {}
    start_id = _new_id(rng, 0)

    def build(node_id: str, node_depth: int) -> None:
        branching = rng.randint(branching_range[0], branching_range[1])
        options = sorted(rng.sample(DIRECTIONS, branching))
        children: dict[str, str] = {}
        node = MazeNode(id=node_id, depth=node_depth, options=options, children=children)
        nodes[node_id] = node
        is_last_level = node_depth == depth - 1
        for opt in options:
            if is_last_level:
                children[opt] = END_SENTINEL
            else:
                child_id = _new_id(rng, node_depth + 1)
                children[opt] = child_id
                build(child_id, node_depth + 1)

    build(start_id, 0)
    return MazeTree(seed=seed, depth=depth, branching_range=branching_range, start=start_id, nodes=nodes)


def random_walk(tree: MazeTree, rng: random.Random) -> list[tuple[str, str]]:
    """A single clean forward walk from start to END (no noise). Returns
    [(node_id, chosen_option), ...] of length tree.depth."""
    path: list[tuple[str, str]] = []
    current = tree.start
    for _ in range(tree.depth):
        node = tree.nodes[current]
        opt = rng.choice(node.options)
        path.append((current, opt))
        current = node.children[opt]
    return path
