"""LLM integration for Archon — supports OpenAI API-compatible endpoints."""

import json
import time
import requests
from typing import Any, Generator


class LLMClient:
    def __init__(self, config: dict[str, Any]):
        self.provider = config.get("llm_provider", "openai")
        self.model = config.get("llm_model", "gpt-4o")
        self.temperature = config.get("temperature", 0.3)
        self.max_tokens = config.get("max_tokens", 4096)
        self.api_key = config.get("openai_api_key", "")
        self.base_url = config.get("llm_base_url", "https://api.openai.com/v1")
        self.timeout = config.get("llm_timeout", 30)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        last_error = None
        for attempt in range(3):
            try:
                return self._call_api(system_prompt, user_prompt)
            except requests.exceptions.Timeout as e:
                last_error = e
                if attempt < 2:
                    time.sleep(1 * (2**attempt))
                    continue
            except requests.exceptions.ConnectionError as e:
                last_error = e
                if attempt < 2:
                    time.sleep(1 * (2**attempt))
                    continue
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < 2:
                    time.sleep(1 * (2**attempt))
                    continue
        raise RuntimeError(
            f"LLM request failed after 3 attempts. "
            f"Provider: {self.provider}, Model: {self.model}. "
            f"Last error: {last_error}"
        )

    def generate_stream(self, system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        headers = self._build_headers()
        payload = self._build_payload(system_prompt, user_prompt, stream=True)

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
                stream=True,
            )
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"LLM stream request timed out after {self.timeout}s. "
                f"Provider: {self.provider}, Model: {self.model}."
            )
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(
                f"LLM stream connection failed. Check your network and API URL. "
                f"Provider: {self.provider}, URL: {self.base_url}. Error: {e}"
            )

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

    def _build_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_payload(self, system_prompt: str, user_prompt: str, stream: bool = False) -> dict:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if stream:
            payload["stream"] = True
        return payload

    def _call_api(self, system_prompt: str, user_prompt: str) -> str:
        headers = self._build_headers()
        payload = self._build_payload(system_prompt, user_prompt)

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            raise RuntimeError(
                f"LLM API returned HTTP {status}. Check your API key and model name. "
                f"Provider: {self.provider}, Model: {self.model}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"LLM request error: {e}") from e
