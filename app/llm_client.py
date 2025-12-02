# app/llm_client.py
import os
import requests
import logging
from typing import Optional
from .config import Config

logger = logging.getLogger("app.llm_client")
logger.setLevel(logging.INFO)

def call_openrouter(prompt: str, model: Optional[str] = None, max_tokens: int = 512) -> dict:
    """
    Call OpenRouter chat/completions endpoint (or other configured endpoint).
    Returns dict with 'summary' and optionally other fields.
    """
    if Config.DEMO_MODE or not Config.OPENROUTER_API_KEY:
        logger.info("DEMO_MODE enabled or API key missing — returning demo result.")
        return {
            "summary": "Demo-mode results (OPENROUTER_API_KEY missing or DEMO_MODE enabled).",
            "topicsMap": {"Algebra": 12, "Probability": 8, "Calculus": 4},
            "raw": {"stub": True},
        }

    url = Config.OPENROUTER_API_URL
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    model = model or Config.OPENROUTER_MODEL

    body = {
        "model": model,
        # the exact shape depends on the provider — adjust as required
        "messages": [
            {"role": "system", "content": "You are an assistant that extracts top topics from exam question text."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0,
    }

    try:
        logger.info("LLM: calling %s (model=%s)", url, model)
        r = requests.post(url, json=body, headers=headers, timeout=120)
        r.raise_for_status()
        data = r.json()
        # adapt parsing based on provider response format
        # For OpenRouter Chat Completions style the text may be in choices[0].message.content
        summary = None
        raw = data
        try:
            if isinstance(data, dict):
                # Try common shapes
                if "choices" in data and len(data["choices"]) > 0:
                    msg = data["choices"][0].get("message")
                    if msg and isinstance(msg, dict):
                        summary = msg.get("content")
                    else:
                        summary = data["choices"][0].get("text") or None
                elif "output" in data:  # some APIs
                    summary = str(data["output"])
        except Exception:
            summary = str(data)

        return {
            "summary": summary or "No summary returned by LLM.",
            "topicsMap": {},  # let the LLM consumer fill this if needed
            "raw": raw,
        }
    except Exception as e:
        logger.exception("LLM call failed: %s", e)
        return {
            "summary": None,
            "topicsMap": {},
            "raw": {"error": str(e)},
        }
