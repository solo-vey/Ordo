from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import alpha20_runtime as rt


def _row(tc_id, expected_state):
    return {
        "tc_id": tc_id,
        "scenario": "scenario",
        "short_input": "input",
        "expected_result": "result",
        "expected_state": expected_state,
        "covers": ["null_empty"],
    }


def test_kf023_duplicate_append_rejected_and_merge_row_updates_existing_test():
    state = {"unit_test_catalog": {"rows": [_row("UT_003", "no_data"), _row("UT_009", "error")]}}
    duplicate = {
        "base_revision": 21,
        "operations": [
            {"op": "append", "path": "unit_test_catalog.rows", "value": _row("UT_003", "absent"), "basis": "recovery"}
        ],
    }
    _, rejected = rt.apply_state_patch_atomic(
        state,
        duplicate,
        allowed_paths=["unit_test_catalog.rows"],
        current_revision=21,
    )
    assert rejected["committed"] is False
    assert any("duplicate tc_id" in e and "merge_row" in e for e in rejected["errors"])

    repair = {
        "base_revision": 21,
        "operations": [
            {
                "op": "merge_row",
                "path": "unit_test_catalog.rows",
                "row_key": "tc_id",
                "row_match": "UT_003",
                "value": {"expected_state": "absent", "expected_result": "Ризик-фактор визначено як відсутній"},
                "basis": "recovery",
            },
            {
                "op": "merge_row",
                "path": "unit_test_catalog.rows",
                "row_key": "tc_id",
                "row_match": "UT_009",
                "value": {"expected_state": "unchanged", "expected_result": "Попередній валідний стан зберігається"},
                "basis": "recovery",
            },
        ],
    }
    updated, committed = rt.apply_state_patch_atomic(
        state,
        repair,
        allowed_paths=["unit_test_catalog.rows"],
        current_revision=21,
    )
    assert committed["committed"] is True
    rows = updated["unit_test_catalog"]["rows"]
    assert len(rows) == 2
    by_id = {r["tc_id"]: r for r in rows}
    assert by_id["UT_003"]["expected_state"] == "absent"
    assert by_id["UT_009"]["expected_state"] == "unchanged"
