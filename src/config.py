"""Configuration loading and validation."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")


def _resolve_env(value: Any) -> Any:
    if isinstance(value, str):
        def replacer(match: re.Match[str]) -> str:
            key = match.group(1)
            return os.getenv(key, "")

        return _ENV_PATTERN.sub(replacer, value)
    if isinstance(value, dict):
        return {k: _resolve_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env(item) for item in value]
    return value


@dataclass
class BenchmarkConfig:
    name: str
    version: str
    goal: str
    competitor: str
    systems: list[dict[str, str]]
    dataset_path: Path
    documents_dir: Path
    metrics: list[str]
    fuzzy_threshold: int
    grounding_threshold: int
    results_dir: Path
    report_formats: list[str]
    adapters: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: Path) -> "BenchmarkConfig":
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        raw = _resolve_env(raw)

        benchmark = raw["benchmark"]
        dataset = raw["dataset"]
        evaluation = raw["evaluation"]
        output = raw["output"]

        root = path.parent
        return cls(
            name=benchmark["name"],
            version=benchmark["version"],
            goal=benchmark["goal"].strip(),
            competitor=benchmark["competitor"],
            systems=benchmark["systems"],
            dataset_path=root / dataset["path"],
            documents_dir=root / dataset["documents_dir"],
            metrics=evaluation["metrics"],
            fuzzy_threshold=evaluation["fuzzy_threshold"],
            grounding_threshold=evaluation["grounding_threshold"],
            results_dir=root / output["results_dir"],
            report_formats=output["report_format"],
            adapters=raw.get("adapters", {}),
        )
