from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMProvider(ABC):
    """
    Abstract LLM Provider interface.
    Ensures that RecoverAI is never hardcoded to any single model vendor.
    """
    @abstractmethod
    async def generate_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Generates a structured JSON response adhering strictly to the given schema.
        Must never trust raw text as executable commands.
        """
        pass
