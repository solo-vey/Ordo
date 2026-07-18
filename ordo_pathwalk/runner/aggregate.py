"""Aggregate scores across many PathWalk test cases into one summary.

Reads every *_score.json in a directory (produced by `ordo-pathwalk score
--out <dir>/<scenario_id>_score.json`) and computes overall statistics -
this is what turns individual test results into the "one number per model/
version" comparison the whole benchmark exists for.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any


def _load_scores(score_dir: Path) -> list[dict[str, Any]]:
    scores = []
    for path in sorted(score_dir.glob("*_score.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        data["_source_file"] = path.name
        scores.append(data)
    return scores


def aggregate(score_dir: Path) -> dict[str, Any]:
    scores = _load_scores(score_dir)
    if not scores:
        return {"status": "no_scores_found", "score_dir": str(score_dir)}

    total = len(scores)
    passed = [s for s in scores if s.get("gate_passed")]
    quality_values = [s["path_quality_score"] for s in scores if "path_quality_score" in s]

    summary: dict[str, Any] = {
        "status": "ok",
        "total_test_cases": total,
        "gate_pass_rate": round(len(passed) / total, 4),
        "path_quality_score": {
            "mean": round(statistics.mean(quality_values), 4) if quality_values else None,
            "median": round(statistics.median(quality_values), 4) if quality_values else None,
            "stdev": round(statistics.stdev(quality_values), 4) if len(quality_values) > 1 else 0.0,
            "min": round(min(quality_values), 4) if quality_values else None,
            "max": round(max(quality_values), 4) if quality_values else None,
        },
        "failed_test_cases": [
            {
                "file": s["_source_file"],
                "partial_cell_match_rate": (s.get("diagnostic_only") or {}).get("partial_cell_match_rate"),
                "last_recorded_node": (s.get("diagnostic_only") or {}).get("last_recorded_node"),
            }
            for s in scores if not s.get("gate_passed")
        ],
    }

    # Optional breakdowns by driver / cli_mode / runtime_view.
    for field in ("driver", "cli_mode", "runtime_view"):
        by_tag: dict[str, list[float]] = {}
        for s in scores:
            tag = s.get(field)
            if tag and "path_quality_score" in s:
                by_tag.setdefault(str(tag), []).append(s["path_quality_score"])
        if by_tag:
            summary[f"breakdown_by_{field}"] = {
                tag: {"count": len(vals), "mean": round(statistics.mean(vals), 4)}
                for tag, vals in by_tag.items()
            }

    # Preserve the runtime protocol versions that were actually measured.
    protocol_versions = sorted({
        str((s.get("runtime_metadata") or {}).get("runtime_protocol_version"))
        for s in scores if (s.get("runtime_metadata") or {}).get("runtime_protocol_version")
    })
    if protocol_versions:
        summary["runtime_protocol_versions"] = protocol_versions

    return summary


def render_markdown(summary: dict[str, Any]) -> str:
    if summary.get("status") != "ok":
        return f"# PathWalk benchmark summary\n\nNo scores found in {summary.get('score_dir')}.\n"
    pqs = summary["path_quality_score"]
    lines = [
        "# PathWalk benchmark summary",
        "",
        f"- Test cases: **{summary['total_test_cases']}**",
        f"- Gate pass rate: **{summary['gate_pass_rate'] * 100:.1f}%**",
        f"- path_quality_score: mean **{pqs['mean']}**, median {pqs['median']}, "
        f"stdev {pqs['stdev']}, range [{pqs['min']}, {pqs['max']}]",
        "",
    ]
    for key, title in [("breakdown_by_driver", "driver"), ("breakdown_by_cli_mode", "cli_mode"), ("breakdown_by_runtime_view", "runtime_view")]:
        if summary.get(key):
            lines.append(f"## Breakdown by {title}")
            lines.append("")
            lines.append(f"| {title} | count | mean path_quality_score |")
            lines.append("|---|---|---|")
            for tag, stats in summary[key].items():
                lines.append(f"| {tag} | {stats['count']} | {stats['mean']} |")
            lines.append("")
    if summary.get("failed_test_cases"):
        lines.append(f"## Failed test cases ({len(summary['failed_test_cases'])})")
        lines.append("")
        lines.append("| file | partial_cell_match_rate | last_recorded_node |")
        lines.append("|---|---|---|")
        for f in summary["failed_test_cases"]:
            lines.append(f"| {f['file']} | {f['partial_cell_match_rate']} | {f['last_recorded_node']} |")
        lines.append("")
    return "\n".join(lines)
