from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from antipattern_runtime import AntipatternRuntime


class AntipatternGateAdapter:
    def __init__(
        self,
        *,
        runtime: AntipatternRuntime,
        activation_profile: dict[str, Any],
    ) -> None:
        self.runtime = runtime
        self.profile = activation_profile
        self.taxonomy_map: dict[str, str] = {}

    @classmethod
    def from_language_root(cls, language_root: str | Path) -> "AntipatternGateAdapter":
        root = Path(language_root)
        runtime = AntipatternRuntime.from_language_root(root)
        profile = json.loads(
            (root / "integration/antipattern_activation_profile.apf.v1.json")
            .read_text(encoding="utf-8")
        )
        return cls(runtime=runtime, activation_profile=profile)

    def evaluate_gate(
        self,
        *,
        state: dict[str, Any],
        context_type: str,
        source_id: str,
        source_hash: str | None = None,
        detected_at: str | None = None,
        enabled_antipattern_overrides: list[str] | None = None,
    ) -> dict[str, Any]:
        contexts = self.profile["contexts"]
        if context_type not in contexts:
            raise ValueError(f"context is not activated: {context_type}")

        config = contexts[context_type]
        profile_enabled = set(config["enabled_antipatterns"])
        enabled = set(enabled_antipattern_overrides) if enabled_antipattern_overrides is not None else profile_enabled
        unknown = enabled - set(self.runtime.antipatterns)
        if unknown:
            raise ValueError(f"unknown or inactive anti-pattern override(s): {sorted(unknown)}")
        incompatible = []
        for antipattern_id in sorted(enabled):
            supported = any(
                rule.get("antipattern_id") == antipattern_id
                and context_type in rule.get("input_contract", {}).get("allowed_contexts", [])
                for rule in self.runtime.rules
            )
            if not supported:
                incompatible.append(antipattern_id)
        if incompatible:
            raise ValueError(
                f"anti-pattern override(s) unsupported for context {context_type}: {incompatible}"
            )
        findings = []

        for antipattern_id in sorted(enabled):
            findings.extend(self.runtime.evaluate_one(
                antipattern_id=antipattern_id,
                state=state,
                context_type=context_type,
                source_id=source_id,
                source_hash=source_hash,
                detected_at=detected_at,
            ))

        from antipattern_finding_model import aggregate_findings
        report = aggregate_findings(findings)
        report["gate_id"] = config["gate"]
        report["activation_profile_id"] = self.profile["profile_id"]
        report["context_type"] = context_type
        report["source_id"] = source_id
        report["enabled_antipatterns"] = sorted(enabled)
        report["profile_default_antipatterns"] = sorted(profile_enabled)
        report["override_applied"] = enabled_antipattern_overrides is not None
        report["enabled_fundamental_antipatterns"] = sorted({
            self.taxonomy_map[rule_id]
            for rule_id in enabled
            if rule_id in self.taxonomy_map
        })
        report["detector_to_fundamental_mapping"] = {
            rule_id: self.taxonomy_map[rule_id]
            for rule_id in sorted(enabled)
            if rule_id in self.taxonomy_map
        }

        if (
            report["decision"] == "inconclusive"
            and self.profile["policy"]["inconclusive_policy"]
            == "block_when_required_signals_missing_for_blocking_rule"
        ):
            report["decision"] = "block"
            report["inconclusive_escalated_to_block"] = True
        else:
            report["inconclusive_escalated_to_block"] = False

        return report

    def enforce_gate(self, report: dict[str, Any]) -> None:
        if report["decision"] == "block":
            ids = ", ".join(report.get("blocking_finding_ids", []))
            raise RuntimeError(
                f"anti-pattern gate {report.get('gate_id')} blocked execution"
                + (f": {ids}" if ids else "")
            )
