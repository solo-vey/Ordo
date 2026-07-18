from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
import hashlib
import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone

CACHE_SCHEMA_VERSION = "ordo.apf.package_cache_state.v1"
RELOAD_DECISION_VERSION = "ordo.apf.package_reload_decision.v1"
TRACE_EVENTS = {
    "PACKAGE_CACHE_HIT",
    "PACKAGE_CACHE_MISS",
    "PACKAGE_RELOAD_REQUIRED",
    "PACKAGE_RELOAD_COMPLETED",
    "PACKAGE_CACHE_INVALIDATED",
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def validate_package_cache_state(state: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    if not isinstance(state, dict):
        return {"status": "fail", "schema_version": CACHE_SCHEMA_VERSION, "issues": [{"code": "PACKAGE_CACHE_STATE_NOT_MAPPING", "message": "cache state must be a mapping"}]}

    required = {
        "schema_version",
        "package_loaded",
        "package_version",
        "package_fingerprint",
        "unpacked_location",
        "manifest_validated",
        "source_of_truth_loaded",
        "cache_valid",
    }
    for key in sorted(required - set(state)):
        issues.append({"code": "PACKAGE_CACHE_FIELD_MISSING", "message": f"missing required field: {key}", "location": key})

    if state.get("schema_version") != CACHE_SCHEMA_VERSION:
        issues.append({"code": "PACKAGE_CACHE_SCHEMA_UNSUPPORTED", "message": f"schema_version must be {CACHE_SCHEMA_VERSION}", "location": "schema_version"})
    for key in ("package_loaded", "manifest_validated", "source_of_truth_loaded", "cache_valid"):
        if key in state and not isinstance(state.get(key), bool):
            issues.append({"code": "PACKAGE_CACHE_BOOLEAN_REQUIRED", "message": f"{key} must be boolean", "location": key})
    fp = state.get("package_fingerprint")
    if fp is not None and (not isinstance(fp, str) or not _SHA256_RE.fullmatch(fp)):
        issues.append({"code": "PACKAGE_CACHE_FINGERPRINT_INVALID", "message": "package_fingerprint must be a lowercase SHA-256 hex string", "location": "package_fingerprint"})
    if state.get("package_loaded"):
        if not state.get("package_version"):
            issues.append({"code": "PACKAGE_CACHE_VERSION_MISSING", "message": "loaded package must record package_version", "location": "package_version"})
        if not state.get("unpacked_location"):
            issues.append({"code": "PACKAGE_CACHE_LOCATION_MISSING", "message": "loaded package must record unpacked_location", "location": "unpacked_location"})
    if state.get("cache_valid") and not all(state.get(k) is True for k in ("package_loaded", "manifest_validated", "source_of_truth_loaded")):
        issues.append({"code": "PACKAGE_CACHE_VALIDITY_CONTRADICTION", "message": "cache_valid requires package_loaded, manifest_validated and source_of_truth_loaded", "location": "cache_valid"})

    return {"status": "pass" if not issues else "fail", "schema_version": CACHE_SCHEMA_VERSION, "issues": issues}


def evaluate_package_reload_necessity(
    state: dict[str, Any] | None,
    *,
    incoming_version: str | None,
    incoming_fingerprint: str | None,
    required_files: list[str] | None = None,
    explicit_reload: bool = False,
    check_filesystem: bool = True,
) -> dict[str, Any]:
    """Return a fail-closed reload decision without mutating process state."""
    reasons: list[str] = []
    event = "PACKAGE_CACHE_HIT"

    if explicit_reload:
        reasons.append("explicit_reload_requested")
    if state is None:
        reasons.append("cache_state_missing")
    else:
        validation = validate_package_cache_state(state)
        if validation["status"] != "pass":
            reasons.append("cache_state_invalid")
        if not state.get("cache_valid"):
            reasons.append("cache_marked_invalid")
        if incoming_version is not None and state.get("package_version") != incoming_version:
            reasons.append("package_version_changed")
        if incoming_fingerprint is not None and state.get("package_fingerprint") != incoming_fingerprint:
            reasons.append("package_fingerprint_changed")
        if not state.get("manifest_validated"):
            reasons.append("manifest_not_validated")
        if not state.get("source_of_truth_loaded"):
            reasons.append("source_of_truth_not_loaded")

        location = state.get("unpacked_location")
        if check_filesystem and location:
            root = Path(location)
            if not root.is_dir():
                reasons.append("unpacked_location_unavailable")
            else:
                for rel in required_files or []:
                    p = (root / rel).resolve()
                    try:
                        p.relative_to(root.resolve())
                    except ValueError:
                        reasons.append(f"required_file_path_escape:{rel}")
                        continue
                    if not p.exists():
                        reasons.append(f"required_file_missing:{rel}")

    reload_required = bool(reasons)
    if reload_required:
        event = "PACKAGE_CACHE_MISS" if "cache_state_missing" in reasons else "PACKAGE_RELOAD_REQUIRED"
    return {
        "schema_version": RELOAD_DECISION_VERSION,
        "decision": "reload_required" if reload_required else "cache_hit",
        "reload_required": reload_required,
        "trace_event": event,
        "reasons": reasons,
        "process_state_mutation_allowed": False,
        "active_node_must_remain_unchanged": True,
    }


_FINGERPRINT_DOMAIN = b"ordo.apf.package_fingerprint.v1\\0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_package_fingerprint(source: str | Path, *, exclude_names: Iterable[str] | None = None) -> str:
    """Compute a stable content fingerprint for a package file or directory.

    Directory fingerprints include normalized relative paths, file modes and bytes in
    lexical order. Timestamps and absolute paths are intentionally excluded.
    """
    root = Path(source)
    if not root.exists():
        raise FileNotFoundError(root)
    excluded = set(exclude_names or {"__pycache__", ".pytest_cache", ".DS_Store"})
    h = hashlib.sha256()
    h.update(_FINGERPRINT_DOMAIN)
    if root.is_file():
        h.update(b"F\\0")
        h.update(root.name.encode("utf-8"))
        h.update(b"\\0")
        with root.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    if not root.is_dir():
        raise ValueError(f"unsupported package source: {root}")
    for path in sorted(root.rglob("*"), key=lambda x: x.relative_to(root).as_posix()):
        rel = path.relative_to(root)
        if any(part in excluded for part in rel.parts):
            continue
        rel_text = rel.as_posix().encode("utf-8")
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed in package fingerprinting: {rel.as_posix()}")
        if path.is_dir():
            h.update(b"D\\0" + rel_text + b"\\0")
            continue
        if path.is_file():
            h.update(b"F\\0" + rel_text + b"\\0")
            h.update(str(path.stat().st_mode & 0o777).encode("ascii") + b"\\0")
            with path.open("rb") as fh:
                for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                    h.update(chunk)
    return h.hexdigest()


def persist_cache_state_atomic(state: dict[str, Any], state_file: str | Path) -> Path:
    """Validate and atomically persist cache state as canonical JSON."""
    validation = validate_package_cache_state(state)
    if validation["status"] != "pass":
        raise ValueError(f"invalid cache state: {validation['issues']}")
    target = Path(state_file)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, target)
        try:
            dir_fd = os.open(target.parent, os.O_DIRECTORY)
        except (AttributeError, OSError):
            dir_fd = None
        if dir_fd is not None:
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise
    return target


def load_cache_state(state_file: str | Path) -> dict[str, Any] | None:
    path = Path(state_file)
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cache state is unreadable: {path}") from exc
    validation = validate_package_cache_state(state)
    if validation["status"] != "pass":
        raise ValueError(f"cache state is invalid: {validation['issues']}")
    return state


def _copy_package_source(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination)
    elif source.is_file():
        destination.mkdir(parents=True, exist_ok=False)
        shutil.copy2(source, destination / source.name)
    else:
        raise ValueError(f"unsupported package source: {source}")


def atomic_load_package_cache(
    source: str | Path,
    *,
    package_version: str,
    cache_root: str | Path,
    state_file: str | Path,
    required_files: list[str] | None = None,
    expected_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Load a package through staging and atomically replace the active cache.

    The previous cache and state file remain intact if copying, fingerprinting or
    required-file validation fails.
    """
    src = Path(source).resolve()
    root = Path(cache_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    fingerprint = compute_package_fingerprint(src)
    if expected_fingerprint is not None and fingerprint != expected_fingerprint:
        raise ValueError("incoming package fingerprint does not match expected_fingerprint")

    staging_parent = Path(tempfile.mkdtemp(prefix=".package-cache-stage-", dir=root.parent))
    staged = staging_parent / "payload"
    active = root / "active"
    backup = root / ".active.backup"
    try:
        _copy_package_source(src, staged)
        for rel in required_files or []:
            candidate = (staged / rel).resolve()
            try:
                candidate.relative_to(staged.resolve())
            except ValueError as exc:
                raise ValueError(f"required file escapes package root: {rel}") from exc
            if not candidate.is_file():
                raise ValueError(f"required file missing after staged load: {rel}")

        staged_fingerprint = compute_package_fingerprint(staged)
        if src.is_dir() and staged_fingerprint != fingerprint:
            raise ValueError("staged package fingerprint mismatch")

        if backup.exists():
            shutil.rmtree(backup)
        if active.exists():
            os.replace(active, backup)
        try:
            os.replace(staged, active)
            state = {
                "schema_version": CACHE_SCHEMA_VERSION,
                "package_loaded": True,
                "package_version": package_version,
                "package_fingerprint": fingerprint,
                "unpacked_location": str(active),
                "manifest_validated": True,
                "source_of_truth_loaded": True,
                "cache_valid": True,
                "loaded_at": _utc_now(),
                "invalidated_at": None,
                "invalidation_reason": None,
            }
            persist_cache_state_atomic(state, state_file)
        except Exception:
            if active.exists():
                shutil.rmtree(active)
            if backup.exists():
                os.replace(backup, active)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        return {"status": "pass", "trace_event": "PACKAGE_RELOAD_COMPLETED", "state": state}
    finally:
        shutil.rmtree(staging_parent, ignore_errors=True)


def invalidate_package_cache_atomic(
    *,
    state_file: str | Path,
    reason: str,
    remove_payload: bool = False,
) -> dict[str, Any]:
    """Atomically mark cache invalid, optionally removing payload after state commit."""
    previous = load_cache_state(state_file)
    if previous is None:
        return {"status": "pass", "trace_event": "PACKAGE_CACHE_INVALIDATED", "state": None}
    updated = dict(previous)
    updated.update({
        "cache_valid": False,
        "invalidated_at": _utc_now(),
        "invalidation_reason": reason,
    })
    persist_cache_state_atomic(updated, state_file)
    if remove_payload:
        location = Path(str(previous.get("unpacked_location", "")))
        if location.is_dir():
            shutil.rmtree(location)
    return {"status": "pass", "trace_event": "PACKAGE_CACHE_INVALIDATED", "state": updated}


def ensure_package_cache(
    source: str | Path,
    *,
    package_version: str,
    cache_root: str | Path,
    state_file: str | Path,
    required_files: list[str] | None = None,
    explicit_reload: bool = False,
) -> dict[str, Any]:
    """Return a valid cached package, loading only when the reload gate requires it.

    On a cache hit this function MUST NOT copy, unpack, or reread the source package.
    The decision is based solely on the persisted cache state and cached payload.
    """
    try:
        state = load_cache_state(state_file)
    except ValueError:
        state = None

    incoming_fingerprint: str | None = None
    incoming_version = package_version

    # Fast path: do not touch source bytes when the current cache already matches
    # the requested version and the cached payload remains valid.
    if state is not None and state.get("package_version") == package_version and not explicit_reload:
        decision = evaluate_package_reload_necessity(
            state,
            incoming_version=package_version,
            incoming_fingerprint=state.get("package_fingerprint"),
            required_files=required_files,
            explicit_reload=False,
            check_filesystem=True,
        )
        if decision["decision"] == "cache_hit":
            return {
                "status": "pass",
                "decision": "cache_hit",
                "trace_event": "PACKAGE_CACHE_HIT",
                "state": state,
                "source_read_performed": False,
                "unpack_performed": False,
            }

    # Reload path: source content is read exactly once to obtain the fingerprint,
    # then atomic_load_package_cache validates the same expected fingerprint.
    incoming_fingerprint = compute_package_fingerprint(source)
    decision = evaluate_package_reload_necessity(
        state,
        incoming_version=incoming_version,
        incoming_fingerprint=incoming_fingerprint,
        required_files=required_files,
        explicit_reload=explicit_reload,
        check_filesystem=True,
    )
    if decision["decision"] == "cache_hit":
        return {
            "status": "pass",
            "decision": "cache_hit",
            "trace_event": "PACKAGE_CACHE_HIT",
            "state": state,
            "source_read_performed": True,
            "unpack_performed": False,
        }

    loaded = atomic_load_package_cache(
        source,
        package_version=package_version,
        cache_root=cache_root,
        state_file=state_file,
        required_files=required_files,
        expected_fingerprint=incoming_fingerprint,
    )
    return {
        **loaded,
        "decision": "reloaded",
        "reload_reason": decision["reasons"],
        "source_read_performed": True,
        "unpack_performed": True,
    }

TRACE_SCHEMA_VERSION = "ordo.apf.package_cache_trace.v1"
METRICS_SCHEMA_VERSION = "ordo.apf.package_cache_metrics.v1"
DIAGNOSTICS_SCHEMA_VERSION = "ordo.apf.package_cache_diagnostics.v1"


def append_cache_trace_event(trace_file: str | Path, *, event: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    if event not in TRACE_EVENTS:
        raise ValueError(f"unsupported cache trace event: {event}")
    record = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "event": event,
        "timestamp": _utc_now(),
        "details": details or {},
    }
    path = Path(trace_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def compute_cache_metrics(trace_file: str | Path) -> dict[str, Any]:
    counts = {event: 0 for event in sorted(TRACE_EVENTS)}
    path = Path(trace_file)
    malformed = 0
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            event = record.get("event")
            if event in counts:
                counts[event] += 1
            else:
                malformed += 1
    hits = counts["PACKAGE_CACHE_HIT"]
    misses = counts["PACKAGE_CACHE_MISS"] + counts["PACKAGE_RELOAD_REQUIRED"]
    total = hits + misses
    return {
        "schema_version": METRICS_SCHEMA_VERSION,
        "counts": counts,
        "cache_hit_ratio": (hits / total) if total else None,
        "decision_events": total,
        "malformed_records": malformed,
        "status": "pass" if malformed == 0 else "warn",
    }


def diagnose_package_cache(state_file: str | Path, *, required_files: list[str] | None = None, trace_file: str | Path | None = None) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    try:
        state = load_cache_state(state_file)
    except ValueError as exc:
        state = None
        findings.append({"severity": "error", "code": "CACHE_STATE_UNREADABLE", "message": str(exc)})
    if state is None:
        findings.append({"severity": "error", "code": "CACHE_STATE_MISSING", "message": "cache state is missing"})
    else:
        validation = validate_package_cache_state(state)
        for issue in validation["issues"]:
            findings.append({"severity": "error", **issue})
        location = Path(str(state.get("unpacked_location", "")))
        if not location.is_dir():
            findings.append({"severity": "error", "code": "CACHE_PAYLOAD_MISSING", "message": "unpacked cache location is unavailable"})
        else:
            for rel in required_files or []:
                candidate = (location / rel).resolve()
                try:
                    candidate.relative_to(location.resolve())
                except ValueError:
                    findings.append({"severity": "error", "code": "CACHE_REQUIRED_FILE_PATH_ESCAPE", "message": rel})
                    continue
                if not candidate.is_file():
                    findings.append({"severity": "error", "code": "CACHE_REQUIRED_FILE_MISSING", "message": rel})
    metrics = compute_cache_metrics(trace_file) if trace_file is not None else None
    if metrics and metrics["malformed_records"]:
        findings.append({"severity": "warning", "code": "CACHE_TRACE_MALFORMED", "message": str(metrics["malformed_records"])})
    return {
        "schema_version": DIAGNOSTICS_SCHEMA_VERSION,
        "status": "fail" if any(x["severity"] == "error" for x in findings) else ("warn" if findings else "pass"),
        "findings": findings,
        "metrics": metrics,
    }
