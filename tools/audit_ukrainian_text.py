#!/usr/bin/env python3
"""Read-only, archive-aware audit for Ukrainian text in repository payloads.

The scanner reads Git-tracked files by default, treats ``book/**`` as the only
intentional localization contour, and recursively inspects ZIP, TAR, and GZIP
members.  It never extracts archives to the working tree.
"""
from __future__ import annotations

import argparse
import fnmatch
import gzip
import io
import json
import re
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Iterable


UKRAINIAN = re.compile(r"[А-Яа-яІіЇїЄєҐґ]")
DEFAULT_EXCLUSIONS = ("book/**",)
ARCHIVE_SUFFIXES = (
    ".zip",
    ".tar",
    ".tar.gz",
    ".tgz",
    ".tar.bz2",
    ".tbz2",
    ".tar.xz",
    ".txz",
    ".gz",
)


class Limits:
    def __init__(
        self,
        max_archive_depth: int,
        max_members_per_archive: int,
        max_member_bytes: int,
        max_total_archive_bytes: int,
    ) -> None:
        self.max_archive_depth = max_archive_depth
        self.max_members_per_archive = max_members_per_archive
        self.max_member_bytes = max_member_bytes
        self.max_total_archive_bytes = max_total_archive_bytes


def matches(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return path == prefix or path.startswith(f"{prefix}/")
    return fnmatch.fnmatchcase(path, pattern)


def tracked_files(root: Path) -> list[Path] | None:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        return None
    return [root / entry for entry in result.stdout.decode("utf-8").split("\0") if entry]


def filesystem_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.relative_to(root).parts:
            yield path


def is_archive(name: str, payload: bytes) -> bool:
    lower = name.lower()
    return (
        lower.endswith(ARCHIVE_SUFFIXES)
        or zipfile.is_zipfile(io.BytesIO(payload))
        or tarfile.is_tarfile(io.BytesIO(payload))
    )


def text_occurrences(payload: bytes, sample_limit: int) -> tuple[int, list[str]]:
    if b"\0" in payload[:8192]:
        return 0, []
    text = payload.decode("utf-8", errors="ignore")
    lines = [line.strip() for line in text.splitlines() if UKRAINIAN.search(line)]
    return len(lines), lines[:sample_limit]


def archive_members(name: str, payload: bytes, limits: Limits) -> tuple[list[tuple[str, bytes]], list[str]]:
    members: list[tuple[str, bytes]] = []
    warnings: list[str] = []
    source = io.BytesIO(payload)
    try:
        if zipfile.is_zipfile(source):
            with zipfile.ZipFile(source) as archive:
                infos = [info for info in archive.infolist() if not info.is_dir()]
                if len(infos) > limits.max_members_per_archive:
                    warnings.append(f"member limit exceeded: {len(infos)}")
                    infos = infos[: limits.max_members_per_archive]
                total = 0
                for info in infos:
                    if info.file_size > limits.max_member_bytes:
                        warnings.append(f"member too large: {info.filename}")
                        continue
                    total += info.file_size
                    if total > limits.max_total_archive_bytes:
                        warnings.append("total uncompressed byte limit exceeded")
                        break
                    members.append((info.filename, archive.read(info)))
                return members, warnings

        source.seek(0)
        if tarfile.is_tarfile(source):
            with tarfile.open(fileobj=source, mode="r:*") as archive:
                infos = [info for info in archive.getmembers() if info.isfile()]
                if len(infos) > limits.max_members_per_archive:
                    warnings.append(f"member limit exceeded: {len(infos)}")
                    infos = infos[: limits.max_members_per_archive]
                total = 0
                for info in infos:
                    if info.size > limits.max_member_bytes:
                        warnings.append(f"member too large: {info.name}")
                        continue
                    total += info.size
                    if total > limits.max_total_archive_bytes:
                        warnings.append("total uncompressed byte limit exceeded")
                        break
                    extracted = archive.extractfile(info)
                    if extracted is not None:
                        members.append((info.name, extracted.read()))
                return members, warnings

        if name.lower().endswith(".gz"):
            uncompressed = gzip.decompress(payload)
            if len(uncompressed) > limits.max_member_bytes:
                return [], ["gzip member too large"]
            return [(Path(name).stem, uncompressed)], warnings
    except (OSError, EOFError, tarfile.TarError, zipfile.BadZipFile) as error:
        return [], [f"archive read failed: {error}"]
    return [], warnings


def scan_payload(
    source_path: str,
    member_path: str,
    payload: bytes,
    depth: int,
    limits: Limits,
    sample_limit: int,
    findings: list[dict],
    warnings: list[dict],
) -> None:
    occurrence_count, samples = text_occurrences(payload, sample_limit)
    if occurrence_count:
        findings.append(
            {
                "source_path": source_path,
                "member_path": member_path or None,
                "occurrence_count": occurrence_count,
                "samples": samples,
            }
        )

    if not is_archive(member_path or source_path, payload):
        return
    if depth >= limits.max_archive_depth:
        warnings.append({"source_path": source_path, "member_path": member_path or None, "warning": "archive depth limit exceeded"})
        return
    members, member_warnings = archive_members(member_path or source_path, payload, limits)
    for warning in member_warnings:
        warnings.append({"source_path": source_path, "member_path": member_path or None, "warning": warning})
    for name, member in members:
        nested_path = f"{member_path}!/{name}" if member_path else name
        scan_payload(source_path, nested_path, member, depth + 1, limits, sample_limit, findings, warnings)


def audit(root: Path, *, filesystem: bool, exclusions: tuple[str, ...], limits: Limits, sample_limit: int) -> dict:
    root = root.resolve()
    files = list(filesystem_files(root)) if filesystem else tracked_files(root)
    source_mode = "filesystem" if filesystem else "git_tracked"
    if files is None:
        files = list(filesystem_files(root))
        source_mode = "filesystem_fallback"

    findings: list[dict] = []
    warnings: list[dict] = []
    excluded: list[str] = []
    scanned_files = 0
    archive_sources = 0
    for path in sorted(files):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root).as_posix()
        if any(matches(relative, pattern) for pattern in exclusions):
            excluded.append(relative)
            continue
        try:
            payload = path.read_bytes()
        except OSError as error:
            warnings.append({"source_path": relative, "member_path": None, "warning": f"read failed: {error}"})
            continue
        scanned_files += 1
        if is_archive(relative, payload):
            archive_sources += 1
        scan_payload(relative, "", payload, 0, limits, sample_limit, findings, warnings)

    return {
        "schema_version": "ordo.ukrainian_text_audit.v1",
        "status": "findings" if findings else "clear",
        "source_mode": source_mode,
        "root": str(root),
        "excluded_globs": list(exclusions),
        "scanned_file_count": scanned_files,
        "excluded_file_count": len(excluded),
        "archive_source_count": archive_sources,
        "finding_count": len(findings),
        "warning_count": len(warnings),
        "findings": findings,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--filesystem", action="store_true", help="scan all physical files instead of Git-tracked payload")
    parser.add_argument("--include-book", action="store_true", help="include the intentionally localized book contour")
    parser.add_argument("--exclude-glob", action="append", default=[], help="additional repository-relative exclusion glob")
    parser.add_argument("--max-archive-depth", type=int, default=4)
    parser.add_argument("--max-members-per-archive", type=int, default=10_000)
    parser.add_argument("--max-member-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument("--max-total-archive-bytes", type=int, default=256 * 1024 * 1024)
    parser.add_argument("--sample-limit", type=int, default=3)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args(argv)
    if min(args.max_archive_depth, args.max_members_per_archive, args.max_member_bytes, args.max_total_archive_bytes, args.sample_limit) < 0:
        parser.error("limits must be non-negative")
    exclusions = tuple(args.exclude_glob) if args.include_book else DEFAULT_EXCLUSIONS + tuple(args.exclude_glob)
    result = audit(
        args.root,
        filesystem=args.filesystem,
        exclusions=exclusions,
        limits=Limits(args.max_archive_depth, args.max_members_per_archive, args.max_member_bytes, args.max_total_archive_bytes),
        sample_limit=args.sample_limit,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        output = args.out if args.out.is_absolute() else args.root.resolve() / args.out
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    if args.json:
        sys.stdout.write(payload)
    else:
        print(
            "ukrainian-text audit: "
            f"{result['status'].upper()} (files={result['scanned_file_count']}, "
            f"archives={result['archive_source_count']}, findings={result['finding_count']}, "
            f"warnings={result['warning_count']})"
        )
    return 1 if args.fail_on_findings and result["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
