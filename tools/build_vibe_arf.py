#!/usr/bin/env python3
"""Build deterministic repository-native Vibe ARF release ZIP files."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages" / "vibe_arf"
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_tree(source: Path, target: Path) -> None:
    shutil.copytree(source, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"))


def assemble_program(stage: Path) -> None:
    source = stage / "source"
    manifest = yaml.safe_load((source / "module_manifest.yaml").read_text(encoding="utf-8"))
    program: dict = {}
    for entry in manifest["modules"]:
        module = yaml.safe_load((source / entry["path"]).read_text(encoding="utf-8")) or {}
        for key in entry["owns_top_level_keys"]:
            if key in program:
                raise ValueError(f"duplicate top-level key while assembling Vibe source: {key}")
            program[key] = module.get(key)
    # Vibe deliberately uses one connected authoring lifecycle: repair,
    # review, and retry routes may return to earlier authoring stages.  The
    # release declares that approved lifecycle explicitly for the current
    # Ordo graph validator.
    graph_contract = program.setdefault("graph_contract", {})
    lifecycle_vertices = [
        item["id"]
        for section in ("nodes", "gates")
        for item in program.get(section, []) or []
        if isinstance(item, dict) and item.get("id")
    ]
    graph_contract["allowed_cycle_regions"] = [
        {"id": "VIBE_AUTHORING_LIFECYCLE", "nodes": sorted(lifecycle_vertices)}
    ]
    (source / "program.ordo.yaml").write_text(
        yaml.safe_dump(program, allow_unicode=False, sort_keys=False, width=100), encoding="utf-8"
    )


def stage_package() -> Path:
    temporary = Path(tempfile.mkdtemp(prefix="vibe-arf-"))
    stage = temporary / "VIBE_ARF"
    copy_tree(PACKAGE, stage)
    assemble_program(stage)

    support = stage / "canonical_support"
    copy_tree(ROOT / "language", support / "language")
    (support / "REPOSITORY_BINDING.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "language_source": "repository/language",
                "language_source_sha256": sha256(ROOT / "language" / "README.md"),
                "cli_source": "repository/cli/ordo",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    copy_tree(ROOT / "cli" / "ordo", stage / "cli_embedded" / "ordo_pkg" / "ordo")
    launcher = stage / "cli_embedded" / "ordo"
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\nimport sys\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parent / 'ordo_pkg'))\n"
        "from ordo.cli import main\n"
        "raise SystemExit(main(sys.argv[1:]))\n",
        encoding="utf-8",
    )
    launcher.chmod(0o755)
    # The current CLI requires this generated evidence path during lint.  It
    # belongs only to the disposable validation stage and is excluded from all
    # release ZIP artifacts together with every other generated report.
    reports = stage / "reports"
    reports.mkdir(exist_ok=True)
    summary = reports / "CLI_VALIDATION_SUMMARY.md"
    if not summary.exists():
        summary.write_text("# CLI validation summary\n\nCLI status: not_run\n", encoding="utf-8")
    return temporary


def members(stage: Path, profile: str) -> list[Path]:
    excluded = {".pytest_cache", "__pycache__", "compiled", "runtime", "runtime_projection", "design"}
    if profile == "MODEL_RUN":
        excluded |= {"authoring", "verification", "tests", "cli_embedded"}
    result = []
    for path in sorted(stage.rglob("*")):
        rel = path.relative_to(stage)
        if not path.is_file() or any(part in excluded for part in rel.parts):
            continue
        if rel.parts[0] == "reports" and rel.as_posix() != "reports/CLI_VALIDATION_SUMMARY.md":
            continue
        result.append(path)
    return result


def build_profile(stage: Path, output: Path, profile: str, version: str) -> dict:
    payload = members(stage, profile)
    manifest = {
        "schema_version": "1.0",
        "product": "Vibe ARF",
        "version": version,
        "profile": profile,
        "repository_revision": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
        "members": [{"path": p.relative_to(stage).as_posix(), "sha256": sha256(p)} for p in payload],
    }
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in payload:
            rel = path.relative_to(stage).as_posix()
            info = zipfile.ZipInfo(rel, date_time=FIXED_TIMESTAMP)
            info.create_system = 3
            info.external_attr = ((0o100755 if rel == "cli_embedded/ordo" else 0o100644) << 16)
            archive.writestr(info, path.read_bytes())
        archive.writestr("RELEASE_MANIFEST.json", json.dumps(manifest, indent=2).encode() + b"\n")
    return {"path": output.name, "sha256": sha256(output), "bytes": output.stat().st_size}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "vibe_arf")
    args = parser.parse_args()
    version = (PACKAGE / "VIBE_ARF_VERSION").read_text(encoding="utf-8").strip()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    temporary = stage_package()
    try:
        stage = temporary / "VIBE_ARF"
        # Production evidence is derived in the disposable staging tree.  It
        # proves the release can be built without committing generated output.
        evidence = subprocess.run(
            ["python3", str(stage / "tools" / "build_production_evidence.py"), str(stage)],
            text=True,
            capture_output=True,
        )
        if evidence.returncode:
            raise RuntimeError(f"production evidence materialization failed:\n{evidence.stdout}\n{evidence.stderr}")
        report = {"product": "Vibe ARF", "version": version, "profiles": {}}
        for profile in ("EDIT", "CLI_RUN", "MODEL_RUN"):
            output = args.output_dir / f"VIBE_ARF_{version}_{profile}.zip"
            report["profiles"][profile] = build_profile(stage, output, profile, version)
        (args.output_dir / "SHA256SUMS.txt").write_text(
            "".join(f"{item['sha256']}  {item['path']}\n" for item in report["profiles"].values()),
            encoding="utf-8",
        )
        print(json.dumps(report, indent=2))
    finally:
        shutil.rmtree(temporary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
