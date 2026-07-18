from __future__ import annotations

from typing import Any
from benchmark_driver import ProviderResponse


class FixtureAdapter:
    provider_name = "fixture"
    api_family = "local-fixture"

    def __init__(self, output: Any, *, resolved_model_id: str = "fixture-model-v1", fail_times: int = 0):
        self.output = output
        self.resolved_model_id = resolved_model_id
        self.fail_times = fail_times
        self.calls = 0

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
    ) -> ProviderResponse:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RuntimeError("synthetic provider failure")
        return ProviderResponse(
            resolved_model_id=self.resolved_model_id,
            raw_output=self.output,
            normalized_output=self.output,
            provider_metadata={"calls": self.calls},
        )
