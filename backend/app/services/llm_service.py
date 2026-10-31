import json
import logging
import os
import re
from typing import Optional, Dict, Any
import httpx


class LLMService:
    """
    LLM inference adapter supporting Gemini, OpenAI, or offline grounded fallback.
    Extracts structured JSON responses when an API key is present in environment variables.
    """

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def is_configured(self) -> bool:
        return bool(self.gemini_api_key or self.openai_api_key)

    async def generate_json(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Query configured LLM and parse JSON output.
        Returns parsed dictionary if successful, or None to fall back to rule-based engine.
        """
        if self.gemini_api_key:
            return await self._call_gemini(prompt, system_prompt)
        elif self.openai_api_key:
            return await self._call_openai(prompt, system_prompt)
        return None

    async def _call_gemini(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system_prompt}\n\nTask:\n{prompt}"}]}
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return self._clean_and_parse_json(text)
                else:
                    logging.warning(f"Gemini API returned status {res.status_code}: {res.text[:200]}")
        except Exception as exc:
            logging.warning(f"Gemini LLM invocation failed: {exc}")
        return None

    async def _call_openai(self, prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    text = data["choices"][0]["message"]["content"]
                    return self._clean_and_parse_json(text)
                else:
                    logging.warning(f"OpenAI API returned status {res.status_code}: {res.text[:200]}")
        except Exception as exc:
            logging.warning(f"OpenAI LLM invocation failed: {exc}")
        return None

    def _clean_and_parse_json(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Extract and parse JSON from Markdown code blocks or raw response text."""
        if not raw_text or not raw_text.strip():
            return None

        clean = raw_text.strip()
        # Strip markdown fences if present
        if clean.startswith("```"):
            clean = re.sub(r"^```(?:json)?\s*", "", clean)
            clean = re.sub(r"\s*```$", "", clean)
            clean = clean.strip()

        try:
            return json.loads(clean)
        except Exception:
            # Try to locate first '{' and last '}'
            start = clean.find("{")
            end = clean.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(clean[start : end + 1])
                except Exception:
                    pass
        return None


llm_service = LLMService()
