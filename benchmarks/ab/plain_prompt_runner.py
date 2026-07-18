from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import hashlib
import json

from benchmark_driver import BenchmarkDriver, BenchmarkRunConfig
from contamination_controls import scan_plain_prompt, shared_payload_sha256


PLAIN_PROMPT_TEMPLATE_VERSION = "M87.3-plain-prompt-v1"


def render_plain_prompt(task: dict[str, Any]) -> str:
    shared = task["shared_input"]
    facts = shared.get("facts") or []
    acceptance = task.get("acceptance_criteria") or []
    required_output = task.get("required_output") or []

    sections = [
        f"Task: {task['title']}",
        f"Scenario: {shared.get('scenario', '')}",
        f"Request: {shared.get('request', '')}",
        "Facts:",
        *[f"- {item}" for item in facts],
        "Acceptance criteria:",
        *[f"- {item}" for item in acceptance],
        "Required output fields:",
        *[f"- {item}" for item in required_output],
        "Return only the requested result. Do not invent missing facts."
    ]
    return "\n".join(sections).strip() + "\n"


def deterministic_pair_order(pair_id: str) -> str:
    digest = hashlib.sha256(pair_id.encode("utf-8")).digest()
    return "A_then_B" if digest[0] % 2 == 0 else "B_then_A"


@dataclass(frozen=True)
class PlainPromptRunResult:
    pair_id: str
    arm: str
    order: str
    shared_payload_sha256: str
    prompt_template_version: str
    evidence: dict[str, Any]


class PlainPromptBaselineRunner:
    def __init__(self, driver: BenchmarkDriver) -> None:
        self.driver = driver

    def run_task(
        self,
        *,
        task: dict[str, Any],
        model_id: str,
        repeat: int,
        run_id: str,
        seed: int | None = None,
    ) -> PlainPromptRunResult:
        pair_id = f"PAIR-{task['task_id']}-{model_id}-{repeat}"
        prompt = render_plain_prompt(task)
        allowed_shared_texts = [
            task["title"],
            task["shared_input"].get("scenario", ""),
            task["shared_input"].get("request", ""),
            *(task["shared_input"].get("facts") or []),
            *(task.get("acceptance_criteria") or []),
            *(task.get("required_output") or []),
        ]
        contamination = scan_plain_prompt(prompt, allowed_shared_texts=allowed_shared_texts)
        if contamination:
            raise ValueError(f"plain prompt contamination detected: {contamination}")

        input_payload = {
            "task_id": task["task_id"],
            "shared_input": task["shared_input"],
            "acceptance_criteria": task["acceptance_criteria"],
            "required_output": task["required_output"],
            "shared_payload_sha256": shared_payload_sha256(task),
            "arm": "A",
            "pair_id": pair_id,
            "repeat": repeat,
        }

        evidence = self.driver.run(BenchmarkRunConfig(
            benchmark_id="ordo-vs-plain-prompt-v1",
            dataset_version="M87.2-shared-tasks-v1",
            protocol_version="M87.3",
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
            "arm": "A",
            "order": deterministic_pair_order(pair_id),
            "task_id": task["task_id"],
            "model_id": model_id,
            "repeat": repeat,
            "shared_payload_sha256": shared_payload_sha256(task),
            "prompt_template_version": PLAIN_PROMPT_TEMPLATE_VERSION,
            "prompt_sha256": evidence["artifacts"]["prompt_sha256"],
            "evidence_run_id": evidence["run_id"],
        }

        run_dir = self.driver.output_root / evidence["run_id"]
        (run_dir / "ab_metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        return PlainPromptRunResult(
            pair_id=pair_id,
            arm="A",
            order=metadata["order"],
            shared_payload_sha256=metadata["shared_payload_sha256"],
            prompt_template_version=PLAIN_PROMPT_TEMPLATE_VERSION,
            evidence=evidence,
        )


def load_dataset(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
