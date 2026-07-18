"""Noise/script generator for the PathWalk benchmark.

Produces a scripted sequence of conversational turns (open-loop, fully
predetermined) that navigates a MazeTree from start to END, interleaved with
realistic confusion: distractions, backtracks to a named earlier step,
implicit corrections, clarifying questions, and invalid answers. Ground
truth is NOT fixed in advance - it is the byproduct of simulating this exact
script (per explicit product decision: there is no "wrong" direction, only
what the user actually, finally, chose).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from .maze_gen import MazeTree, END_SENTINEL

UA_DIRECTION = {
    "forward": ["вперед", "прямо", "рухаємось вперед"],
    "back": ["назад", "у зворотньому напрямку"],
    "left": ["ліворуч", "наліво", "вліво"],
    "right": ["праворуч", "направо", "вправо"],
    "up": ["вгору", "наверх"],
    "down": ["вниз", "донизу"],
}

TURN_TYPES = [
    "forward_valid",
    "forward_natural_language",
    "backtrack_to_step",
    "backtrack_same_choice",
    "correction_implicit",
    "clarifying_question",
    "invalid_direction_current_step",
    "invalid_backtrack_target",
]


@dataclass
class ScriptTurn:
    index: int
    type: str
    text: str
    state_changing: bool
    expected_node_after: str  # node id the NEXT question should be about, after this turn
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class PathWalkScript:
    tree_seed: int
    script_seed: int
    turns: list[ScriptTurn]
    ground_truth: list[tuple[str, str]]  # [(node_id, chosen_option), ...] length == tree.depth

    def to_dict(self) -> dict[str, Any]:
        return {
            "tree_seed": self.tree_seed,
            "script_seed": self.script_seed,
            "turns": [
                {
                    "index": t.index, "type": t.type, "text": t.text,
                    "state_changing": t.state_changing,
                    "expected_node_after": t.expected_node_after,
                    "meta": t.meta,
                }
                for t in self.turns
            ],
            "ground_truth": [{"node_id": n, "value": v} for n, v in self.ground_truth],
        }


class _Simulator:
    """Tracks confirmed path and current node as the script is built/replayed."""

    def __init__(self, tree: MazeTree):
        self.tree = tree
        self.confirmed: list[tuple[str, str]] = []  # (node_id, option)

    def current_node_id(self) -> str:
        node_id = self.tree.start
        for _, opt in self.confirmed:
            node_id = self.tree.nodes[node_id].children[opt]
        return node_id

    def is_complete(self) -> bool:
        return len(self.confirmed) >= self.tree.depth

    def forward(self, option: str | None, rng: random.Random) -> str:
        node = self.tree.nodes[self.current_node_id()]
        opt = option if option is not None else rng.choice(node.options)
        self.confirmed.append((node.id, opt))
        return opt

    def backtrack_to(self, step_index: int) -> None:
        """step_index is 0-based count of confirmed steps to keep (truncate length)."""
        self.confirmed = self.confirmed[:step_index]


def _pick_step_word(rng: random.Random, node_depth: int) -> str:
    return f"кроку {node_depth + 1}"


def generate_script(
    tree: MazeTree,
    *,
    script_seed: int,
    num_confusion_episodes: tuple[int, int] = (1, 4),
    allow_backtrack_same_choice: bool = True,
) -> PathWalkScript:
    rng = random.Random(script_seed)
    sim = _Simulator(tree)
    turns: list[ScriptTurn] = []
    idx = 0
    n_episodes = rng.randint(*num_confusion_episodes)
    episodes_inserted = 0

    def add_turn(type_: str, text: str, state_changing: bool, meta: dict | None = None) -> None:
        nonlocal idx
        turns.append(ScriptTurn(
            index=idx, type=type_, text=text, state_changing=state_changing,
            expected_node_after=sim.current_node_id() if not sim.is_complete() else END_SENTINEL,
            meta=meta or {},
        ))
        idx += 1

    while not sim.is_complete():
        node = tree.nodes[sim.current_node_id()]

        # Randomly decide whether to insert a confusion episode before the forward move,
        # but only if we still have episodes budgeted and there is history to backtrack into.
        can_insert_confusion = episodes_inserted < n_episodes
        if can_insert_confusion and rng.random() < 0.6:
            choice = rng.choice(TURN_TYPES[2:])  # bias toward non-forward types for episodes
            episodes_inserted += 1

            if choice == "clarifying_question":
                text = rng.choice([
                    f"а що означає цей вузол ({node.id})?",
                    "нагадай, будь ласка, які варіанти тут доступні?",
                    "а що було на попередньому кроці?",
                ])
                add_turn("clarifying_question", text, state_changing=False)
                continue

            if choice == "invalid_direction_current_step":
                bogus_pool = [d for d in UA_DIRECTION if d not in node.options]
                if bogus_pool:
                    bogus = rng.choice(bogus_pool)
                    add_turn(
                        "invalid_direction_current_step", bogus, state_changing=False,
                        meta={"node_id": node.id, "valid_options": list(node.options)},
                    )
                    continue

            if choice == "invalid_backtrack_target" and len(sim.confirmed) >= 0:
                bogus_target = len(sim.confirmed) + rng.randint(2, 5)
                add_turn(
                    "invalid_backtrack_target",
                    f"давай повернемось до кроку {bogus_target + 1}",
                    state_changing=False,
                    meta={"requested_step": bogus_target, "actual_confirmed_steps": len(sim.confirmed)},
                )
                continue

            if choice in ("backtrack_to_step", "backtrack_same_choice") and len(sim.confirmed) >= 1:
                target = rng.randint(0, len(sim.confirmed) - 1)
                old_node_id, old_opt = sim.confirmed[target]
                sim.backtrack_to(target)
                reopened_node = tree.nodes[sim.current_node_id()]
                add_turn(
                    "backtrack_to_step" if choice == "backtrack_to_step" else "backtrack_same_choice",
                    f"давай повернемось до {_pick_step_word(rng, target)} і підемо іншим шляхом",
                    state_changing=True,
                    meta={"target_step": target, "reopened_node": reopened_node.id},
                )
                if choice == "backtrack_same_choice" and allow_backtrack_same_choice:
                    chosen = old_opt
                else:
                    others = [o for o in reopened_node.options if o != old_opt]
                    chosen = rng.choice(others) if others else old_opt
                applied = sim.forward(chosen, rng)
                add_turn(
                    "forward_valid", applied, state_changing=True,
                    meta={"node_id": reopened_node.id, "after_backtrack": True},
                )
                continue

            if choice == "correction_implicit" and len(sim.confirmed) >= 1:
                last_node_id, last_opt = sim.confirmed[-1]
                sim.backtrack_to(len(sim.confirmed) - 1)
                reopened_node = tree.nodes[sim.current_node_id()]
                others = [o for o in reopened_node.options if o != last_opt]
                new_opt = rng.choice(others) if others else last_opt
                add_turn(
                    "correction_implicit",
                    f"ой, я помилився, там мало бути {new_opt}, не {last_opt}",
                    state_changing=True,
                    meta={"node_id": reopened_node.id, "old": last_opt, "new": new_opt},
                )
                sim.forward(new_opt, rng)
                continue

        # Default: a plain forward move (valid or natural-language phrasing)
        opt = rng.choice(node.options)
        use_natural = rng.random() < 0.4
        sim.forward(opt, rng)
        if use_natural and opt in UA_DIRECTION:
            phrase = rng.choice(UA_DIRECTION[opt])
            add_turn("forward_natural_language", phrase, state_changing=True, meta={"maps_to": opt})
        else:
            add_turn("forward_valid", opt, state_changing=True, meta={"maps_to": opt})

    return PathWalkScript(
        tree_seed=tree.seed, script_seed=script_seed, turns=turns, ground_truth=sim.confirmed
    )
