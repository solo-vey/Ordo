from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def resolve_package_root(path: str | Path) -> Path:
    p = Path(path).resolve()
    if p.is_file():
        p = p.parent
    if (p / "ordo.yml").exists():
        return p
    if (p.parent / "ordo.yml").exists():
        return p.parent
    raise FileNotFoundError(f"Cannot find ordo.yml near {path}")


def load_package(package_path: str | Path) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = resolve_package_root(package_path)
    manifest = load_yaml(root / "ordo.yml")
    source_path = root / manifest.get("source", "source/program.ordo.yaml")
    tests_path = root / manifest.get("tests", "tests/test_cases.yaml")
    source = load_yaml(source_path)
    tests = load_yaml(tests_path) if tests_path.exists() else {}
    return root, manifest, source, tests
