from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "packages" / "arf_playbook_kit"
SOURCE = KIT / "source"
VERSION = (KIT / "VERSION").read_text(encoding="utf-8").strip()
ARCHIVE_NAME = f"ORDO_ARF_PLAYBOOK_KIT_{VERSION}.zip"
MEMBERS = (
    "START_HERE.md",
    "START_PROMPT.md",
    "PLAYBOOK_LAWS.md",
    "PLAYBOOK_TEMPLATE.md",
    "PLAYBOOK_BRIEF.md",
    "TEST_AND_IMPROVE.md",
    "EXPECTED_DELIVERABLES.md",
)
ZIP_TIMESTAMP = (2026, 7, 23, 0, 0, 0)


def source_manifest() -> dict:
    return {
        "schema_version": "ordo.arf_playbook_kit.v1",
        "kit": "ARF Playbook Kit",
        "version": VERSION,
        "members": [
            {
                "path": name,
                "sha256": hashlib.sha256((SOURCE / name).read_bytes()).hexdigest(),
            }
            for name in MEMBERS
        ],
    }


def build(output: Path) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    internal_manifest = json.dumps(source_manifest(), indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in (*MEMBERS, "KIT_MANIFEST.json"):
            payload = internal_manifest if name == "KIT_MANIFEST.json" else (SOURCE / name).read_bytes()
            info = ZipInfo(name, date_time=ZIP_TIMESTAMP)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload, compress_type=ZIP_DEFLATED, compresslevel=9)
    return {
        **source_manifest(),
        "archive": output.name,
        "archive_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
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
