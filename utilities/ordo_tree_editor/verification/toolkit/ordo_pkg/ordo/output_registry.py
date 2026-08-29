from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import yaml


@dataclass
class TemplateSetRef:
    id: str
    version: str
    root: str
    catalog: str
    source: str


def _set_path(registry_root: Path, set_id: str, version: str) -> Path:
    parts = [p for p in set_id.split('.') if p]
    return registry_root.joinpath(*parts, version)


def _candidate_roots(package_root: Path) -> list[tuple[str, Path]]:
    # M43 lean mode: templates are package-local, not workspace/global registry artifacts.
    return [("package_local", package_root / "output_templates")]


def list_template_sets(package_root: str | Path | None = None) -> list[dict[str, Any]]:
    root = Path(package_root).resolve() if package_root else Path.cwd().resolve()
    found: dict[tuple[str, str, str], TemplateSetRef] = {}
    for source, registry_root in _candidate_roots(root):
        if not registry_root.exists():
            continue
        for catalog in registry_root.rglob("output_templates.yaml"):
            try:
                rel_parent = catalog.parent.relative_to(registry_root)
            except ValueError:
                continue
            parts = rel_parent.parts
            if len(parts) < 2:
                continue
            version = parts[-1]
            set_id = ".".join(parts[:-1])
            key = (set_id, version, source)
            found[key] = TemplateSetRef(
                id=set_id,
                version=version,
                root=str(catalog.parent),
                catalog=str(catalog),
                source=source,
            )
    return [asdict(v) for v in sorted(found.values(), key=lambda x: (x.id, x.version, x.source))]


def resolve_template_set(package_root: str | Path, set_id: str, version: str, preferred_source: str | None = None) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    root = Path(package_root).resolve()
    candidates = _candidate_roots(root)
    if preferred_source == "local_package":
        preferred_source = "package_local"
    if preferred_source:
        candidates = [item for item in candidates if item[0] == preferred_source]
    for source, registry_root in candidates:
        set_root = _set_path(registry_root, set_id, version)
        catalog = set_root / "output_templates.yaml"
        if catalog.exists():
            data = yaml.safe_load(catalog.read_text(encoding="utf-8")) or {}
            meta = {"id": set_id, "version": version, "source": source, "root": str(set_root), "catalog": str(catalog)}
            return data, catalog, meta
    source_text = f" in {preferred_source}" if preferred_source else ""
    raise FileNotFoundError(f"template set {set_id}@{version} not found{source_text}")
