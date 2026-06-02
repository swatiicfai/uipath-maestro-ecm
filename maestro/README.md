# Maestro process — `FieldIncidentTriage`

A UiPath Maestro (BPMN 2.0) process for the **Change Trigger** lane of the
field-inspection incident lifecycle. It is the live, drawable counterpart of
`run_pipeline.py`'s triage stage: an incident is captured, scored by the Vision
AI Analyst, reviewed, then routed — high-risk / low-confidence cases escalate to
the **Incident Review Board via Action Center (HITL)**; the rest take the
**Fast-Track autonomous** path.

```
Field Incident Captured              (e.g. Solomon SolVision defect FAIL)
  → AI Triage & Risk Score           (service — agents/analyst_agent.py)
  → Reproduce Incident
  → Analyze Root Cause
  → Incident Review
  → Impact Analysis                  (service — agents/impact_agent.py)
        economic (repair + downtime + inaction risk) + organizational
        (rolesEngaged / orgScope / safetyCritical) -> hitlRequired
  → ◇ HITL Required?                 (routes on IMPACT, not risk alone)
        ├─ true  → Escalate to Review Board (Action Center)  → Escalated
        └─ else  → Fast-Track Auto-Resolve                   → Auto-Resolved
```

Routing rule: `hitlRequired = analyst-flagged OR economicImpactScore ≥ 0.40 OR
safetyCritical OR orgScope = FLEET_WIDE`. A costly / safety-critical / fleet-wide
defect escalates to a human review board; a cheap, contained one auto-resolves.

This is the Physical AI framing of Figure 12 (CM II Based ECM), Change Trigger
swimlane. Source figure: `docs/figure12-source/`.

## Files

| File | Purpose |
|---|---|
| `FieldIncidentTriage/content/FieldIncidentTriage.bpmn` | the diagram — standard BPMN 2.0 + `uipath:` extensions, with `bpmndi` layout |
| `FieldIncidentTriage/entry-points.json` | start-event → entry-point GUID mapping (Studio Web project metadata) |

## Open it in Studio Web

The `.bpmn` is the exact format UiPath Studio Web reads/writes for Maestro
processes (verified against real exported processes). Two ways to get it in:

1. **Git source control** — connect the Studio Web project to this repo and pull;
   the process appears under the project.
2. **New process, then paste/replace** — create a new Maestro process in Studio
   Web and replace the generated `.bpmn` with this one (same `content/` path).

## What still needs wiring inside Studio Web

The diagram renders and routes as-is. To make it *executable*, bind the nodes to
real tenant resources (these can't be hand-authored reliably):

- **AI Triage** service task → the published Analyst activity/agent.
- **Escalate to Review Board** → a real **Action Center** action (External /
  QuickForm) — see issue #8.
- **Dequeue** → wire the `IncidentReports` queue (live: Shared folder, id 16639)
  as the trigger source so each queue item runs this process.
