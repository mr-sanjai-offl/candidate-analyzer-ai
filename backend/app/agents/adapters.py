"""Concrete AI model provider adapters.

Implements OpenAI API client, OpenRouter client, and a deterministic Mock client.
"""

import json
import logging
import httpx
from typing import Any

from app.agents.base import BaseLLMAdapter, LLMRequest, LLMResponse, TokenUsage

logger = logging.getLogger(__name__)


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for official OpenAI API endpoints."""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1") -> None:
        self.api_key = api_key
        self.base_url = base_url

    async def generate(self, request: LLMRequest) -> LLMResponse:
        model = request.model or "gpt-4o-mini"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": request.system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": request.prompt},
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                choice = data["choices"][0]["message"]["content"]
                usage_data = data.get("usage", {})
                usage = TokenUsage(
                    prompt_tokens=usage_data.get("prompt_tokens", 0),
                    completion_tokens=usage_data.get("completion_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0),
                )
                return LLMResponse(text=choice, usage=usage, model=model)
            except Exception as e:
                logger.error("OpenAI API call failed: %s", e)
                raise RuntimeError(f"OpenAI adapter generation failure: {e}") from e


class OpenRouterAdapter(BaseLLMAdapter):
    """Adapter for OpenRouter gateway endpoints."""

    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1") -> None:
        self.api_key = api_key
        self.base_url = base_url

    async def generate(self, request: LLMRequest) -> LLMResponse:
        model = request.model or "meta-llama/llama-3-8b-instruct:free"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://apexguidance.ai",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": request.system_prompt or "You are an assistant."},
                {"role": "user", "content": request.prompt},
            ],
            "temperature": request.temperature,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                choice = data["choices"][0]["message"]["content"]
                usage_data = data.get("usage", {})
                usage = TokenUsage(
                    prompt_tokens=usage_data.get("prompt_tokens", 0),
                    completion_tokens=usage_data.get("completion_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0),
                )
                return LLMResponse(text=choice, usage=usage, model=model)
            except Exception as e:
                logger.error("OpenRouter API call failed: %s", e)
                raise RuntimeError(f"OpenRouter adapter generation failure: {e}") from e


class MockAdapter(BaseLLMAdapter):
    """Deterministic, rule-based mock LLM adapter.

    Never hits external APIs. Generates responses based on prompt keyword matching.
    """

    async def generate(self, request: LLMRequest) -> LLMResponse:
        prompt_text = request.prompt.lower()
        task = (request.task_name or "").lower()

        # ── Route based on task_name first, then keywords ─────────────────────
        if task == "recruiter_report" or "recruiter report" in prompt_text or "recruiter" in prompt_text:
            text = self._mock_recruiter_report()
        elif task == "candidate_feedback" or "feedback" in prompt_text or "candidate report" in prompt_text or "recommendations" in prompt_text:
            text = self._mock_candidate_feedback()
        elif task == "job_matching" or "job match" in prompt_text or "match assessment" in prompt_text:
            text = self._mock_job_matching()
        elif task == "interview_generation" or "interview question" in prompt_text or "interview" in prompt_text:
            text = self._mock_interview_questions()
        elif task == "skill_explanation" or "chat" in prompt_text or "why is" in prompt_text or "explain" in prompt_text:
            text = self._mock_chat_response(request.prompt)
        else:
            text = self._mock_default_response()

        usage = TokenUsage(prompt_tokens=len(request.prompt) // 4, completion_tokens=len(text) // 4, total_tokens=(len(request.prompt) + len(text)) // 4)
        return LLMResponse(text=text, usage=usage, model="mock-model-engine")

    # ── Mocks Generation Helpers ─────────────────────────────────────────────

    def _mock_recruiter_report(self) -> str:
        report = {
            "Executive Summary": "Strong backend candidate with significant production experience in FastAPI and Docker, backed by public GitHub repositories.",
            "Technical Profile": {
                "Programming Languages": "Python (Verified), C++ (Claimed)",
                "Frameworks": "FastAPI (Verified)",
                "Projects": "my-api (Verified with 2 stars)",
                "Architecture": "Restful API design with clean repositories segregation",
                "Open Source": "2 public repositories on GitHub",
                "Problem Solving": "Solid algorithmic base verified via LeetCode daily streaks",
                "DSA": "Demonstrated core trees and graphs problem solving capability",
                "Consistency": "Highly active during repository setup",
                "Engineering Maturity": "Containerizes and packages software via Docker configurations"
            },
            "Strengths": ["Hands-on Async Python experience", "Containerized setup with Docker configs"],
            "Weaknesses": ["Frontend framework experience is missing", "No cloud deployments evidence found"],
            "Risks": ["High dependency on personal templates", "Low unit testing coverage"],
            "Interview Focus Areas": ["Explain concurrent async programming locks in Python", "Demonstrate microservice deployment in Kubernetes"],
            "Hiring Recommendation": "Strong Hire",
            "Confidence Explanation": "95% confidence based on source evidence cross-checks.",
            "Evidence References": [
                "Resume: claims 3 years Backend experience",
                "GitHub: my-api repository uses Python (10000 bytes) and includes a working Dockerfile"
            ]
        }
        return json.dumps(report, indent=2)

    def _mock_candidate_feedback(self) -> str:
        feedback = {
            "Learning roadmap": ["Acquire React/TypeScript frontend capabilities", "Learn AWS/GCP cloud configurations"],
            "Missing technologies": ["React", "Kubernetes", "AWS"],
            "Recommended certifications": ["AWS Certified Developer - Associate"],
            "Recommended projects": [
                {"title": "Interactive Client Dashboard", "tech": "React, TypeScript"}
            ],
            "Weekly roadmap": ["Week 1: Learn React Hooks", "Week 2: Call async backend APIs from React client"],
            "Monthly roadmap": ["Month 1: Frontend foundations", "Month 2: Deploy to AWS cloud EC2"],
            "Interview preparation plan": ["Practice Graph traversals on LeetCode", "Mock backend REST API architecture explanations"],
            "Resume improvements": ["Highlight Docker and API gateway skills prominently"],
            "GitHub improvements": ["Add structured README.md files to all repositories"],
            "LeetCode improvements": ["Increase solves of Medium/Hard algorithms problems"]
        }
        return json.dumps(feedback, indent=2)

    def _mock_job_matching(self) -> str:
        matching = {
            "match_score": 85.0,
            "missing_skills": ["React", "Kubernetes"],
            "transferable_skills": ["Python scripting", "Docker packaging"],
            "suggested_learning_plan": "Focus on React dashboard implementations to complement backend skills."
        }
        return json.dumps(matching, indent=2)

    def _mock_interview_questions(self) -> str:
        questions = [
            {"category": "Backend", "question": "What is the difference between concurrency and parallelism in Python's async/await?", "difficulty": "Medium"},
            {"category": "DevOps", "question": "Explain multi-stage builds in Docker and why they are useful.", "difficulty": "Hard"}
        ]
        return json.dumps(questions, indent=2)

    def _mock_chat_response(self, prompt: str) -> str:
        if "backend readiness" in prompt.lower():
            return "The candidate's backend readiness score is 72% because while they show strong Python/FastAPI skills and Docker usage, they lack PostgreSQL/Redis database integration evidence in their public GitHub repositories."
        return "Based on the evidence database, the candidate possesses verified skills in Python and Docker, with claims in C++ on their resume."

    def _mock_default_response(self) -> str:
        return "Engine processing complete. Target output produced successfully."
