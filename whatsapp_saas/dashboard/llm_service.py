import json
import os

import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
MAX_COMMENTS = 40


class LLMUnavailable(Exception):
    pass


def analyze_feedback(rating_counts, entries):
    """entries: list of dicts with location, rating, comment."""
    lines = [
        f"- [{e['location']}] ({e['rating']}) {e['comment']}" for e in entries[:MAX_COMMENTS]
    ]
    prompt = (
        "You are a customer-experience analyst for a cafe/restaurant business. "
        "Analyze the customer feedback below and reply ONLY with JSON using these keys: "
        "summary (2-3 sentences), strengths (list of short strings), "
        "issues (list of objects with 'issue', 'location', 'severity' as high|medium|low), "
        "solutions (list of objects with 'for_issue' and 'action', concrete and practical). "
        "Mention a location only if the feedback points to it.\n\n"
        f"Rating counts: {json.dumps(rating_counts)}\n\n"
        "Feedback:\n" + "\n".join(lines)
    )

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=180,
        )
        resp.raise_for_status()
        result = json.loads(resp.json()["response"])
    except (requests.RequestException, ValueError, KeyError) as e:
        raise LLMUnavailable(str(e))

    return {
        "summary": result.get("summary", ""),
        "strengths": result.get("strengths", []),
        "issues": result.get("issues", []),
        "solutions": result.get("solutions", []),
    }
