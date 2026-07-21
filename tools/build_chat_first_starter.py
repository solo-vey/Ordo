from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / "examples/chat_first_playbook_starter"
SOURCE = STARTER / "source"
DEFAULT_OUTPUT = STARTER / "ORDO_CHAT_FIRST_PLAYBOOK_STARTER.zip"
MEMBERS = (
    "EXPECTED_DELIVERABLES.md",
    "PLAYBOOK_BRIEF.md",
    "START_PROMPT.md",
    "TEST_AND_IMPROVE.md",
)


def build(output: Path) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in MEMBERS:
            payload = (SOURCE / name).read_bytes()
            info = ZipInfo(name, date_time=(2026, 7, 21, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload, compress_type=ZIP_DEFLATED, compresslevel=9)
    return {
        "schema_version": "ordo.chat_first_starter_manifest.v1",
        "archive": output.name,
        "archive_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "members": [
            {
                "path": name,
                "sha256": hashlib.sha256((SOURCE / name).read_bytes()).hexdigest(),
            }
            for name in MEMBERS
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    manifest = build(args.out)
    if args.manifest:
        args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
