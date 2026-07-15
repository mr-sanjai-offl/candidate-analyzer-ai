"""AI Orchestration Engine.

Coordinates prompts, context assembly, provider routing, output validation,
and token metrics logging.
"""

import logging
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.agents.adapters import OpenAIAdapter, OpenRouterAdapter, MockAdapter
from app.agents.base import BaseLLMAdapter, LLMRequest, LLMResponse
from app.agents.prompts import PromptManager
from app.agents.router import ModelRouter
from app.agents.validator import ResponseValidator
from app.agents.usage import TokenUsageTracker

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """The central orchestrator driving all AI workflow executions."""

    def __init__(self, settings: Any = None) -> None:
        self.settings = settings or get_settings()
        self.prompt_manager = PromptManager()
        self.model_router = ModelRouter()
        self.validator = ResponseValidator()
        self.tracker = TokenUsageTracker()
        self.adapter = self._resolve_adapter()

    def _resolve_adapter(self) -> BaseLLMAdapter:
        """Resolve LLM provider client adapter based on env settings."""
        provider = self.settings.LLM_PROVIDER.lower()
        if provider == "openai" and self.settings.OPENAI_API_KEY:
            logger.info("Initializing OpenAI API adapter client.")
            return OpenAIAdapter(api_key=self.settings.OPENAI_API_KEY)
        elif provider == "openrouter" and self.settings.OPENROUTER_API_KEY:
            logger.info("Initializing OpenRouter gateway client.")
            return OpenRouterAdapter(api_key=self.settings.OPENROUTER_API_KEY)

        logger.info("Initializing Mock LLM adapter client (deterministic fallback).")
        return MockAdapter()

    async def execute_task(
        self,
        db: AsyncSession | None,
        task_name: str,
        variables: dict[str, Any],
        required_keys: list[str] | None = None,
    ) -> tuple[Any, dict[str, Any]]:
        """Run full generation: renders template -> routes model -> calls adapter -> validates output.

        Returns a tuple (validated_payload, token_usage_info).
        """
        # 1. Load active template version and system context instructions
        system_prompt, user_prompt, version = await self.prompt_manager.get_prompt(
            db=db,
            name=task_name,
            variables=variables,
        )

        # 2. Select target model endpoint based on cost routing
        model = self.model_router.get_model(task_name)

        # 3. Call adapter client
        request = LLMRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=model,
            task_name=task_name,
        )

        logger.debug("Executing AI task %s with model %s", task_name, model)
        response: LLMResponse = await self.adapter.generate(request)

        # 4. Record token usage
        self.tracker.track(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
        )

        # 5. Run validation if required keys are provided
        if required_keys:
            is_valid, parsed = self.validator.validate_json(response.text, required_keys)
            if not is_valid:
                logger.warning(
                    "AI task %s output validation failed. Returning parsed payload context.",
                    task_name,
                )
            return parsed, response.usage.model_dump()

        return response.text, response.usage.model_dump()

