// ===== SENTINEL DEMO SIMULATION =====

const incidents = [
  {
    id: "IR-20260607-0003",
    title: "HARDWARE_FAULT: GPU thermal throttling detected on training node",
    analyst: "HARDWARE_FAULT risk=0.45 conf=0.92 action=HOLD",
    gateway: "HITL",
    cloud: "provider aws-us-east-1 (AWS Spot (us-east-1, H100)) tier=A openIssues=2",
    action: "QA-00004 (OPEN, owner=review-board)"
  },
  {
    id: "IR-20260607-0001",
    title: "GRADIENT_COLLAPSE: reward flatlined and gradients vanished at step 24000",
    analyst: "GRADIENT_COLLAPSE risk=0.45 conf=0.92 action=RESTART",
    gateway: "HITL",
    cloud: "provider aws-us-east-1 (AWS Spot (us-east-1, H100)) tier=A openIssues=2",
    action: "QA-00005 (OPEN, owner=review-board)"
  },
  {
    id: "IR-20260607-0004",
    title: "Idle GPU spend: instance kept running 40 min after the run finished",
    analyst: "RESOURCE_RISK risk=0.05 conf=0.92 action=PROCEED",
    gateway: "FAST",
    cloud: "provider gcp-us-central1 (GCP (us-central1, A100/L4)) tier=B openIssues=1",
    action: "QA-00006 (OPEN, owner=auto-remediation)"
  },
  {
    id: "IR-20260607-0002",
    title: "LOSS_DIVERGENCE: critic loss diverging and reward crashing on a bipedal run",
    analyst: "LOSS_DIVERGENCE risk=0.45 conf=0.92 action=RESTART",
    gateway: "HITL",
    cloud: "provider amd-devcloud (AMD Developer Cloud (MI300X)) tier=A openIssues=0",
    action: "QA-00007 (OPEN, owner=review-board)"
  },
  {
    id: "IR-20260607-0005",
    title: "Cloud GPU quota nearly exhausted on the training project",
    analyst: "RESOURCE_RISK risk=0.15 conf=0.92 action=PROCEED",
    gateway: "HITL",
    cloud: "provider aws-us-east-1 (AWS Spot (us-east-1, H100)) tier=A openIssues=2",
    action: "QA-00008 (OPEN, owner=review-board)"
  },
  {
    id: "IR-20260607-0006",
    title: "Idle GPU spend: second instance left running 55 min post-completion",
    analyst: "RESOURCE_RISK risk=0.03 conf=0.95 action=PROCEED",
    gateway: "FAST",
    cloud: "provider gcp-us-central1 (GCP (us-central1, A100/L4)) tier=B openIssues=0",
    action: "QA-00009 (OPEN, owner=auto-remediation)"
  },
  {
    id: "IR-20260607-0007",
    title: "HARDWARE_FAULT: NVLink error rate spiking on multi-GPU node",
    analyst: "HARDWARE_FAULT risk=0.55 conf=0.89 action=HOLD",
    gateway: "HITL",
    cloud: "provider aws-us-east-1 (AWS Spot (us-east-1, H100)) tier=A openIssues=3",
    action: "QA-00010 (OPEN, owner=review-board)"
  },
  {
    id: "IR-20260607-0008",
    title: "GRADIENT_COLLAPSE: policy gradient norm collapsed on grasping skill run",
    analyst: "GRADIENT_COLLAPSE risk=0.50 conf=0.91 action=RESTART",
    gateway: "HITL",
    cloud: "provider amd-devcloud (AMD Developer Cloud (MI300X)) tier=A openIssues=1",
    action: "QA-00011 (OPEN, owner=review-board)"
  }
];

let running = false;
let hitlCount = 0;
let autoCount = 0;
let totalCount = 0;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function addLine(text, cls = '') {
  const body = document.getElementById('terminalBody');
  const line = document.createElement('span');
  line.className = 't-line ' + cls;
  line.textContent = text;
  body.appendChild(line);
  body.scrollTop = body.scrollHeight;
}

function clearDemo() {
  document.getElementById('terminalBody').innerHTML = '<span class="t-line muted">$ Waiting for pipeline to start...</span>';
  hitlCount = 0; autoCount = 0; totalCount = 0;
  updateStats();
  running = false;
  const btn = document.getElementById('runBtn');
  btn.disabled = false;
  document.getElementById('btnIcon').textContent = '▶';
  document.getElementById('btnText').textContent = 'Run Pipeline Simulation';
}

function updateStats() {
  document.getElementById('ds-total').innerHTML = `Processed: <strong>${totalCount}</strong>`;
  document.getElementById('ds-hitl').innerHTML = `HITL: <strong class="danger">${hitlCount}</strong>`;
  document.getElementById('ds-auto').innerHTML = `Auto: <strong class="success">${autoCount}</strong>`;
}

async function runDemo() {
  if (running) return;
  running = true;
  hitlCount = 0; autoCount = 0; totalCount = 0;

  const btn = document.getElementById('runBtn');
  btn.disabled = true;
  document.getElementById('btnIcon').textContent = '⏳';
  document.getElementById('btnText').textContent = 'Running...';

  // Clear terminal
  document.getElementById('terminalBody').innerHTML = '';

  addLine('$ python run_pipeline.py', 'header');
  await sleep(500);
  addLine('', '');
  addLine('Sentinel — Agentic Cloud-GPU Orchestrator', 'header');
  addLine('Connecting to UiPath Orchestrator Queue: IncidentReports...', 'muted');
  await sleep(800);
  addLine('✓ Queue connected. Fetching incidents...', 'gateway-fast');
  await sleep(600);
  addLine(`✓ ${incidents.length} anomaly events dequeued.`, 'gateway-fast');
  await sleep(400);
  addLine('━'.repeat(60), 'separator');
  await sleep(300);

  for (let i = 0; i < incidents.length; i++) {
    const inc = incidents[i];
    await sleep(400);
    addLine('', '');
    addLine(`=== ${inc.id} :: ${inc.title}`, 'header');
    await sleep(350);
    addLine(`  analyst [offline:rules] -> ${inc.analyst}`, 'analyst');
    await sleep(300);

    if (inc.gateway === 'HITL') {
      addLine(`  gateway -> HITL: routed to Researcher Review Board (Action Center)`, 'gateway-hitl');
      hitlCount++;
    } else {
      addLine(`  gateway -> FAST TRACK: autonomous remediation, no human gate`, 'gateway-fast');
      autoCount++;
    }
    await sleep(250);

    addLine(`  cloud   -> ${inc.cloud}`, 'cloud');
    await sleep(200);
    addLine(`  action  -> ${inc.action}`, 'action');

    totalCount++;
    updateStats();
  }

  await sleep(500);
  addLine('', '');
  addLine('━'.repeat(60), 'separator');
  addLine(`--- processed ${incidents.length} anomaly event(s): ${hitlCount} routed to HITL, ${autoCount} autonomous fast-track ---`, 'summary');
  await sleep(200);
  addLine('✓ All transactions marked Successful in Orchestrator Queue.', 'gateway-fast');
  addLine('✓ Audit log written. Pipeline complete.', 'gateway-fast');

  running = false;
  btn.disabled = false;
  document.getElementById('btnIcon').textContent = '▶';
  document.getElementById('btnText').textContent = 'Run Again';
}

// Intersection Observer for fade-in animations
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.animation = 'fadeIn 0.6s ease forwards';
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.problem-card, .tech-card, .team-card, .flow-node').forEach(el => {
  el.style.opacity = '0';
  observer.observe(el);
});
