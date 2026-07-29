from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[2]
EDITOR = ROOT / "utilities" / "ordo_tree_editor"
VERSION = (EDITOR / "VERSION").read_text(encoding="utf-8").strip()
ARCHIVE_NAME = f"ORDO_TREE_EDITOR_{VERSION}.zip"
ZIP_TIMESTAMP = (2026, 7, 29, 0, 0, 0)


def _copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".DS_Store"))


def build(output: Path) -> dict[str, str | int]:
    with TemporaryDirectory(prefix="ordo-tree-editor-") as temporary_directory:
        stage = Path(temporary_directory) / "ORDO_TREE_EDITOR"
        _copy_tree(EDITOR, stage / "utilities" / "ordo_tree_editor")
        _copy_tree(ROOT / "cli" / "ordo", stage / "cli" / "ordo")
        members = sorted(path for path in stage.rglob("*") if path.is_file())
        output.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for path in members:
                info = ZipInfo(path.relative_to(stage).as_posix(), date_time=ZIP_TIMESTAMP)
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)
    return {"archive": output.name, "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "bytes": output.stat().st_size}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic Ordo Tree Editor source distribution.")
    parser.add_argument("--out", type=Path, default=ROOT / "dist" / ARCHIVE_NAME)
    args = parser.parse_args(argv)
    print(build(args.out.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
