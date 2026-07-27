from __future__ import annotations

import re
from pathlib import Path

from ordo.compiler import compile_source
from ordo.loader import load_yaml


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "FLOW.EDGE",
    "FLOW.JOIN.DEF",
    "SHARED.TAIL.DEF",
    "SHARED.TAIL.REFERENCE.RESOLVED",
}


def catalog_opcodes(path: Path) -> set[str]:
    pattern = re.compile(r"`([A-Z][A-Z0-9_]*(?:\.[A-Z0-9_]+)+)`")
    return set(pattern.findall(path.read_text(encoding="utf-8")))


def test_apf_lowering_opcodes_are_registered_in_both_catalogs() -> None:
    source = load_yaml(ROOT / "packages/ordo_applied_project_factory/source/program.ordo.yaml")
    emitted = {op["op"] for op in compile_source(source).get("ops", []) if op.get("op") in EXPECTED}
    canonical = catalog_opcodes(ROOT / "language/registry/OPCODE_CATALOG.md")
    embedded = catalog_opcodes(ROOT / "packages/ordo_applied_project_factory/cli_embedded/language/registry/OPCODE_CATALOG.md")
    assert emitted == EXPECTED
    assert EXPECTED <= canonical
    assert EXPECTED <= embedded


def test_reconciliation_document_declares_lowering_boundary() -> None:
    text = (ROOT / "packages/ordo_applied_project_factory/docs/APF_OPCODE_REGISTRY_RECONCILIATION.md").read_text(encoding="utf-8")
    for opcode in sorted(EXPECTED):
        assert f"`{opcode}`" in text
    assert "do not promote" in text
