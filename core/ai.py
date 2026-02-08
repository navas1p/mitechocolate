import json
import os
import urllib.request

from django.conf import settings

from .reports import basic_report


def _load_project_rules() -> str:
    path = settings.BASE_DIR / "docs" / "project_requirements.md"
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return "Project rules not found."


def ask_ai(question: str) -> str:
    report = basic_report(question)
    if report:
        return report

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY is not set. Please add it to your environment."

    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    temperature = float(os.environ.get("OPENAI_TEMPERATURE", "0.2"))
    max_tokens = int(os.environ.get("OPENAI_MAX_TOKENS", "600"))
    api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")

    system_rules = _load_project_rules()
    system_prompt = (
        "You are the AI assistant for the Heart of Chocolate Django system. "
        "Use the project rules below as the source of truth.\n\n"
        f"{system_rules}"
    )

    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    }

    req = urllib.request.Request(
        f"{api_base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        return f"AI request failed: {exc}"
