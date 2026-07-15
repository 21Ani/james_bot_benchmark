#!/usr/bin/env python3
"""Compare two benchmark runs to track James Bot improvements over time."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compare(baseline: dict, current: dict) -> str:
    lines = [
        "# Benchmark Run Comparison",
        "",
        f"**Baseline:** {baseline['benchmark']['run_timestamp']}",
        f"**Current:** {current['benchmark']['run_timestamp']}",
        "",
        "| System | Metric | Baseline | Current | Delta |",
        "|--------|--------|----------|---------|-------|",
    ]

    all_systems = set(baseline["aggregated_metrics"]) | set(current["aggregated_metrics"])
    metrics = [
        ("accuracy_fuzzy_pct", "Fuzzy Accuracy %"),
        ("accuracy_strict_pct", "Strict Accuracy %"),
        ("avg_grounding_score", "Avg Grounding"),
        ("avg_response_time_ms", "Avg Response (ms)"),
    ]

    for system_id in sorted(all_systems):
        base = baseline["aggregated_metrics"].get(system_id, {})
        curr = current["aggregated_metrics"].get(system_id, {})
        name = curr.get("system_name") or base.get("system_name") or system_id

        for key, label in metrics:
            b_val = base.get(key, 0)
            c_val = curr.get(key, 0)
            delta = round(c_val - b_val, 2)
            sign = "+" if delta > 0 else ""
            lines.append(f"| {name} | {label} | {b_val} | {c_val} | {sign}{delta} |")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two benchmark JSON reports")
    parser.add_argument("baseline", type=Path, help="Earlier benchmark report JSON")
    parser.add_argument("current", type=Path, help="Newer benchmark report JSON")
    parser.add_argument("-o", "--output", type=Path, help="Save comparison markdown")
    args = parser.parse_args()

    for path in (args.baseline, args.current):
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            return 1

    report = compare(load_report(args.baseline), load_report(args.current))
    print(report)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Saved: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
