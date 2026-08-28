import json
import httpx
from typing import Dict, Any
from backend.app.providers.llm.base import LLMProvider
from backend.app.core.config import settings
from backend.app.core.logging import logger


class GeminiLLMProvider(LLMProvider):
    """
    Google Gemini Provider for real-time generative reasoning with strict JSON response schema.
    """
    def __init__(self, api_key: str = "", model: str = "gemini-2.0-flash"):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.LLM_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"System Instructions:\n{system_prompt}\n\nContext to analyze:\n{user_prompt}"}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                logger.error(f"Gemini API error: {resp.status_code} - {resp.text}")
                raise RuntimeError(f"Gemini API returned status {resp.status_code}")

            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_text)
