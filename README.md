# uipath-maestro-ecm — Training Fleet & Cloud Resource Manager on UiPath Maestro

> [!IMPORTANT]
> ### 🏆 GRAND PRIZE POOL: $48,000 USD!
> **Grand Prize:** $8,000 USD Cash + Global UiPath Recognition! Let's automate the enterprise with fütüristik AI Orchestration! 🤖💼


[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

> An open-source framework for running a **cloud-GPU orchestrator and humanoid RL training lifecycle manager** as an **agentic, human-in-the-loop (HITL) orchestration** on **UiPath Maestro BPMN** — combining UiPath's two signature strengths: **agentic AI** (Agent Builder decisioning) and **RPA** (robots that provision cloud GPUs and execute into back-office systems).

Training neural skills (walking, running, grasping) for bipedal humanoid robots (like the Unitree G1) in reinforcement-learning simulation is compute-heavy and expensive. Teams burn thousands of dollars on cloud GPUs (AWS, GCP, AMD Developer Cloud) that sit **idle**, or on RL runs that **silently diverge or collapse** for hours before anyone notices. This project orchestrates the whole training lifecycle — from a researcher's training request, to cost-optimal GPU provisioning, to live anomaly detection that kills wasted runs, to human-approved checkpoint registration — as a **BPMN process where AI agents do the analysis and humans approve the critical cost and physics-safety gates.**

## Where this fits — the humanoid-robot stack

| Stage | Project | Role |
|---|---|---|
| **Deploy** | [`gcp`](https://github.com/Forenly/gcp) | Pick the right robot for a task + plan the install |
| **Operate** | [`gemini-xprize`](https://github.com/Forenly/gemini-xprize) — FleetMind | Run the autonomous day-to-day ops loop |
| **Govern** | **`uipath-maestro` (this repo)** | **Manage training runs + cloud GPU budget with human-approved gates** (the governance / HITL layer) |
| **Respond** | [`protocol-sift-dfir`](https://github.com/Forenly/protocol-sift-dfir) | Forensics when a unit is compromised |

Reference workload across all four: **Unitree G1-class** humanoid RL skills trained in MuJoCo.

## The two UiPath pillars (what we lean on)

- **Agentic** — the decisioning runs as **UiPath Agent Builder** agents: a **Telemetry Analyst** (classify the anomaly + Anomaly Risk score), a **Cost & Impact Agent** (cloud-GPU economic + organizational impact → routing), and a compliance-summary agent. They reason over each training-run anomaly and decide *fast-track vs human review*.
- **RPA** — once an action is approved, a **UiPath RPA robot** executes it into systems that have **no clean API**: cloud-provider consoles, the billing/quota dashboards, the model registry, and SSH-driven container control — driven through the UI when needed, plus API Workflows where an API exists.

## What it does

- **8 process containers** modeling the full training lifecycle (training request → GPU provisioning → telemetry/anomaly analysis → risk/cost routing → approved remediation & audit) as Maestro BPMN subprocesses.
- **9 roles** as BPMN swimlanes — some realized as autonomous LLM agents (Telemetry Analyst, Anomaly Risk Agent), others as human-in-the-loop review boards via UiPath Action Center.
- **An agentic "Fast Track" gateway** — the Anomaly Risk Agent scores each event and bypasses the full review board for low-risk, contained anomalies (auto-remediate, e.g. release an idle instance).
- **Vendor-agnostic sources** — live reward/loss telemetry, container logs, a hardware monitor (GPU/thermal/quota), or a researcher console all normalize to one canonical `IncidentReport` (training-run anomaly event).
- **Audit-grade traceability** — immutable log entries at every gateway and task node (GPU hours, cost, approvals).

## The 8 training-fleet containers

```
Process 1 · Anomaly & Request Intake
  1. Anomaly Report       Telemetry/logs/monitor → Telemetry Analyst → Researcher HITL → disposition
  2. Manual Intervention  Researcher console request or a fixed monitor flags an anomaly + feedback loop

Process 2 · Analysis & Risk Routing
  3. Risk & Anomaly Analysis  Anomaly → Anomaly Risk Agent → Fast Track OR Researcher Review Board (HITL)
  4. Cost & Impact Analysis   Cloud-GPU economic + organizational impact (idle spend / run loss / liability / fleet reach)

Process 3 · Action & Compliance
  5. Remediation Plan     Analyst Agent + RL Engineer draft a recovery playbook (retune/restart) → Ops HITL
  6. Execute Remediation  SSH-shutdown a diverging run, release/teardown an instance; HOLD a production-bound run
  7. Cloud/Registry Write-back  **RPA robot** writes to the cloud console, billing dashboard, model registry
  8. Quality Assurance    Compliance-summary agent + immutable audit log + researcher sign-off
```

## 🛠️ UiPath Components & Architecture

Our architecture integrates the full suite of advanced UiPath Automation Cloud components as an enterprise governance and orchestration layer:

| UiPath Component | Description & Role in Solution |
| :--- | :--- |
| **UiPath Maestro BPMN** | The primary process orchestration engine. Models and controls the full 8-container training lifecycle from ingestion to termination/registry. |
| **UiPath Agent Builder** | Coordinates the specialized autonomous AI agents (Telemetry Analyst, Anomaly Risk Agent, Cost & Impact Agent) with structured prompt templates. |
| **UiPath Action Center** | Renders rich interactive Human-in-the-Loop (HITL) forms for researchers to inspect training telemetry (loss/reward curves) and approve/reject weight deployment. |
| **UiPath RPA Robots & API Workflows** | Executes hard integration tasks (such as GCP/AWS cloud-provider console interactions, SSH container termination, and model weight registry updates). |
| **UiPath Orchestrator Queues** | Manages the unified, high-reliability `IncidentReports` queue that triggers process executions upon new anomaly detection. |

---

## 🤖 Agent Type: Both Coded Agents and Low-code Agents

This solution leverages a **Hybrid (Both Coded and Low-code)** agent architecture to combine enterprise-grade stability with high-intelligence reasoning:

1. **Low-code / No-code Agents (UiPath Maestro BPMN & Orchestrator)**: Handles the end-to-end routing, human approvals (Action Center), queue state transitions, and high-level execution policies.
2. **Coded Agents (Python / LangChain / Claude & Gemini)**: Handles real-time telemetry analysis (1Hz data processing, anomaly classification, gradient collapse detection, and risk scoring). These coded agents connect seamlessly to UiPath via **REST API endpoints and Orchestrator Queues**, creating a closed-loop system where advanced code-based intelligence runs under low-code BPMN governance.

Full architecture and design patterns: [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md).

---

## 🚀 Setup & Execution Instructions for Judging

You can configure, run, and evaluate this solution using either a quick offline simulation or a full cloud deployment.

### Option A: Quick Offline Local Run (Recommended for Immediate Verification)
The entire agentic pipeline, telemetry monitoring, exclusive gateways, and write-back execution are fully testable locally with **zero external dependencies** (the LLM and cloud services fallback elegantly to rule-based mock logic if no API keys are provided):

1. **Clone the repository and enter the directory**:
   ```bash
   git clone https://github.com/ForenlyAI/uipath-maestro-ecm.git
   cd uipath-maestro-ecm
   ```

2. **Initialize a virtual environment and install dependencies**:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Validate the JSON schemas and incident triggers**:
   Verify that all incoming telemetry and resource alerts comply with the strict data model schema:
   ```bash
   python -c "
   import json, glob
   from jsonschema import Draft202012Validator
   schema = json.load(open('samples/triggers/incident_report.schema.json'))
   v = Draft202012Validator(schema)
   for f in glob.glob('samples/triggers/*.json'):
       if 'schema' in f: continue
       v.validate(json.load(open(f)))
       print('Verified:', f)
   "
   ```

4. **Run the complete end-to-end pipeline simulation**:
   This runs the anomaly triage, executes the Coded Telemetry Analyst, routes the event via the Risk gateway, triggers the actions, and updates the local registry:
   ```bash
   python run_pipeline.py
   ```

5. **Run the automated test suite**:
   ```bash
   python -m pytest -v
   ```

### Option B: Deploying & Running on UiPath Automation Cloud (Maestro)
To set up, configure, and execute the Maestro BPMN process live in the cloud environment:
1. **Studio Web Import**: Connect your UiPath Studio Web workspace to this git repository, or import the pre-compiled BPMN diagram located at `maestro/FieldIncidentTriage/content/FieldIncidentTriage.bpmn`.
2. **Queue Setup**: Create an Orchestrator Queue named `IncidentReports` on your UiPath tenant and wire it as the process trigger.
3. **HITL Forms & Integration**: Deploy the Action Center schema (`artifacts/container1/action_center_irb.json`) and configure your Agent Builder credentials.
4. **Detailed Cloud Deployment Steps**: For full step-by-step guidance on Automation Cloud provisioning, credential binding, and publishing, follow our comprehensive [UiPath Cloud Deployment Runbook (docs/DEPLOY-MAESTRO.md)](./docs/DEPLOY-MAESTRO.md).

## Community

Building this in the open — join the team chat on Discord: https://discord.gg/ntXbNbvN95

## Contributing

Contributions are welcome — see [`CONTRIBUTING.md`](./CONTRIBUTING.md). Day-to-day discussion happens on the project **Discord**.

## License

[Apache License 2.0](./LICENSE)
