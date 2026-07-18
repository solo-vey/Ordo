"""Self-driven mode mechanics for `ordo-pathwalk run --driver self`.

No external API call - the CURRENT agentic session plays the model-under-test
and is guided through the script one turn at a time via these two functions,
mirroring the M58 principle (CLI-mediated access, not direct file reads) so
the agent cannot peek ahead at future turns or at the ground truth.

Usage from an agent's own tool loop:
    python3 -m ordo_pathwalk.cli self-feed-next --session <dir>
    ... (agent acts on the sandbox, using its own tools) ...
    python3 -m ordo_pathwalk.cli self-submit --session <dir> --response-file <path>
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..generator.noise_gen import PathWalkScript


def _session_state_path(session_dir: Path) -> Path:
    return session_dir / "self_session_state.json"


def init_self_session(session_dir: Path, script: PathWalkScript) -> None:
    """Write the script into a location the player is instructed not to read
    directly, and initialize the consumption journal at seq 0."""
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "_script_hidden.json").write_text(
        json.dumps(script.to_dict(), ensure_ascii=False), encoding="utf-8"
    )
    _session_state_path(session_dir).write_text(
        json.dumps({"next_turn_index": 0, "transcript": []}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def feed_next_turn(session_dir: Path) -> dict[str, Any]:
    """Return only the next unconsumed turn, or a completion marker. Refuses
    to advance past a turn that has no recorded response yet."""
    state_path = _session_state_path(session_dir)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    script_data = json.loads((session_dir / "_script_hidden.json").read_text(encoding="utf-8"))
    turns = script_data["turns"]
    idx = state["next_turn_index"]

    if idx >= len(turns):
        return {"status": "no_more_turns", "total_turns": len(turns)}

    pending = [t for t in state["transcript"] if t["turn_index"] == idx]
    if pending and "response_text" not in pending[-1]:
        return {"status": "awaiting_submit", "turn_index": idx, "reason": "previous turn not yet submitted"}

    turn = turns[idx]
    return {
        "status": "ok",
        "turn_index": turn["index"],
        "text": turn["text"],
        # Deliberately NOT returning turn["type"] or turn["expected_node_after"] -
        # those would leak ground-truth-adjacent information to the player.
    }


def submit_turn_response(session_dir: Path, turn_index: int, response_text: str, asked_node_id: str | None) -> dict[str, Any]:
    state_path = _session_state_path(session_dir)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if turn_index != state["next_turn_index"]:
        return {
            "status": "rejected",
            "reason": f"out_of_order: expected turn_index={state['next_turn_index']}, got {turn_index}",
        }
    state["transcript"].append({
        "turn_index": turn_index,
        "response_text": response_text,
        "asked_node_id": asked_node_id,
    })
    state["next_turn_index"] = turn_index + 1
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "accepted", "next_turn_index": state["next_turn_index"]}


def build_scoreable_transcript(session_dir: Path) -> list[dict[str, Any]]:
    """Merge the (hidden-from-player) script metadata back in, for scoring only."""
    state = json.loads(_session_state_path(session_dir).read_text(encoding="utf-8"))
    script_data = json.loads((session_dir / "_script_hidden.json").read_text(encoding="utf-8"))
    turns_by_index = {t["index"]: t for t in script_data["turns"]}
    merged = []
    for entry in state["transcript"]:
        turn_meta = turns_by_index.get(entry["turn_index"], {})
        merged.append({
            "turn_index": entry["turn_index"],
            "turn_type": turn_meta.get("type"),
            "user_text": turn_meta.get("text"),
            "model_reply_text": entry.get("response_text"),
            "asked_node_id": entry.get("asked_node_id"),
            "expected_node_after": turn_meta.get("expected_node_after"),
        })
    return merged
