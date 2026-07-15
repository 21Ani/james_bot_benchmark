"""System adapters for benchmark targets."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class SystemResponse:
    text: str
    response_time_ms: float
    metadata: dict[str, Any]


class BaseAdapter(ABC):
    @abstractmethod
    def ask(self, question: str, document_id: str, document_text: str) -> SystemResponse:
        raise NotImplementedError


class JamesBotAdapter(BaseAdapter):
    """Adapter for James Bot / TalkingDB API. Falls back to mock when API is unavailable."""

    def __init__(self, config: dict[str, Any]):
        self.base_url = (config.get("base_url") or "").rstrip("/")
        self.api_key = config.get("api_key") or ""
        self.timeout = config.get("timeout_seconds", 120)

    def ask(self, question: str, document_id: str, document_text: str) -> SystemResponse:
        if self.base_url and self.api_key:
            return self._call_api(question, document_id)

        return self._mock_response(question, document_text)

    def _call_api(self, question: str, document_id: str) -> SystemResponse:
        start = time.perf_counter()
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"question": question, "document_id": document_id}

        response = requests.post(
            f"{self.base_url}/query",
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        elapsed_ms = (time.perf_counter() - start) * 1000

        return SystemResponse(
            text=data.get("answer", ""),
            response_time_ms=elapsed_ms,
            metadata={"mode": "live_api", "document_id": document_id},
        )

    def _mock_response(self, question: str, document_text: str) -> SystemResponse:
        """Simulates TalkingDB-style grounded retrieval for demo runs."""
        start = time.perf_counter()
        answer = self._extract_grounded_answer(question, document_text)
        elapsed_ms = (time.perf_counter() - start) * 1000 + 350

        return SystemResponse(
            text=answer,
            response_time_ms=elapsed_ms,
            metadata={"mode": "mock", "note": "Set JAMES_BOT_API_URL for live runs"},
        )

    def _extract_grounded_answer(self, question: str, document_text: str) -> str:
        question_lower = question.lower()
        lines = [line.strip() for line in document_text.splitlines() if line.strip()]

        keywords = [word for word in question_lower.split() if len(word) > 3]
        scored_lines: list[tuple[int, str]] = []

        for line in lines:
            line_lower = line.lower()
            score = sum(1 for kw in keywords if kw in line_lower)
            if score > 0:
                scored_lines.append((score, line))

        if not scored_lines:
            return "I could not find a grounded answer in the indexed documents."

        scored_lines.sort(key=lambda item: item[0], reverse=True)
        top_lines = [line for _, line in scored_lines[:3]]
        return " ".join(top_lines)


class ChatGPTAdapter(BaseAdapter):
    """Adapter for OpenAI ChatGPT. Mock mode simulates household AI limitations."""

    def __init__(self, config: dict[str, Any]):
        self.model = config.get("model", "gpt-4o-mini")
        self.api_key = config.get("api_key") or ""
        self.timeout = config.get("timeout_seconds", 60)
        self.include_document_context = config.get("include_document_context", False)

    def ask(self, question: str, document_id: str, document_text: str) -> SystemResponse:
        if self.api_key:
            return self._call_openai(question, document_text)

        return self._mock_response(question, document_text)

    def _call_openai(self, question: str, document_text: str) -> SystemResponse:
        from openai import OpenAI

        start = time.perf_counter()
        client = OpenAI(api_key=self.api_key, timeout=self.timeout)

        if self.include_document_context:
            system_prompt = (
                "Answer the question using ONLY the provided document. "
                "If the answer is not in the document, say you don't know."
            )
            user_content = f"Document:\n{document_text}\n\nQuestion: {question}"
        else:
            system_prompt = (
                "You are a general-purpose assistant. Answer based on your training knowledge. "
                "You do not have access to proprietary enterprise documents."
            )
            user_content = question

        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        text = completion.choices[0].message.content or ""

        return SystemResponse(
            text=text,
            response_time_ms=elapsed_ms,
            metadata={
                "mode": "live_api",
                "model": self.model,
                "document_context": self.include_document_context,
            },
        )

    def _mock_response(self, question: str, document_text: str) -> SystemResponse:
        """Simulates household AI without document access — often inaccurate on domain QA."""
        start = time.perf_counter()
        question_lower = question.lower()

        generic_responses = {
            "warranty": "Most enterprise products include a standard 1-year warranty, though terms vary by vendor.",
            "sla": "Typical enterprise SLAs guarantee 99.9% uptime with support response within 24 hours.",
            "refund": "Refund policies generally allow returns within 30 days if the product is unused.",
            "password": "Password reset is usually available through the account portal or support team.",
            "pricing": "Pricing depends on plan tier and is typically listed on the vendor website.",
        }

        answer = "I don't have access to your company's internal knowledge base documents."
        for keyword, response in generic_responses.items():
            if keyword in question_lower:
                answer = response
                break

        elapsed_ms = (time.perf_counter() - start) * 1000 + 800
        return SystemResponse(
            text=answer,
            response_time_ms=elapsed_ms,
            metadata={"mode": "mock", "note": "Set OPENAI_API_KEY for live runs"},
        )


def create_adapter(adapter_id: str, config: dict[str, Any]) -> BaseAdapter:
    if adapter_id == "james_bot":
        return JamesBotAdapter(config)
    if adapter_id == "chatgpt":
        return ChatGPTAdapter(config)
    raise ValueError(f"Unknown adapter: {adapter_id}")
