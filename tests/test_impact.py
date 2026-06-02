"""Impact Analysis node tests — economic + organizational impact -> routing.

    python -m pytest tests/ -q
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.analyst_agent import analyze
from agents.impact_agent import assess


CRACK = {
    "incidentId": "IR-TEST-CRACK",
    "source": {"type": "vision", "name": "solvision", "detectorConfidence": 0.93},
    "severity": "high",
    "subject": "FAIL_CRACK: weld crack on load-bearing structural support",
    "description": "SolVision flagged a crack at weld seam 3 of a structural support.",
    "affectedItems": [{"itemId": "STR-SUP-7", "itemType": "assembly", "quantity": 1}],
    "complianceClass": "as9100",
    "tags": ["structural", "crack", "weld"],
}

COSMETIC = {
    "incidentId": "IR-TEST-COSMETIC",
    "source": {"type": "vision", "name": "solvision", "detectorConfidence": 0.96},
    "severity": "low",
    "subject": "FAIL_SCRATCH: shallow cosmetic scratch on plastic cover",
    "description": "Shallow cosmetic scratch on a plastic enclosure cover. Surface finish only.",
    "affectedItems": [{"itemId": "COV-1", "itemType": "part", "quantity": 1}],
    "complianceClass": "",
    "tags": ["cosmetic", "scratch"],
}


def test_high_impact_crack_escalates_to_action_center():
    disp, _ = analyze(CRACK)
    imp = assess(CRACK, disp)
    assert imp["route"] == "ACTION_CENTER"
    assert imp["hitlRequired"] is True
    assert imp["safetyCritical"] is True
    assert imp["economicImpactScore"] >= 0.40
    assert "Safety Officer" in imp["rolesEngaged"]


def test_low_impact_cosmetic_is_auto_resolved():
    disp, _ = analyze(COSMETIC)
    imp = assess(COSMETIC, disp)
    assert imp["route"] == "AUTONOMOUS"
    assert imp["hitlRequired"] is False
    assert imp["safetyCritical"] is False


def test_economic_score_is_bounded_and_breaks_down():
    disp, _ = analyze(CRACK)
    imp = assess(CRACK, disp)
    assert 0.0 <= imp["economicImpactScore"] <= 1.0
    b = imp["costBreakdownUsd"]
    assert round(b["repair"] + b["downtime"] + b["inactionRisk"], 2) == imp["estimatedCostUsd"]


def test_non_structural_does_not_trip_safety_cue():
    # Word-boundary matching: "non-structural" must NOT be read as "structural".
    inc = dict(COSMETIC, subject="cosmetic scratch on non-structural trim",
               description="surface scratch on a non-structural trim piece")
    disp, _ = analyze(inc)
    imp = assess(inc, disp)
    assert imp["safetyCritical"] is False


if __name__ == "__main__":
    test_high_impact_crack_escalates_to_action_center()
    test_low_impact_cosmetic_is_auto_resolved()
    test_economic_score_is_bounded_and_breaks_down()
    test_non_structural_does_not_trip_safety_cue()
    print("all impact tests passed")
