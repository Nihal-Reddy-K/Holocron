"""Optional LLM explanation layer for Holocron.

The numerical pipeline never depends on this module. If no API key/provider
is configured, the backend returns a safe deterministic fallback insight.

The provider call is server-side only.
"""
from __future__ import annotations

import json
import os
from typing import Any


SYSTEM_PROMPT = """
You are the explanation layer for Holocron, a healthcare research/demo
prototype for quantitative movement monitoring.

Rules:
- Only interpret the supplied measurements and context.
- Do not invent measurements.
- Do not diagnose Huntington's disease, Parkinson's disease, ALS, or any other condition.
- Do not infer causality.
- Do not describe one session as disease progression.
- Distinguish measured data from self-reported context.
- Do not recommend medication changes or treatment.
- Do not claim that a simulated intervention is effective.
- Do not interpret one frequency value as proof of a specific disorder.
- Use cautious language.
- If evidence is insufficient, say so.
- Keep the response short.
Return JSON with exactly:
{
  "summary": "string",
  "observations": ["string", "..."],
  "limitations": "string"
}
"""


def _fallback(result: dict) -> dict:
    baseline = result.get("baseline", {})
    pattern = result.get("pattern", {})
    current = baseline.get("current", result.get("current_index", 0))
    base = baseline.get("baseline", current)
    change = baseline.get("relative_change", 0)
    observations = [
        f"Movement Index was {current:.1f}, compared with a recent personal baseline of {base:.1f}."
    ]
    if pattern.get("pattern"):
        observations.append(f"Pattern classifier output: {pattern['pattern'].replace('_', ' ')}.")
    context = result.get("context") or {}
    if context.get("sleep_hours") is not None:
        observations.append(f"Self-reported sleep was {context['sleep_hours']} hours.")
    if context.get("stress") is not None:
        observations.append(f"Self-reported stress was {context['stress']}.")
    direction = "above" if change > 0 else "below" if change < 0 else "near"
    summary = f"Movement was {direction} the recent personal baseline."
    if not baseline.get("baseline_ready", False):
        summary = "This is an initial/provisional baseline comparison; more sessions are needed for a personal baseline."
    return {
        "summary": summary,
        "observations": observations,
        "limitations": "Prototype interpretation only; not a clinical assessment. Context variables are self-reported and do not establish causality.",
        "provider": "local_fallback",
    }


def generate_insight(structured_result: dict) -> dict:
    api_key = os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback(structured_result)

    provider = os.getenv("AI_PROVIDER", "openai").lower()
    if provider != "openai":
        return _fallback(structured_result)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = os.getenv("AI_MODEL", "gpt-5-mini")
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(structured_result, separators=(",", ":")),
                },
            ],
        )
        text = getattr(response, "output_text", "") or ""
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise ValueError("AI response was not a JSON object")
        parsed.setdefault("summary", "Insufficient information for a concise interpretation.")
        parsed.setdefault("observations", [])
        parsed.setdefault("limitations", "Prototype interpretation only; not a clinical assessment.")
        parsed["provider"] = "openai"
        return parsed
    except Exception as exc:
        # AI is optional enrichment; never take down numerical processing.
        fallback = _fallback(structured_result)
        fallback["ai_error"] = str(exc)
        return fallback
