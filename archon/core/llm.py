"""LLM integration for Archon — supports OpenAI API-compatible endpoints."""

import json
import requests
from typing import Any


class LLMClient:
    def __init__(self, config: dict[str, Any]):
        self.provider = config.get("llm_provider", "openai")
        self.model = config.get("llm_model", "gpt-4o")
        self.temperature = config.get("temperature", 0.3)
        self.max_tokens = config.get("max_tokens", 4096)
        self.api_key = config.get("openai_api_key", "")
        self.base_url = config.get("llm_base_url", "https://api.openai.com/v1")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        raw = self.generate(system_prompt, user_prompt)
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(raw[start:end])
        except json.JSONDecodeError:
            pass
        return {"raw_response": raw}
