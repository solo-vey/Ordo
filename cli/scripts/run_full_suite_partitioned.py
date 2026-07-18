from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "tests"
REPORT = ROOT.parent / "reports" / "FULL_TEST_SUITE_PARTITIONED_REPORT.json"


def main() -> int:
    files = sorted(TEST_DIR.glob("test_*.py"))
    results = []
    total_passed = total_failed = 0
    started = time.time()
    for path in files:
        t0 = time.time()
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        results.append({
            "file": path.name,
            "exit_code": proc.returncode,
            "duration_seconds": round(time.time() - t0, 3),
            "output_tail": out[-4000:],
        })
        if proc.returncode == 0:
            total_passed += 1
            print(f"PASS {path.name}")
        else:
            total_failed += 1
            print(f"FAIL {path.name}")
    payload = {
        "schema_version": "ordo.test.partitioned_report.v1",
        "status": "passed" if total_failed == 0 else "failed",
        "test_files_total": len(files),
        "test_files_passed": total_passed,
        "test_files_failed": total_failed,
        "duration_seconds": round(time.time() - started, 3),
        "results": results,
    }
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"report: {REPORT}")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
