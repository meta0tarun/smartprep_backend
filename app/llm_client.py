# app/llm_client.py
import os
import httpx
import json
from .config import Config
from typing import List, Dict, Any

OPENROUTER_URL = "https://api.openrouter.ai/v1/chat/completions"

def call_llm_for_topics(chunks: List[str]) -> Dict[str, Any]:
    """
    Send combined prompt to OpenRouter and parse response into a topics map.
    This function returns raw LLM response and a normalized topics_map dict.
    """
    if Config.DEMO_MODE or not Config.OPENROUTER_API_KEY:
        # demo stub
        return {
            "raw": {"stub": True},
            "topics_map": {"Algebra": 12, "Probability": 8, "Calculus": 4},
            "summary": "Demo-mode results (OPENROUTER_API_KEY missing or DEMO_MODE enabled)."
        }

    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    # Build a prompt that asks the LLM to list topics and approximate weight
    system = {"role": "system", "content": "You are an assistant that extracts topics and weight from exam question paper text. Return JSON with 'topics': [{'name': str, 'score': int}], and 'summary'."}
    user_content = "Extract topics and approximate importance scores from the following text chunks. Return only valid JSON of the form {\"topics\": [{\"name\": \"...\", \"score\": 10}, ...], \"summary\": \"...\"}\n\n"
    for i, c in enumerate(chunks):
        user_content += f"--- CHUNK {i+1} ---\n{c}\n\n"

    messages = [system, {"role": "user", "content": user_content}]

    payload = {
        "model": Config.OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 600
    }

    with httpx.Client(timeout=120.0) as client:
        r = client.post(OPENROUTER_URL, json=payload, headers=headers)
        if r.status_code != 200:
            # raise an exception with body to help debugging
            raise RuntimeError(f"LLM call failed: status={r.status_code} body={r.text}")
        data = r.json()

    # the response shape depends on the model wrapper. Attempt to find content.
    try:
        # typical: data['choices'][0]['message']['content']
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        # Attempt to locate JSON in the content
        import re
        m = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if m:
            j = json.loads(m.group(0))
            topics = j.get("topics", [])
            summary = j.get("summary") or j.get("summary", "")
        else:
            # fallback: try if response is already JSON
            if isinstance(data, dict) and "topics" in data:
                j = data
                topics = j.get("topics", [])
                summary = j.get("summary", "")
            else:
                # cannot parse -> return raw
                return {"raw": data, "topics_map": {}, "summary": ""}
    except Exception:
        # parse error - return raw
        return {"raw": data, "topics_map": {}, "summary": ""}

    # normalize topics list into map
    topics_map = {}
    for t in topics:
        try:
            name = str(t.get("name") if isinstance(t, dict) else t[0])
            score = int(t.get("score") if isinstance(t, dict) else (t[1] if len(t) > 1 else 1))
            topics_map[name] = topics_map.get(name, 0) + score
        except Exception:
            continue

    return {"raw": data, "topics_map": topics_map, "summary": summary}
