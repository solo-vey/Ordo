from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from benchmark_driver import BenchmarkDriver, BenchmarkRunConfig
from contamination_controls import shared_payload_sha256


ORDO_PROMPT_TEMPLATE_VERSION = "M87.4-ordo-prompt-v1"


def render_ordo_prompt(task: dict[str, Any]) -> str:
    shared = task["shared_input"]
    facts = shared.get("facts") or []
    acceptance = task.get("acceptance_criteria") or []
    required_output = task.get("required_output") or []

    sections = [
        f"Ordo task: {task['title']}",
        f"Scenario: {shared.get('scenario', '')}",
        f"Request: {shared.get('request', '')}",
        "Shared facts:",
        *[f"- {item}" for item in facts],
        "Acceptance criteria:",
        *[f"- {item}" for item in acceptance],
        "Required output fields:",
        *[f"- {item}" for item in required_output],
        "Apply explicit contracts, state protection, mandatory process gates, truthful completion labels, and structured output.",
        "Do not invent missing facts. Do not mutate state without authorization.",
    ]
    return "\n".join(sections).strip() + "\n"


@dataclass(frozen=True)
class OrdoRunResult:
    pair_id: str
    arm: str
    shared_payload_sha256: str
    prompt_template_version: str
    evidence: dict[str, Any]


class OrdoArmRunner:
    def __init__(self, driver: BenchmarkDriver) -> None:
        self.driver = driver

    def run_task(
        self,
        *,
        task: dict[str, Any],
        model_id: str,
        repeat: int,
        pair_id: str,
        run_id: str,
        seed: int | None = None,
    ) -> OrdoRunResult:
        prompt = render_ordo_prompt(task)
        shared_hash = shared_payload_sha256(task)

        input_payload = {
            "task_id": task["task_id"],
            "shared_input": task["shared_input"],
            "acceptance_criteria": task["acceptance_criteria"],
            "required_output": task["required_output"],
            "shared_payload_sha256": shared_hash,
            "arm": "B",
            "pair_id": pair_id,
            "repeat": repeat,
        }

        evidence = self.driver.run(BenchmarkRunConfig(
            benchmark_id="ordo-vs-plain-prompt-v1",
            dataset_version="M87.2-shared-tasks-v1",
            protocol_version="M87.4",
            model=model_id,
            prompt=prompt,
            input_payload=input_payload,
            benchmark_mode="real-model",
            temperature=0,
            top_p=1,
            max_output_tokens=4096,
            seed=seed,
            timeout_seconds=120,
            max_attempts=1,
            run_id=run_id,
        ))

        metadata = {
            "schema_version": "ordo.ab_arm_run_metadata.v1",
            "pair_id": pair_id,
            "arm": "B",
            "task_id": task["task_id"],
            "model_id": model_id,
            "repeat": repeat,
            "shared_payload_sha256": shared_hash,
            "prompt_template_version": ORDO_PROMPT_TEMPLATE_VERSION,
            "prompt_sha256": evidence["artifacts"]["prompt_sha256"],
            "evidence_run_id": evidence["run_id"],
        }

        run_dir = self.driver.output_root / evidence["run_id"]
        (run_dir / "ab_metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        return OrdoRunResult(
            pair_id=pair_id,
            arm="B",
            shared_payload_sha256=shared_hash,
            prompt_template_version=ORDO_PROMPT_TEMPLATE_VERSION,
            evidence=evidence,
        )
