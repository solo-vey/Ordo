from __future__ import annotations

from pathlib import Path
from typing import Any
import json


def _package_root_for_report(path: Path) -> Path | None:
    for parent in (path.parent, *path.parents):
        if (parent / "ordo.yml").is_file():
            try:
                relative = path.resolve().relative_to(parent.resolve())
            except ValueError:
                return None
            return parent if relative.parts and relative.parts[0] == "reports" else None
    return None


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    package_root = _package_root_for_report(path)
    if package_root is not None and isinstance(data, dict) and "evidence_identity" not in data:
        from .evidence_identity import attach_evidence_identity
        data = attach_evidence_identity(data, package_root, report_name=path.name)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
