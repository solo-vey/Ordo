from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import re


def _key(value: str) -> str:
    return re.sub(r"[._\-\s]+", ".", value.strip().lower()).strip(".")


class AliasRegistry:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.lookup: dict[str, str] = {}
        for item in payload.get("aliases", []):
            canonical = item["canonical"]
            keys = [_key(canonical)] + [_key(v) for v in item.get("variants", [])]
            for key in keys:
                previous = self.lookup.get(key)
                if previous is not None and previous != canonical:
                    raise ValueError(f"alias collision for {key}: {previous} vs {canonical}")
                self.lookup[key] = canonical

    @classmethod
    def from_file(cls, path: str | Path) -> "AliasRegistry":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def normalize(self, value: str) -> tuple[str, bool]:
        key = _key(value)
        canonical = self.lookup.get(key)
        if canonical is None:
            return value, False
        return canonical, value.strip() != canonical


class MismatchTaxonomy:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.classes = {item["id"]: item for item in payload.get("classes", [])}
        if "unknown_mismatch" not in self.classes:
            raise ValueError("taxonomy requires unknown_mismatch fallback")

    @classmethod
    def from_file(cls, path: str | Path) -> "MismatchTaxonomy":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def classify(self, mismatch_id: str | None) -> dict[str, Any]:
        if not mismatch_id:
            mismatch_id = "none"
        return self.classes.get(mismatch_id, self.classes["unknown_mismatch"])


def compare_opcode(expected: str, actual: str, registry: AliasRegistry) -> dict[str, Any]:
    expected_canonical, _ = registry.normalize(expected)
    actual_canonical, alias_used = registry.normalize(actual)

    if expected_canonical == actual_canonical:
        return {
            "semantic_match": True,
            "canonical_expected": expected_canonical,
            "canonical_actual": actual_canonical,
            "alias_used": alias_used,
            "mismatch_class": "alias_gap" if alias_used else "none",
        }

    return {
        "semantic_match": False,
        "canonical_expected": expected_canonical,
        "canonical_actual": actual_canonical,
        "alias_used": False,
        "mismatch_class": "fabricated_opcode",
    }
