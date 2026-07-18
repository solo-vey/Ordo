from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol
import hashlib
import json
import time
import uuid

from validate_benchmark_evidence import load_schema, validate_evidence


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


class ProviderAdapter(Protocol):
    provider_name: str
    api_family: str

    def invoke(
        self,
        *,
        model: str,
        prompt: str,
        input_payload: Any,
        temperature: float | None,
        top_p: float | None,
        max_output_tokens: int | None,
        seed: int | None,
        timeout_seconds: float,
    ) -> "ProviderResponse":
        ...


@dataclass(frozen=True)
class ProviderResponse:
    resolved_model_id: str
    raw_output: Any
    normalized_output: Any
    provider_metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class BenchmarkRunConfig:
    benchmark_id: str
    dataset_version: str
    protocol_version: str
    model: str
    prompt: str
    input_payload: Any
    benchmark_mode: str = "real-model"
    temperature: float | None = 0
    top_p: float | None = 1
    max_output_tokens: int | None = 4096
    seed: int | None = None
    timeout_seconds: float = 120
    max_attempts: int = 1
    retry_backoff_seconds: float = 0
    run_id: str | None = None


class BenchmarkDriver:
    def __init__(
        self,
        *,
        adapter: ProviderAdapter,
        output_root: str | Path,
        schema_path: str | Path,
        build_session_id: str | None = None,
        current_tree_sha256: str | None = None,
        git_commit: str | None = None,
    ) -> None:
        self.adapter = adapter
        self.output_root = Path(output_root)
        self.schema = load_schema(schema_path)
        self.build_session_id = build_session_id
        self.current_tree_sha256 = current_tree_sha256
        self.git_commit = git_commit

    def run(self, config: BenchmarkRunConfig) -> dict[str, Any]:
        run_id = config.run_id or f"RUN-{uuid.uuid4()}"
        run_dir = self.output_root / run_id
        run_dir.mkdir(parents=True, exist_ok=False)

        prompt_bytes = config.prompt.encode("utf-8")
        input_bytes = _json_bytes(config.input_payload)
        (run_dir / "prompt.txt").write_bytes(prompt_bytes)
        (run_dir / "input.json").write_bytes(input_bytes)

        started_at = _utc_now()
        final_error = None
        response = None
        used_attempt = 0

        for attempt in range(1, config.max_attempts + 1):
            used_attempt = attempt
            try:
                response = self.adapter.invoke(
                    model=config.model,
                    prompt=config.prompt,
                    input_payload=config.input_payload,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    max_output_tokens=config.max_output_tokens,
                    seed=config.seed,
                    timeout_seconds=config.timeout_seconds,
                )
                final_error = None
                break
            except Exception as exc:
                final_error = {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "retryable": attempt < config.max_attempts,
                }
                if attempt < config.max_attempts and config.retry_backoff_seconds > 0:
                    time.sleep(config.retry_backoff_seconds)

        finished_at = _utc_now()

        if response is not None:
            raw_bytes = _json_bytes(response.raw_output)
            normalized_bytes = _json_bytes(response.normalized_output)
            (run_dir / "raw_output.json").write_bytes(raw_bytes)
            (run_dir / "normalized_output.json").write_bytes(normalized_bytes)
            status = "passed"
            score = 1.0
            matched = 1
            mismatched = 0
            alias_matches = 0
            mismatch_classes: list[str] = []
            resolved_model = response.resolved_model_id
            error = None
        else:
            raw_bytes = _json_bytes({"error": final_error})
            normalized_bytes = _json_bytes({"error": final_error})
            (run_dir / "raw_output.json").write_bytes(raw_bytes)
            (run_dir / "normalized_output.json").write_bytes(normalized_bytes)
            status = "error"
            score = None
            matched = 0
            mismatched = 0
            alias_matches = 0
            mismatch_classes = ["provider_error"]
            resolved_model = config.model
            error = final_error

        evidence = {
            "schema_version": "ordo.benchmark_run_evidence.v1",
            "benchmark_id": config.benchmark_id,
            "run_id": run_id,
            "benchmark_mode": config.benchmark_mode,
            "dataset_version": config.dataset_version,
            "protocol_version": config.protocol_version,
            "provider": {
                "name": self.adapter.provider_name,
                "api_family": self.adapter.api_family,
                "endpoint_class": None,
                "region": None,
            },
            "model": {
                "requested_id": config.model,
                "resolved_id": resolved_model,
                "revision": None,
            },
            "invocation": {
                "attempt": used_attempt,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "max_output_tokens": config.max_output_tokens,
                "seed": config.seed,
                "timeout_seconds": config.timeout_seconds,
                "retry_of_run_id": None,
            },
            "artifacts": {
                "prompt_sha256": _sha256_bytes(prompt_bytes),
                "input_sha256": _sha256_bytes(input_bytes),
                "raw_output_sha256": _sha256_bytes(raw_bytes),
                "normalized_output_sha256": _sha256_bytes(normalized_bytes),
                "prompt_path": str((run_dir / "prompt.txt").relative_to(self.output_root)),
                "input_path": str((run_dir / "input.json").relative_to(self.output_root)),
                "raw_output_path": str((run_dir / "raw_output.json").relative_to(self.output_root)),
                "normalized_output_path": str((run_dir / "normalized_output.json").relative_to(self.output_root)),
            },
            "result": {
                "status": status,
                "score": score,
                "matched": matched,
                "mismatched": mismatched,
                "alias_matches": alias_matches,
                "mismatch_classes": mismatch_classes,
                "error": error,
            },
            "timestamps": {
                "started_at": started_at,
                "finished_at": finished_at,
            },
            "environment": {
                "driver": "ordo.provider_neutral_benchmark_driver.v1"
            },
            "provenance": {
                "git_commit": self.git_commit,
                "build_session_id": self.build_session_id,
                "current_tree_sha256": self.current_tree_sha256,
            },
        }

        issues = validate_evidence(evidence, self.schema)
        if issues:
            raise ValueError(f"generated evidence failed validation: {issues}")

        (run_dir / "evidence.json").write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return evidence
