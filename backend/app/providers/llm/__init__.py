from backend.app.providers.llm.base import LLMProvider
from backend.app.providers.llm.mock import MockLLMProvider
from backend.app.providers.llm.gemini import GeminiLLMProvider
from backend.app.core.config import settings


def get_llm_provider(provider_type: str = "") -> LLMProvider:
    """Factory to retrieve configured LLMProvider."""
    target = provider_type or settings.LLM_PROVIDER.lower()
    if target == "gemini" and settings.GEMINI_API_KEY:
        return GeminiLLMProvider()
    return MockLLMProvider()


__all__ = ["LLMProvider", "MockLLMProvider", "GeminiLLMProvider", "get_llm_provider"]
