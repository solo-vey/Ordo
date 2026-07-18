from pathlib import Path
import hashlib
import json
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "generated_artifacts_policy.yaml"
policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))["generated_artifacts"]

allowed = set(policy.get("allowed_source_placeholders", []))
roots = tuple(policy.get("package_generated_roots", []))
violations = []

# Package source trees: generated payload roots must be empty except explicit placeholders.
packages_root = ROOT / "packages"
if packages_root.exists():
    for pkg in sorted(packages_root.iterdir()):
        if not pkg.is_dir():
            continue
        for root_name in roots:
            directory = pkg / root_name
            if not directory.exists():
                continue
            for file_path in directory.rglob("*"):
                if not file_path.is_file():
                    continue
                rel_pkg = file_path.relative_to(pkg).as_posix()
                if file_path.name == ".gitkeep" or rel_pkg in allowed:
                    continue
                violations.append({"type": "package_generated_payload", "path": file_path.relative_to(ROOT).as_posix()})

# Workspace reports: only explicitly manifested canonical historical records may remain.
workspace_reports = policy.get("workspace_reports", {})
manifest_rel = workspace_reports.get("canonical_manifest")
if manifest_rel:
    manifest_path = ROOT / manifest_rel
    if not manifest_path.is_file():
        violations.append({"type": "missing_canonical_reports_manifest", "path": manifest_rel})
    else:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        reports_root = ROOT / manifest.get("reports_root", "reports")
        entries = manifest.get("entries", [])
        declared = {}
        for entry in entries:
            rel = entry.get("path")
            digest = entry.get("sha256")
            if not rel or not digest:
                violations.append({"type": "invalid_manifest_entry", "entry": entry})
                continue
            if rel in declared:
                violations.append({"type": "duplicate_manifest_entry", "path": rel})
            declared[rel] = digest
            candidate = reports_root / rel
            try:
                candidate.resolve().relative_to(reports_root.resolve())
            except ValueError:
                violations.append({"type": "report_path_escape", "path": rel})
                continue
            if not candidate.is_file():
                violations.append({"type": "missing_canonical_report", "path": rel})
                continue
            actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual != digest:
                violations.append({"type": "canonical_report_checksum_mismatch", "path": rel, "expected": digest, "actual": actual})

        if reports_root.exists():
            for file_path in reports_root.rglob("*"):
                if not file_path.is_file() or file_path.resolve() == manifest_path.resolve():
                    continue
                rel = file_path.relative_to(reports_root).as_posix()
                if rel not in declared:
                    violations.append({"type": "unmanifested_workspace_report", "path": f"reports/{rel}"})

report = {
    "schema_version": "ordo.generated_artifact_isolation.report.v2",
    "status": "passed" if not violations else "failed",
    "violations": violations,
}
print(json.dumps(report, indent=2))
sys.exit(0 if not violations else 1)
