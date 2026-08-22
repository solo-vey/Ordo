#!/usr/bin/env python3
"""Replace non-English Vibe node prompts with English contract-derived prompts.

The Vibe source keeps an English ``description`` for every node.  This utility
uses that normative responsibility plus the node's declared machine contracts
to produce English execution instructions without changing IDs, state writes,
transitions, or validation fields.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


UKRAINIAN = re.compile(r"[А-Яа-яІіЇїЄєҐґ]")


def english_prompt(node: dict) -> str:
    if node.get("id") == "N_VIBE_INTAKE":
        return (
            "Describe in your own words what the future playbook must do and "
            "which outputs you need. Add example results, templates, input "
            "documents, or legacy instructions when available. The system will "
            "design the process and ask you only for a decision that belongs to you."
        )
    responsibility = str(node.get("description") or "the declared node responsibility").strip()
    return (
        "Execute this node's declared responsibility exactly. Preserve the "
        "declared state, evidence, authority, tool, output, and transition "
        f"contracts. Responsibility: {responsibility}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("module", type=Path)
    args = parser.parse_args()
    data = yaml.safe_load(args.module.read_text(encoding="utf-8"))
    changed = 0
    for node in data.get("nodes", []):
        if UKRAINIAN.search(str(node.get("question", ""))):
            node["question"] = english_prompt(node)
            changed += 1
    args.module.write_text(
        yaml.safe_dump(data, allow_unicode=False, sort_keys=False, width=100),
        encoding="utf-8",
    )
    print(f"English-rebased {changed} Vibe node prompts: {args.module}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
