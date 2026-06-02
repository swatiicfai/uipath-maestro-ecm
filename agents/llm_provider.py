"""LLM provider abstraction for the agentic task nodes.

The BPMN orchestration is the product; the LLM is a swappable task node. This module
exposes a single `complete_json()` entry point with three layers, tried in order:

  1. Anthropic Claude  (primary)   — env ANTHROPIC_API_KEY
  2. Google Gemini     (fallback)  — env GEMINI_API_KEY
  3. Deterministic rules (offline) — always available; no network, no keys

The offline layer mirrors the Safety Risk gateway math in
`samples/simulate_gateway.py`, so the pipeline runs end-to-end in CI or a demo
machine with no credentials and still produces schema-valid output.
"""
import json
import os

# Provider order is intentional: Claude primary, Gemini fallback (see docs/ARCHITECTURE.md).
PRIMARY_MODEL = "claude-3-5-sonnet-v2"
FALLBACK_MODEL = "gemini-2.0-flash"


def _try_anthropic(system_prompt, user_payload):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        import anthropic
    except ImportError:
        return None
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model=PRIMARY_MODEL,
        max_tokens=1500,
        temperature=0.1,
        system=system_prompt,
        messages=[{"role": "user", "content": json.dumps(user_payload)}],
    )
    return _extract_json(msg.content[0].text), "anthropic:" + PRIMARY_MODEL


def _try_gemini(system_prompt, user_payload):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    try:
        import google.generativeai as genai
    except ImportError:
        return None
    genai.configure(api_key=key)
    model = genai.GenerativeModel(FALLBACK_MODEL, system_instruction=system_prompt)
    resp = model.generate_content(json.dumps(user_payload))
    return _extract_json(resp.text), "gemini:" + FALLBACK_MODEL


def _extract_json(text):
    """Pull the first JSON object out of an LLM response (handles ```json fences)."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in LLM response")
    return json.loads(text[start : end + 1])


def complete_json(system_prompt, user_payload, offline_fn):
    """Return (result_dict, provider_label).

    Tries Claude, then Gemini, then the deterministic `offline_fn(user_payload)`.
    Any provider error degrades to the next layer — the pipeline never hard-fails
    on a missing key or a flaky network.
    """
    for attempt in (_try_anthropic, _try_gemini):
        try:
            out = attempt(system_prompt, user_payload)
            if out is not None:
                return out
        except Exception as exc:  # noqa: BLE001 — degrade, don't crash the BPMN node
            print(f"  [provider] {attempt.__name__} failed ({exc}); falling back")
    return offline_fn(user_payload), "offline:rules"
