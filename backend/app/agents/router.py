"""Model Router.

Maps orchestration tasks (recruiter report, chat assistant) to appropriate LLM models
(high-performance vs low-cost).
"""


class ModelRouter:
    """Routes execution tasks to target models based on complexity and cost."""

    def __init__(self, use_cheap: bool = False) -> None:
        self.use_cheap = use_cheap

    def get_model(self, task_name: str) -> str:
        """Route to appropriate OpenAI/OpenRouter model string."""
        if self.use_cheap:
            return "gpt-4o-mini"

        # Route complex analyses to larger models
        if task_name in ("recruiter_report", "job_matching"):
            return "gpt-4o"
        return "gpt-4o-mini"
