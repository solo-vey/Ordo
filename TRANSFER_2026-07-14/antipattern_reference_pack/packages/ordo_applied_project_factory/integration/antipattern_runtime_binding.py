from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_taxonomy(
    *,
    detector_registry: dict[str, Any],
    fundamental_registry: dict[str, Any],
    governance: dict[str, Any],
    binding: dict[str, Any],
) -> dict[str, str]:
    active_fundamentals = {
        item["id"]: item
        for item in fundamental_registry.get("items", [])
        if item.get("status") == "active"
    }
    if not active_fundamentals:
        raise ValueError("fundamental anti-pattern registry has no active rules")

    mapping: dict[str, str] = {}
    for item in detector_registry.get("items", []):
        if item.get("status") != "active":
            continue
        detector_id = item.get("id")
        fundamental_id = item.get("fundamental_id")
        if item.get("classification_level") != "subpattern":
            raise ValueError(f"runtime rule is not classified as subpattern: {detector_id}")
        if fundamental_id not in active_fundamentals:
            raise ValueError(
                f"runtime rule {detector_id} maps to missing/inactive fundamental {fundamental_id}"
            )
        if detector_id not in set(active_fundamentals[fundamental_id].get("subpattern_ids", [])):
            raise ValueError(
                f"reverse taxonomy mapping missing: {fundamental_id} -> {detector_id}"
            )
        mapping[detector_id] = fundamental_id

    taxonomy_binding = binding.get("taxonomy_binding", {})
    if taxonomy_binding.get("require_every_runtime_rule_to_map_to_active_fundamental") and (
        len(mapping) != len([i for i in detector_registry.get("items", []) if i.get("status") == "active"])
    ):
        raise ValueError("not every active runtime anti-pattern maps to an active fundamental rule")

    policy = governance.get("policy", governance.get("governance", governance))
    owner_gate = (
        policy.get("new_fundamental_rule_requires_owner_approval")
        if isinstance(policy, dict)
        else None
    )
    if owner_gate is None:
        owner_gate = fundamental_registry.get("governance", {}).get(
            "new_fundamental_rule_requires_owner_approval"
        )
    if owner_gate is not True:
        raise ValueError("taxonomy governance does not require owner approval for new fundamentals")

    expected_count = taxonomy_binding.get("fundamental_rule_count")
    if expected_count is not None and len(active_fundamentals) != expected_count:
        raise ValueError(
            f"fundamental rule count mismatch: expected={expected_count} actual={len(active_fundamentals)}"
        )
    return mapping


def load_antipattern_binding(package_root: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    package_root = Path(package_root).resolve()
    binding_path = package_root / "integration/antipattern_runtime_binding.apf.v1.json"
    binding = _load_json(binding_path)

    components = binding["canonical_components"]
    resolved: dict[str, Path] = {}
    missing = []
    for name, relative in components.items():
        path = (package_root / "../.." / relative).resolve()
        resolved[name] = path
        if not path.exists():
            missing.append(f"{name}:{relative}")
    if missing:
        raise FileNotFoundError("missing anti-pattern components: " + ", ".join(missing))

    profile = _load_json(resolved["activation_profile"])
    loader = binding["loader"]
    if profile.get("profile_id") != loader["profile_id"]:
        raise ValueError("anti-pattern activation profile id mismatch")
    if profile.get("status") != loader["required_profile_status"]:
        raise ValueError("anti-pattern activation profile is not active")

    expected = set(binding["activated_contexts"])
    actual = set(profile.get("contexts", {}))
    if expected != actual:
        raise ValueError(f"activation context mismatch: expected={sorted(expected)} actual={sorted(actual)}")

    taxonomy_map = _validate_taxonomy(
        detector_registry=_load_json(resolved["registry"]),
        fundamental_registry=_load_json(resolved["fundamental_registry"]),
        governance=_load_json(resolved["taxonomy_governance"]),
        binding=binding,
    )
    binding["resolved_taxonomy_map"] = taxonomy_map
    return binding, profile


def build_adapter(package_root: str | Path):
    package_root = Path(package_root).resolve()
    language_root = (package_root / "../..").resolve() / "language"
    import sys
    for path in (language_root, language_root / "runtime", language_root / "integration"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    from antipattern_gate_adapter import AntipatternGateAdapter
    binding, _ = load_antipattern_binding(package_root)
    adapter = AntipatternGateAdapter.from_language_root(language_root)
    adapter.taxonomy_map = dict(binding["resolved_taxonomy_map"])
    return adapter
