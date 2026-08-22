#!/usr/bin/env python3
"""Generic profile selector adapter for SIMPLE_DOCUMENT_RECONCILIATION_VERIFICATION.

The host generator fills knowledge/DOMAIN_PROFILE_CATALOG.yaml. This script deliberately
contains no host-domain profile names. It selects only from explicit configured field labels,
accepts provisional markers as current context, and fails closed on zero/multiple matches.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"PyYAML is required: {exc}")


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).casefold()


def extract_explicit_values(text: str, labels: list[str]) -> list[str]:
    values: list[str] = []
    lines = text.splitlines()
    for raw_label in labels:
        label = str(raw_label).strip()
        if not label or label.startswith("<"):
            continue
        esc = re.escape(label)
        patterns = [
            re.compile(rf"^\s*\|\s*{esc}\s*\|\s*(.*?)\s*\|", re.I),
            re.compile(rf"^\s*{esc}\s*[:=]\s*(.+?)\s*$", re.I),
        ]
        for line in lines:
            for pat in patterns:
                m = pat.search(line)
                if m:
                    values.append(m.group(1).strip())
    return values


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--document", required=True, help="Current document path")
    p.add_argument("--catalog", required=True, help="Filled DOMAIN_PROFILE_CATALOG.yaml")
    p.add_argument("--emit-content", action="store_true", help="Include selected profile content")
    args = p.parse_args()

    document_path = Path(args.document).resolve()
    catalog_path = Path(args.catalog).resolve()
    text = document_path.read_text(encoding="utf-8")
    catalog = load_yaml(catalog_path) or {}

    selector = catalog.get("selector") or {}
    labels = selector.get("field_labels") or []
    provisional_markers = [normalize(x) for x in (selector.get("provisional_markers") or []) if x]
    profiles = catalog.get("profiles") or {}

    explicit_values = extract_explicit_values(text, labels)
    matches = []
    for value in explicit_values:
        nvalue = normalize(value)
        for key, spec in profiles.items():
            aliases = [str(key)] + [str(x) for x in ((spec or {}).get("aliases") or [])]
            for alias in aliases:
                nalias = normalize(alias)
                # Match the configured alias as a token/current field value, allowing trailing approval markers/prose.
                if nvalue == nalias or nvalue.startswith(nalias + " ") or nvalue.startswith(nalias + " `"):
                    matches.append((str(key), value, spec or {}))
                    break

    unique = {}
    for key, value, spec in matches:
        unique[key] = (value, spec)

    if len(unique) != 1:
        result = {
            "status": "UNRESOLVED",
            "profile_key": None,
            "reason": "explicit profile field must resolve uniquely to one configured profile",
            "explicit_values": explicit_values,
            "matched_profiles": sorted(unique),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    key, (raw_value, spec) = next(iter(unique.items()))
    nraw = normalize(raw_value)
    provisional = any(marker and marker in nraw for marker in provisional_markers)
    profile_path = (catalog_path.parent.parent / str(spec.get("profile_path", ""))).resolve()
    if not profile_path.is_file():
        result = {
            "status": "UNRESOLVED",
            "profile_key": key,
            "reason": f"configured profile file not found: {profile_path}",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 3

    result = {
        "status": "SELECTED",
        "profile_key": key,
        "provisional": provisional,
        "raw_explicit_value": raw_value,
        "profile_path": str(profile_path),
    }
    if args.emit_content:
        result["profile_content"] = profile_path.read_text(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())


def correct_profile_with_current_evidence(provisional_profile_key: str, evidence_supported_profile_keys: list[str]) -> dict:
    """Generic v1.2 correction contract; evidence may confirm or autonomously correct a provisional selection.
    Domain adapters provide evidence_supported_profile_keys. Zero/multiple supported profiles fail closed.
    """
    keys=sorted({str(x) for x in evidence_supported_profile_keys if str(x).strip()})
    if len(keys)!=1:
        return {"status":"UNRESOLVED","provisional_profile_key":provisional_profile_key,"selected_profile_key":None,"reason":"current evidence must resolve exactly one bound profile"}
    selected=keys[0]
    return {"status":"CONFIRMED" if selected==provisional_profile_key else "CORRECTED","provisional_profile_key":provisional_profile_key,"selected_profile_key":selected,"discard_stale_profile_findings":selected!=provisional_profile_key}
