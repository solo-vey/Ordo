from __future__ import annotations

APF_LINT_MAX_RSS_MIB = 512
APF_LINT_MAX_SECONDS = 15.0
SYNTHETIC_GRAPH_MAX_SECONDS = 10.0

def budget_profile() -> dict[str, float | int | str | bool]:
    return {
        "profile": "standard_ci",
        "apf_lint_max_rss_mib": APF_LINT_MAX_RSS_MIB,
        "apf_lint_max_seconds": APF_LINT_MAX_SECONDS,
        "synthetic_graph_max_seconds": SYNTHETIC_GRAPH_MAX_SECONDS,
        "skip_heavy_allowed": False,
    }
