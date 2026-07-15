"""Abstract interfaces for AI model provider adapters.

Decouples business logic from specific API providers (OpenRouter, OpenAI).
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Tracks token consumption for an LLM call."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class LLMRequest(BaseModel):
    """Input payload for LLM call."""

    prompt: str
    system_prompt: str | None = None
    temperature: float = 0.2
    max_tokens: int = 2000
    model: str | None = None
    task_name: str | None = None



class LLMResponse(BaseModel):
    """Output payload from LLM call."""

    text: str
    usage: TokenUsage = Field(default_factory=TokenUsage)
    model: str


class BaseLLMAdapter(ABC):
    """Abstract interface for all model provider adapters."""

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Call the provider endpoint and return completion response."""
        pass
