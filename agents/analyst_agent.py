"""Vision AI Analyst — the agentic classification + risk task node.

Implements the contract declared in `artifacts/container1/agent_analyst.yaml`:
given a canonical IncidentReport, it returns a structured disposition payload
(category, riskScore, confidence, hitlRequired, reasoning, suggestedAction).

In a UiPath deployment this runs as an Agent Builder agent invoked by the Maestro
BPMN gateway. Here it runs as a plain task node so the pipeline is runnable and
testable locally. The Safety Risk math is identical to the BPMN gateway rules
(`samples/simulate_gateway.py`) regardless of which provider answers.
"""
from agents.llm_provider import complete_json

CATEGORIES = ["STRUCTURAL_DEFECT", "WIRING_FAULT", "COMMODITY_VARIANCE", "OPERATIONAL_RISK"]
ACTIONS = ["REWORK", "SCRAP", "AUDIT", "HOLD", "PROCEED"]

# HITL fires if risk crosses this OR classification confidence drops below 0.70.
RISK_HITL_THRESHOLD = 0.15
CONFIDENCE_HITL_THRESHOLD = 0.70

SYSTEM_PROMPT = """You are the Vision AI Analyst, an autonomous agent inside UiPath Agent Builder.
Ingest the IncidentReport JSON and return ONLY a JSON object with these keys:
incidentId, category, riskScore, confidence, hitlRequired, reasoning, suggestedAction.

Rules:
- category is one of STRUCTURAL_DEFECT, WIRING_FAULT, COMMODITY_VARIANCE, OPERATIONAL_RISK.
- riskScore: baseline 0.05; +0.50 critical / +0.25 high / +0.10 medium severity;
  +0.15 if detectorConfidence < 0.8; x1.5 if complianceClass is AS9100 or ISO13485; clamp 0..1.
- confidence is your 0..1 confidence in the classification.
- hitlRequired is true if riskScore >= 0.15 OR confidence < 0.70.
- suggestedAction is one of REWORK, SCRAP, AUDIT, HOLD, PROCEED.
- Never echo tenant URLs or credentials."""


def _score_offline(incident):
    """Deterministic mirror of the BPMN gateway — used when no LLM key is set."""
    risk = 0.05
    risk += {"critical": 0.50, "high": 0.25, "medium": 0.10}.get(
        incident.get("severity", "low").lower(), 0.0
    )
    if incident.get("source", {}).get("detectorConfidence", 1.0) < 0.8:
        risk += 0.15
    if incident.get("complianceClass", "").lower() in ("as9100", "iso13485"):
        risk *= 1.5
    risk = min(max(risk, 0.0), 1.0)

    blob = (incident.get("subject", "") + " " + incident.get("description", "")).lower()
    if "wiring" in blob or "cable" in blob:
        category = "WIRING_FAULT"
    elif any(w in blob for w in ("structural", "crack", "defect", "fracture")):
        category = "STRUCTURAL_DEFECT"
    elif any(w in blob for w in ("commodity", "price", "market", "supplier cost")):
        category = "COMMODITY_VARIANCE"
    else:
        category = "OPERATIONAL_RISK"

    confidence = 0.92 if incident.get("source", {}).get("detectorConfidence", 1.0) >= 0.8 else 0.65
    action = {
        "WIRING_FAULT": "REWORK",
        "STRUCTURAL_DEFECT": "HOLD" if risk >= 0.5 else "REWORK",
        "COMMODITY_VARIANCE": "AUDIT",
        "OPERATIONAL_RISK": "PROCEED",
    }[category]

    return {
        "incidentId": incident.get("incidentId"),
        "category": category,
        "riskScore": round(risk, 3),
        "confidence": confidence,
        "hitlRequired": risk >= RISK_HITL_THRESHOLD or confidence < CONFIDENCE_HITL_THRESHOLD,
        "reasoning": f"Rule-based disposition: {category} at risk {round(risk, 3)} "
        f"(severity={incident.get('severity')}, compliance={incident.get('complianceClass', 'n/a')}).",
        "suggestedAction": action,
    }


def _validate(result, incident):
    """Coerce/guard LLM output so a downstream BPMN node always gets a clean payload."""
    result.setdefault("incidentId", incident.get("incidentId"))
    if result.get("category") not in CATEGORIES:
        result["category"] = "OPERATIONAL_RISK"
    if result.get("suggestedAction") not in ACTIONS:
        result["suggestedAction"] = "AUDIT"
    result["riskScore"] = min(max(float(result.get("riskScore", 0.0)), 0.0), 1.0)
    result["confidence"] = min(max(float(result.get("confidence", 0.0)), 0.0), 1.0)
    # The gateway is authoritative: recompute hitlRequired from the numbers, never trust the model.
    result["hitlRequired"] = (
        result["riskScore"] >= RISK_HITL_THRESHOLD
        or result["confidence"] < CONFIDENCE_HITL_THRESHOLD
    )
    return result


def analyze(incident):
    """Run the analyst task node. Returns (disposition_dict, provider_label)."""
    result, provider = complete_json(SYSTEM_PROMPT, incident, _score_offline)
    return _validate(result, incident), provider
