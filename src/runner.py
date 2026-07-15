"""Benchmark execution engine."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import Progress

from .adapters import BaseAdapter, create_adapter
from .config import BenchmarkConfig
from .dataset import BenchmarkDataset
from .evaluator import ResponseEvaluator


@dataclass
class QuestionResult:
    question_id: str
    system_id: str
    question: str
    expected_answer: str
    response: str
    response_time_ms: float
    accuracy_strict: bool
    accuracy_fuzzy: bool
    fuzzy_score: float
    grounding_score: float
    category: str
    difficulty: str
    document_id: str
    metadata: dict[str, Any]


class BenchmarkRunner:
    def __init__(self, config: BenchmarkConfig, dataset: BenchmarkDataset):
        self.config = config
        self.dataset = dataset
        self.evaluator = ResponseEvaluator(
            fuzzy_threshold=config.fuzzy_threshold,
            grounding_threshold=config.grounding_threshold,
        )
        self.console = Console()

    def run(self) -> dict[str, Any]:
        adapters: dict[str, BaseAdapter] = {}
        for system in self.config.systems:
            adapter_id = system["adapter"]
            adapters[system["id"]] = create_adapter(
                adapter_id,
                self.config.adapters.get(adapter_id, {}),
            )

        results: list[QuestionResult] = []

        with Progress() as progress:
            task = progress.add_task(
                "[cyan]Running benchmark...",
                total=len(self.config.systems) * len(self.dataset.questions),
            )

            for system in self.config.systems:
                system_id = system["id"]
                adapter = adapters[system_id]

                for question in self.dataset.questions:
                    document_text = self.dataset.documents[question.document_id]
                    response = adapter.ask(
                        question=question.question,
                        document_id=question.document_id,
                        document_text=document_text,
                    )
                    evaluation = self.evaluator.evaluate(
                        response=response.text,
                        expected_answer=question.expected_answer,
                        source_document=document_text,
                    )

                    results.append(
                        QuestionResult(
                            question_id=question.id,
                            system_id=system_id,
                            question=question.question,
                            expected_answer=question.expected_answer,
                            response=response.text,
                            response_time_ms=response.response_time_ms,
                            accuracy_strict=evaluation.accuracy_strict,
                            accuracy_fuzzy=evaluation.accuracy_fuzzy,
                            fuzzy_score=evaluation.fuzzy_score,
                            grounding_score=evaluation.grounding_score,
                            category=question.category,
                            difficulty=question.difficulty,
                            document_id=question.document_id,
                            metadata=response.metadata,
                        )
                    )
                    progress.advance(task)

        report = self._build_report(results)
        self._save_report(report)
        self._print_summary(report)
        return report

    def _build_report(self, results: list[QuestionResult]) -> dict[str, Any]:
        aggregated: dict[str, dict[str, Any]] = {}

        for system in self.config.systems:
            system_id = system["id"]
            system_results = [r for r in results if r.system_id == system_id]
            count = len(system_results) or 1

            aggregated[system_id] = {
                "system_name": system["name"],
                "total_questions": len(system_results),
                "accuracy_strict_pct": round(
                    sum(r.accuracy_strict for r in system_results) / count * 100, 2
                ),
                "accuracy_fuzzy_pct": round(
                    sum(r.accuracy_fuzzy for r in system_results) / count * 100, 2
                ),
                "avg_fuzzy_score": round(
                    sum(r.fuzzy_score for r in system_results) / count, 2
                ),
                "avg_grounding_score": round(
                    sum(r.grounding_score for r in system_results) / count, 2
                ),
                "avg_response_time_ms": round(
                    sum(r.response_time_ms for r in system_results) / count, 2
                ),
                "by_category": self._aggregate_by_field(system_results, "category"),
                "by_difficulty": self._aggregate_by_field(system_results, "difficulty"),
            }

        competitor_id = self.config.competitor
        james_bot_id = next(
            (s["id"] for s in self.config.systems if s["adapter"] == "james_bot"),
            None,
        )

        comparison = {}
        if james_bot_id and competitor_id in aggregated:
            comparison = {
                "james_bot_accuracy_fuzzy_pct": aggregated[james_bot_id]["accuracy_fuzzy_pct"],
                "competitor_accuracy_fuzzy_pct": aggregated[competitor_id]["accuracy_fuzzy_pct"],
                "accuracy_delta_pct": round(
                    aggregated[james_bot_id]["accuracy_fuzzy_pct"]
                    - aggregated[competitor_id]["accuracy_fuzzy_pct"],
                    2,
                ),
                "james_bot_grounding_score": aggregated[james_bot_id]["avg_grounding_score"],
                "competitor_grounding_score": aggregated[competitor_id]["avg_grounding_score"],
            }

        return {
            "benchmark": {
                "name": self.config.name,
                "version": self.config.version,
                "goal": self.config.goal,
                "dataset": self.dataset.name,
                "run_timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "aggregated_metrics": aggregated,
            "comparison": comparison,
            "detailed_results": [asdict(r) for r in results],
        }

    def _aggregate_by_field(
        self, results: list[QuestionResult], field: str
    ) -> dict[str, dict[str, float]]:
        groups: dict[str, list[QuestionResult]] = {}
        for result in results:
            key = getattr(result, field)
            groups.setdefault(key, []).append(result)

        output: dict[str, dict[str, float]] = {}
        for key, group in groups.items():
            count = len(group)
            output[key] = {
                "accuracy_fuzzy_pct": round(
                    sum(r.accuracy_fuzzy for r in group) / count * 100, 2
                ),
                "avg_grounding_score": round(
                    sum(r.grounding_score for r in group) / count, 2
                ),
            }
        return output

    def _save_report(self, report: dict[str, Any]) -> None:
        self.config.results_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        if "json" in self.config.report_formats:
            json_path = self.config.results_dir / f"benchmark_report_{timestamp}.json"
            json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            self.console.print(f"[green]Saved JSON report:[/green] {json_path}")

        if "markdown" in self.config.report_formats:
            md_path = self.config.results_dir / f"benchmark_report_{timestamp}.md"
            md_path.write_text(self._to_markdown(report), encoding="utf-8")
            self.console.print(f"[green]Saved Markdown report:[/green] {md_path}")

    def _to_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            f"# {report['benchmark']['name']}",
            "",
            f"**Run:** {report['benchmark']['run_timestamp']}",
            f"**Dataset:** {report['benchmark']['dataset']}",
            "",
            "## Benchmark Goal",
            report["benchmark"]["goal"],
            "",
            "## Aggregated Metrics",
            "",
            "| System | Strict Accuracy | Fuzzy Accuracy | Avg Grounding | Avg Response (ms) |",
            "|--------|-----------------|----------------|---------------|-------------------|",
        ]

        for system_id, metrics in report["aggregated_metrics"].items():
            lines.append(
                f"| {metrics['system_name']} | {metrics['accuracy_strict_pct']}% | "
                f"{metrics['accuracy_fuzzy_pct']}% | {metrics['avg_grounding_score']} | "
                f"{metrics['avg_response_time_ms']} |"
            )

        if report.get("comparison"):
            comp = report["comparison"]
            lines.extend(
                [
                    "",
                    "## James Bot vs Competitor",
                    "",
                    f"- Accuracy delta (fuzzy): **{comp['accuracy_delta_pct']}%**",
                    f"- James Bot grounding: **{comp['james_bot_grounding_score']}**",
                    f"- Competitor grounding: **{comp['competitor_grounding_score']}**",
                ]
            )

        lines.extend(["", "## Per-Question Results", ""])
        for item in report["detailed_results"]:
            status = "PASS" if item["accuracy_fuzzy"] else "FAIL"
            lines.append(
                f"- [{status}] `{item['system_id']}` **{item['question_id']}**: "
                f"fuzzy={item['fuzzy_score']:.1f}, grounding={item['grounding_score']:.1f}"
            )

        return "\n".join(lines) + "\n"

    def _print_summary(self, report: dict[str, Any]) -> None:
        self.console.print("\n[bold]Benchmark Summary[/bold]")
        for system_id, metrics in report["aggregated_metrics"].items():
            self.console.print(
                f"  {metrics['system_name']}: "
                f"fuzzy accuracy={metrics['accuracy_fuzzy_pct']}%, "
                f"grounding={metrics['avg_grounding_score']}"
            )

        if report.get("comparison"):
            delta = report["comparison"]["accuracy_delta_pct"]
            self.console.print(f"\n[bold]James Bot advantage:[/bold] {delta}% fuzzy accuracy")
