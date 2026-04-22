#!/usr/bin/env python3
"""
Render a daily or weekly Claude prompt from local files.

Example:
    python scripts/build_prompt.py \
      --mode weekly \
      --activity-note examples/developer_activity_note.example.md \
      --git-context examples/git_context.example.json \
      --output out/weekly_prompt.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]


def load_text(path: Optional[Path], default: str) -> str:
    if path is None:
        return default
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> str:
    return json.dumps(json.loads(path.read_text(encoding="utf-8")), indent=2, ensure_ascii=False)


def render_template(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["daily", "weekly"], required=True)
    parser.add_argument("--activity-note", type=Path, required=True)
    parser.add_argument("--git-context", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    prompt_name = "daily_local_report_prompt.md" if args.mode == "daily" else "weekly_local_report_prompt.md"
    schema_name = "developer_daily_report.schema.json" if args.mode == "daily" else "developer_weekly_report.schema.json"

    template = (ROOT / "prompts" / prompt_name).read_text(encoding="utf-8")
    schema_path = args.schema or (ROOT / "schemas" / schema_name)

    replacements = {
        "TOPIC_TAXONOMY": load_json(ROOT / "config" / "topic_taxonomy.json"),
        "DEPTH_TAXONOMY": load_json(ROOT / "config" / "depth_taxonomy.json"),
        "QUESTION_LEVELS": load_json(ROOT / "config" / "question_levels.json"),
        "QUESTION_MODES": load_json(ROOT / "config" / "question_modes.json"),
        "SCHEMA": load_json(schema_path),
        "ACTIVITY_NOTE": load_text(args.activity_note, ""),
        "GIT_CONTEXT": load_json(args.git_context) if args.git_context else "No Git context supplied."
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_template(template, replacements), encoding="utf-8")
    print(f"Wrote prompt to {args.output}")


if __name__ == "__main__":
    main()