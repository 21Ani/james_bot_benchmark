"""Dataset models and loading."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BenchmarkQuestion:
    id: str
    question: str
    expected_answer: str
    document_id: str
    category: str
    difficulty: str
    source_section: str


@dataclass
class BenchmarkDataset:
    name: str
    description: str
    documents: dict[str, str]
    questions: list[BenchmarkQuestion]

    @classmethod
    def load(cls, path: Path, documents_dir: Path) -> "BenchmarkDataset":
        payload = json.loads(path.read_text(encoding="utf-8"))
        documents: dict[str, str] = {}

        for doc_id, filename in payload["documents"].items():
            doc_path = documents_dir / filename
            if not doc_path.exists():
                raise FileNotFoundError(f"Document not found: {doc_path}")
            documents[doc_id] = doc_path.read_text(encoding="utf-8")

        questions = [
            BenchmarkQuestion(
                id=item["id"],
                question=item["question"],
                expected_answer=item["expected_answer"],
                document_id=item["document_id"],
                category=item.get("category", "general"),
                difficulty=item.get("difficulty", "medium"),
                source_section=item.get("source_section", ""),
            )
            for item in payload["questions"]
        ]

        return cls(
            name=payload["name"],
            description=payload["description"],
            documents=documents,
            questions=questions,
        )
