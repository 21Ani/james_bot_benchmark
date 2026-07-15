"""Accuracy and grounding evaluation metrics."""

from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s%.-]", "", text)
    return text


@dataclass
class EvaluationResult:
    accuracy_strict: bool
    accuracy_fuzzy: bool
    fuzzy_score: float
    grounding_score: float
    details: str


class ResponseEvaluator:
    def __init__(self, fuzzy_threshold: int = 85, grounding_threshold: int = 70):
        self.fuzzy_threshold = fuzzy_threshold
        self.grounding_threshold = grounding_threshold

    def evaluate(
        self,
        response: str,
        expected_answer: str,
        source_document: str,
    ) -> EvaluationResult:
        if not response or not response.strip():
            return EvaluationResult(
                accuracy_strict=False,
                accuracy_fuzzy=False,
                fuzzy_score=0.0,
                grounding_score=0.0,
                details="Empty response",
            )

        norm_response = _normalize(response)
        norm_expected = _normalize(expected_answer)

        strict = norm_expected in norm_response or norm_response in norm_expected
        fuzzy_score = float(fuzz.token_set_ratio(norm_expected, norm_response))
        fuzzy = fuzzy_score >= self.fuzzy_threshold

        grounding_score = self._grounding_score(response, source_document)
        details = (
            f"strict={strict}, fuzzy={fuzzy_score:.1f}, grounding={grounding_score:.1f}"
        )

        return EvaluationResult(
            accuracy_strict=strict,
            accuracy_fuzzy=fuzzy,
            fuzzy_score=fuzzy_score,
            grounding_score=grounding_score,
            details=details,
        )

    def _grounding_score(self, response: str, source_document: str) -> float:
        """Measure how much of the response is supported by source document text."""
        response_tokens = set(_normalize(response).split())
        if not response_tokens:
            return 0.0

        doc_normalized = _normalize(source_document)
        supported = sum(1 for token in response_tokens if token in doc_normalized)
        return (supported / len(response_tokens)) * 100.0
