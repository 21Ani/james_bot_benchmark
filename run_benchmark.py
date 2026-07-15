#!/usr/bin/env python3
"""CLI entry point for James Bot benchmarking study."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.config import BenchmarkConfig
from src.dataset import BenchmarkDataset
from src.runner import BenchmarkRunner


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run James Bot benchmarking study (QE Assignment)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to benchmark config YAML",
    )
    args = parser.parse_args()

    load_dotenv()

    if not args.config.exists():
        print(f"Config not found: {args.config}", file=sys.stderr)
        return 1

    config = BenchmarkConfig.from_yaml(args.config)
    dataset = BenchmarkDataset.load(config.dataset_path, config.documents_dir)

    print(f"Benchmark: {config.name}")
    print(f"Dataset: {dataset.name} ({len(dataset.questions)} questions)")
    print(f"Systems: {', '.join(s['name'] for s in config.systems)}")
    print()

    runner = BenchmarkRunner(config, dataset)
    runner.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
