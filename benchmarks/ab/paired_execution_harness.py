from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from contamination_controls import validate_arm_equivalence
from plain_prompt_runner import PlainPromptBaselineRunner, deterministic_pair_order
from ordo_runner import OrdoArmRunner


@dataclass(frozen=True)
class PairExecutionResult:
    pair_id: str
    order: str
    arm_a_run_id: str
    arm_b_run_id: str
    shared_payload_sha256: str
    pair_manifest_path: Path


class PairedExecutionHarness:
    def __init__(
        self,
        *,
        plain_runner: PlainPromptBaselineRunner,
        ordo_runner: OrdoArmRunner,
        output_root: str | Path,
    ) -> None:
        self.plain_runner = plain_runner
        self.ordo_runner = ordo_runner
        self.output_root = Path(output_root)

    def run_pair(
        self,
        *,
        task: dict[str, Any],
        model_id: str,
        repeat: int,
        seed: int | None = None,
    ) -> PairExecutionResult:
        pair_id = f"PAIR-{task['task_id']}-{model_id}-{repeat}"
        order = deterministic_pair_order(pair_id)

        plain_payload = {
            "shared_input": task["shared_input"],
            "acceptance_criteria": task["acceptance_criteria"],
            "required_output": task["required_output"],
        }
        ordo_payload = dict(plain_payload)
        equivalence_issues = validate_arm_equivalence(task, plain_payload, ordo_payload)
        if equivalence_issues:
            raise ValueError(f"arm shared-content mismatch: {equivalence_issues}")

        arm_a_run_id = f"{pair_id}-A"
        arm_b_run_id = f"{pair_id}-B"

        if order == "A_then_B":
            a = self.plain_runner.run_task(
                task=task, model_id=model_id, repeat=repeat,
                run_id=arm_a_run_id, seed=seed
            )
            b = self.ordo_runner.run_task(
                task=task, model_id=model_id, repeat=repeat,
                pair_id=pair_id, run_id=arm_b_run_id, seed=seed
            )
        else:
            b = self.ordo_runner.run_task(
                task=task, model_id=model_id, repeat=repeat,
                pair_id=pair_id, run_id=arm_b_run_id, seed=seed
            )
            a = self.plain_runner.run_task(
                task=task, model_id=model_id, repeat=repeat,
                run_id=arm_a_run_id, seed=seed
            )

        if a.pair_id != b.pair_id:
            raise ValueError("pair_id mismatch between arms")
        if a.shared_payload_sha256 != b.shared_payload_sha256:
            raise ValueError("shared payload hash mismatch between arms")

        manifest = {
            "schema_version": "ordo.ab_pair_execution_manifest.v1",
            "pair_id": pair_id,
            "task_id": task["task_id"],
            "model_id": model_id,
            "repeat": repeat,
            "order": order,
            "shared_payload_sha256": a.shared_payload_sha256,
            "arms": {
                "A": {
                    "run_id": a.evidence["run_id"],
                    "prompt_sha256": a.evidence["artifacts"]["prompt_sha256"],
                    "output_sha256": a.evidence["artifacts"]["normalized_output_sha256"],
                    "status": a.evidence["result"]["status"],
                },
                "B": {
                    "run_id": b.evidence["run_id"],
                    "prompt_sha256": b.evidence["artifacts"]["prompt_sha256"],
                    "output_sha256": b.evidence["artifacts"]["normalized_output_sha256"],
                    "status": b.evidence["result"]["status"],
                }
            }
        }

        pair_dir = self.output_root / "pairs" / pair_id
        pair_dir.mkdir(parents=True, exist_ok=False)
        manifest_path = pair_dir / "pair_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        return PairExecutionResult(
            pair_id=pair_id,
            order=order,
            arm_a_run_id=arm_a_run_id,
            arm_b_run_id=arm_b_run_id,
            shared_payload_sha256=a.shared_payload_sha256,
            pair_manifest_path=manifest_path,
        )
