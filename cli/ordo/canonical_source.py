"""Fail-closed identity checks for an Ordo package's canonical source file."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import argparse
import hashlib
import json
import yaml


SCHEMA = "ordo.canonical_source_identity.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_path(root: Path, raw: Any) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _identity(root: Path, source: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    stat = source.stat()
    return {
        "package": manifest.get("name"),
        "package_version": manifest.get("version"),
        "manifest_path": "ordo.yml",
        "declared_source_path": str(manifest.get("source", "")),
        "verified_source_path": source.relative_to(root).as_posix(),
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace("+00:00", "Z"),
        "sha256": sha256_file(source),
    }


def validate_canonical_source(
    package: str | Path,
    *,
    expected_sha256: str | None = None,
    expected_version: str | None = None,
    supplied_source: str | Path | None = None,
) -> dict[str, Any]:
    """Validate that one package has exactly one authoritative source file.

    The function is read-only. It rejects path escapes, missing/non-regular sources,
    stale digests, version drift, duplicate same-name source files, and callers that
    attempt to use a non-canonical path.
    """
    root = Path(package).resolve()
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    manifest_path = root / "ordo.yml"
    manifest: dict[str, Any] = {}
    if not manifest_path.is_file():
        errors.append({"code": "CANONICAL_MANIFEST_MISSING", "message": "missing package manifest: ordo.yml"})
        return _report(root, manifest, None, errors, warnings)
    try:
        loaded = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest = loaded if isinstance(loaded, dict) else {}
    except Exception as exc:
        errors.append({"code": "CANONICAL_MANIFEST_INVALID", "message": f"cannot read ordo.yml: {exc}"})
        return _report(root, manifest, None, errors, warnings)

    declared = manifest.get("source")
    source = _safe_relative_path(root, declared)
    if source is None:
        errors.append({"code": "CANONICAL_SOURCE_UNSAFE", "message": "manifest source must be a relative path inside the package"})
        return _report(root, manifest, None, errors, warnings)
    if not source.is_file():
        errors.append({"code": "CANONICAL_SOURCE_MISSING", "message": f"canonical source is missing or not a file: {declared}"})
        return _report(root, manifest, source, errors, warnings)

    identity = _identity(root, source, manifest)
    if supplied_source is not None:
        supplied = Path(supplied_source).resolve()
        if supplied != source:
            errors.append({"code": "CANONICAL_SOURCE_PATH_MISMATCH", "message": f"supplied source is not canonical: {supplied.relative_to(root) if supplied.is_relative_to(root) else supplied}"})
    if expected_sha256 is not None and identity["sha256"] != expected_sha256:
        errors.append({"code": "CANONICAL_SOURCE_SHA256_MISMATCH", "message": "canonical source SHA-256 does not match the expected digest"})
    if expected_version is not None and manifest.get("version") != expected_version:
        errors.append({"code": "CANONICAL_SOURCE_VERSION_MISMATCH", "message": "package version does not match the expected version"})

    # Example/fixture payloads and shipped template/regression inputs intentionally
    # contain illustrative programs with the same filename; they are not candidate
    # package sources. All other same-name files are ambiguous and fail closed.
    noncanonical_contours = {"generated_examples", "examples", "fixtures", "tests"}

    def is_noncanonical(path: Path) -> bool:
        parts = path.relative_to(root).parts
        if set(parts) & noncanonical_contours:
            return True
        return (
            parts[:4] == ("cli_embedded", "ordo_pkg", "ordo", "templates")
            or parts[:2] == ("regression", "prp")
        )

    same_name = sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob(source.name)
        if p.is_file() and p.resolve() != source and not is_noncanonical(p)
    )
    if same_name:
        errors.append({"code": "CANONICAL_SOURCE_DUPLICATE_NAME", "message": f"duplicate canonical source filename found: {', '.join(same_name)}"})
    return _report(root, manifest, identity, errors, warnings)


def _report(root: Path, manifest: dict[str, Any], identity: dict[str, Any] | None, errors: list[dict[str, str]], warnings: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA,
        "status": "passed" if not errors else "blocked",
        "package": str(root),
        "package_id": manifest.get("name"),
        "package_version": manifest.get("version"),
        "source_identity": identity,
        "errors": errors,
        # Common report shape consumed by `ordo lint` and CI aggregation.
        "issues": errors,
        "warnings": warnings,
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "pass_evidence": identity if not errors else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an Ordo package canonical source identity")
    parser.add_argument("package")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--expected-version")
    parser.add_argument("--source", dest="supplied_source")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    report = validate_canonical_source(args.package, expected_sha256=args.expected_sha256, expected_version=args.expected_version, supplied_source=args.supplied_source)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
