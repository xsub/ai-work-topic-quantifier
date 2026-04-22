#!/usr/bin/env python3
"""
Aggregate developer weekly or daily JSON reports into a team summary.

Example:
    python scripts/aggregate_reports.py \
      --reports-dir team_reports \
      --output-prefix out/team_week_17
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_reports(reports_dir: Path) -> list[dict[str, Any]]:
    reports = []
    for path in sorted(reports_dir.glob("*.json")):
        try:
            reports.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    return reports


def validate_percent_section(section: dict[str, Any], label: str, path: str) -> None:
    if not isinstance(section, dict):
        raise SystemExit(f"{path}: {label} must be an object")
    total = round(sum(float(v) for v in section.values()))
    if total != 100:
        raise SystemExit(f"{path}: {label} must sum to 100, got {total}")


def avg_sections(reports: list[dict[str, Any]], key: str) -> dict[str, float]:
    totals = defaultdict(float)
    count = 0
    for report in reports:
        section = report.get(key)
        if not section:
            continue
        count += 1
        for subkey, value in section.items():
            totals[subkey] += float(value)
    if count == 0:
        return {}
    return {k: round(v / count, 2) for k, v in sorted(totals.items())}


def top_items(section: dict[str, float], n: int = 5) -> list[tuple[str, float]]:
    return sorted(section.items(), key=lambda kv: kv[1], reverse=True)[:n]


def build_markdown(summary: dict[str, Any]) -> str:
    lines = []
    lines.append("# Team AI work summary")
    lines.append("")
    lines.append(f"- Reports processed: **{summary['reports_count']}**")
    lines.append(f"- Average foundational topic share: **{summary['fundamental_topic_share_avg']}%**")
    lines.append(f"- Developers over threshold ({summary['foundational_threshold']}% foundational): **{summary['developers_over_threshold']}**")
    lines.append("")

    lines.append("## Top topics")
    for name, value in top_items(summary["topic_share_avg"]):
        lines.append(f"- {name}: {value}%")
    lines.append("")

    lines.append("## Depth mix")
    for name, value in summary["depth_share_avg"].items():
        lines.append(f"- {name}: {value}%")
    lines.append("")

    lines.append("## Question levels")
    for name, value in summary["question_level_share_avg"].items():
        lines.append(f"- {name}: {value}%")
    lines.append("")

    if summary["component_share_avg"]:
        lines.append("## Top components")
        for name, value in top_items(summary["component_share_avg"]):
            lines.append(f"- {name}: {value}%")
        lines.append("")

    lines.append("## Interpretation")
    top_topic_name, top_topic_value = top_items(summary["topic_share_avg"], 1)[0]
    lines.append(
        f"The dominant AI-assisted work topic this period was **{top_topic_name}** at **{top_topic_value}%** on average. "
        f"The team is currently weighted toward **{max(summary['depth_share_avg'], key=summary['depth_share_avg'].get)}** work."
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    parser.add_argument("--foundational-threshold", type=float, default=20.0)
    args = parser.parse_args()

    reports = load_reports(args.reports_dir)
    if not reports:
        raise SystemExit("No JSON reports found")

    for idx, report in enumerate(reports):
        validate_percent_section(report["topic_share"], "topic_share", f"report[{idx}]")
        validate_percent_section(report["depth_share"], "depth_share", f"report[{idx}]")
        validate_percent_section(report["question_level_share"], "question_level_share", f"report[{idx}]")
        validate_percent_section(report["question_mode_share"], "question_mode_share", f"report[{idx}]")
        if report.get("component_share"):
            validate_percent_section(report["component_share"], "component_share", f"report[{idx}]")

    fundamental_values = [float(report.get("fundamental_topic_share", 0.0)) for report in reports]
    summary = {
        "reports_count": len(reports),
        "foundational_threshold": args.foundational_threshold,
        "topic_share_avg": avg_sections(reports, "topic_share"),
        "depth_share_avg": avg_sections(reports, "depth_share"),
        "question_level_share_avg": avg_sections(reports, "question_level_share"),
        "question_mode_share_avg": avg_sections(reports, "question_mode_share"),
        "component_share_avg": avg_sections(reports, "component_share"),
        "fundamental_topic_share_avg": round(sum(fundamental_values) / len(fundamental_values), 2),
        "developers_over_threshold": sum(1 for value in fundamental_values if value >= args.foundational_threshold),
    }

    summary_json_path = Path(str(args.output_prefix) + ".summary.json")
    summary_md_path = Path(str(args.output_prefix) + ".summary.md")
    summary_json_path.parent.mkdir(parents=True, exist_ok=True)
    summary_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary_md_path.write_text(build_markdown(summary), encoding="utf-8")

    print(f"Wrote {summary_json_path}")
    print(f"Wrote {summary_md_path}")


if __name__ == "__main__":
    main()