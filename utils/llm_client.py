"""
Single point of contact with the local LLM (Ollama).
Every agent calls complete() instead of interacting with Ollama directly.
"""

import requests
from config import settings


def complete(system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
    """Send a chat request to Ollama and return the assistant response."""

    response = requests.post(
        settings.ollama_url,
        json={
            "model": settings.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "stream": False,
            "options": {
                "num_predict": max_tokens
            }
        },
        timeout=600,
    )

    response.raise_for_status()

    data = response.json()

    # Debug: print complete response from Ollama
    print("\n========== OLLAMA RESPONSE ==========")
    print(data)
    print("=====================================\n")

    if "message" in data and "content" in data["message"]:
        return data["message"]["content"]

    if "response" in data:
        return data["response"]

    if "error" in data:
        raise RuntimeError(f"Ollama Error: {data['error']}")

    raise RuntimeError(f"Unexpected Ollama response: {data}")