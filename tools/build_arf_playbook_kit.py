from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "packages" / "arf_playbook_kit"
APF = ROOT / "packages" / "ordo_applied_project_factory"
GUIDES = KIT / "source"
VERSION = (KIT / "VERSION").read_text(encoding="utf-8").strip()
ARCHIVE_NAME = f"ORDO_ARF_PLAYBOOK_KIT_{VERSION}.zip"
ZIP_TIMESTAMP = (2026, 7, 23, 0, 0, 0)

ROOT_FILES = (
    "START_HERE_RUNTIME_MODE.md",
    "START_PROMPT_RUNTIME_MODE.md",
    "PLAYBOOK_LAWS.md",
    "ordo.runtime.json",
    "playbook_release.json",
    "question_registry.json",
)
COPY_TREES = (
    "source/modules",
    "cli_embedded",
    "integration",
    "output_templates",
)
COPY_FILES = (
    "source/program.ordo.yaml",
    "source/module_manifest.yaml",
    "source/assemble_modular_source.py",
    "tests/test_cases.yaml",
)
GUIDE_FILES = (
    "START_HERE.md",
    "START_PROMPT.md",
    "PLAYBOOK_LAWS.md",
    "PLAYBOOK_TEMPLATE.md",
    "PLAYBOOK_BRIEF.md",
    "TEST_AND_IMPROVE.md",
    "EXPECTED_DELIVERABLES.md",
    "ARF_PACKAGE_README.md",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def create_runtime_manifest(destination: Path) -> None:
    text = (APF / "ordo.yml").read_text(encoding="utf-8")
    lines = [
        line
        for line in text.splitlines()
        if not line.startswith(("generated_output_root:", "version_state:"))
    ]
    lines.extend(
        (
            "generated_output_root: workspace/generated",
            "arf_package_profile: standalone_chat_runtime",
        )
    )
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def assemble(stage: Path) -> None:
    for name in ROOT_FILES:
        copy_file(APF / name, stage / name)
    create_runtime_manifest(stage / "ordo.yml")

    for relative in COPY_TREES:
        shutil.copytree(APF / relative, stage / relative)
    for relative in COPY_FILES:
        copy_file(APF / relative, stage / relative)

    for name in GUIDE_FILES:
        copy_file(GUIDES / name, stage / "guides" / name)

    (stage / "workspace").mkdir()
    copy_file(GUIDES / "WORKSPACE_README.md", stage / "workspace" / "README.md")


def compile_runtime(stage: Path) -> None:
    environment = os.environ.copy()
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = str(ROOT / "cli") + (os.pathsep + existing if existing else "")
    result = subprocess.run(
        [sys.executable, "-m", "cli.ordo.cli", "compile", str(stage)],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(
            "ARF runtime compilation failed:\n"
            + result.stdout
            + result.stderr
        )
    normalize_compiled_runtime(stage)
    # Compilation leaves developer evidence in the staging package. The
    # shipped ARF retains its initialized session trace, but excludes reports
    # that are only meaningful for the temporary build environment.
    shutil.rmtree(stage / "reports", ignore_errors=True)


def normalize_compiled_runtime(stage: Path) -> None:
    """Make compiler metadata reproducible, then regenerate its targets.

    The generic compiler normally adds a timestamp and random canary on every
    invocation. A release artifact needs a stable, source-derived canary so a
    repeat build can be verified byte-for-byte while keeping the canary out of
    chat-facing runtime views.
    """
    ir_path = stage / "compiled" / "program.ir.json"
    ir = json.loads(ir_path.read_text(encoding="utf-8"))
    canary = "canary-" + hashlib.sha256(
        (stage / "source" / "program.ordo.yaml").read_bytes()
    ).hexdigest()[:32]
    ir["compiled_at"] = "2026-07-23T00:00:00+00:00"
    security = ir.get("security")
    if isinstance(security, dict):
        security["canary_secret"] = canary
    for operation in ir.get("ops", []):
        if isinstance(operation, dict) and operation.get("canary"):
            operation["question"] = canary
    ir_path.write_text(json.dumps(ir, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    sys.path.insert(0, str(ROOT / "cli"))
    from ordo.targets import emit_compiled_targets

    emit_compiled_targets(
        stage,
        ir_path=ir_path,
        source_path=stage / "source" / "program.ordo.yaml",
        runtime_view="ordo-code",
    )


def package_members(stage: Path) -> tuple[str, ...]:
    members = [
        path.relative_to(stage).as_posix()
        for path in sorted(stage.rglob("*"))
        if path.is_file() and path.relative_to(stage).as_posix() != "KIT_MANIFEST.json"
    ]
    # ZIP extraction preserves file write order. Put editable source before the
    # compiled representation so the runtime's freshness check sees IR as the
    # newest package-owned artifact after a user extracts the archive.
    return tuple(
        sorted(
            members,
            key=lambda name: (
                0 if name.startswith("source/") else 1 if name.startswith("compiled/") else 2,
                name,
            ),
        )
    )


def internal_manifest(stage: Path, members: tuple[str, ...]) -> dict:
    return {
        "schema_version": "ordo.arf_playbook_kit.v2",
        "kit": "ARF Playbook Kit",
        "package_kind": "standalone_arf_playbook_factory",
        "version": VERSION,
        "source_package": {
            "path": "packages/ordo_applied_project_factory",
            "name": "ordo.applied_project_factory",
            "version": "0.1.0-rc.1",
        },
        "workspace": "workspace/",
        "members": [
            {"path": name, "sha256": sha256(stage / name)}
            for name in members
        ],
    }


def write_zip(output: Path, stage: Path, manifest: dict) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in (*[entry["path"] for entry in manifest["members"]], "KIT_MANIFEST.json"):
            payload = manifest_bytes if name == "KIT_MANIFEST.json" else (stage / name).read_bytes()
            info = ZipInfo(name, date_time=ZIP_TIMESTAMP)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload, compress_type=ZIP_DEFLATED, compresslevel=9)


def build(output: Path) -> dict:
    with TemporaryDirectory(prefix="ordo-arf-kit-") as temporary_directory:
        stage = Path(temporary_directory) / "ORDO_ARF_PLAYBOOK_FACTORY"
        stage.mkdir()
        assemble(stage)
        compile_runtime(stage)
        members = package_members(stage)
        manifest = internal_manifest(stage, members)
        write_zip(output, stage, manifest)
    return {
        **manifest,
        "archive": output.name,
        "archive_sha256": sha256(output),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the standalone ARF Playbook Kit.")
    parser.add_argument("--out", type=Path, default=ROOT / "dist" / ARCHIVE_NAME)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    manifest = build(args.out)
    if args.manifest:
        args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
