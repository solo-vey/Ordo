import json
from pathlib import Path

import pytest

from ordo_pathwalk.runner.calibration import calibration_eligibility, load_profile, validate_profile

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "ordo_pathwalk" / "calibration_profile.json"


def test_profile_is_valid_and_release_qa_primary():
    profile = load_profile(PROFILE)
    assert profile["primary_purpose"] == "ordo_release_qa"
    assert profile["weight_status"] == "locked_pending_eligible_real_model_dataset"


def test_current_small_pilot_is_not_calibration_eligible():
    profile = load_profile(PROFILE)
    result = calibration_eligibility({
        "model_versions": 1,
        "min_runs_per_model": 1,
        "scored_cases": 3,
        "nonperfect_completed_cases": 2,
        "hard_or_protocol_failures": 1,
        "weighted_components_with_nonzero_variance": 2,
        "manual_failure_adjudication_complete": False,
        "uncertainty_summary_complete": False,
    }, profile)
    assert result["eligible"] is False
    assert result["decision"] == "weights_locked"


def test_eligible_real_dataset_unlocks_calibration():
    profile = load_profile(PROFILE)
    result = calibration_eligibility({
        "model_versions": 3,
        "min_runs_per_model": 2,
        "scored_cases": 120,
        "nonperfect_completed_cases": 30,
        "hard_or_protocol_failures": 12,
        "weighted_components_with_nonzero_variance": 4,
        "manual_failure_adjudication_complete": True,
        "uncertainty_summary_complete": True,
    }, profile)
    assert result["eligible"] is True


def test_profile_rejects_softened_protocol_gate():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    profile["hard_gates"]["per_case_protocol_compliance_rate"] = 0.9
    with pytest.raises(ValueError):
        validate_profile(profile)
