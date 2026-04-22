#!/usr/bin/env python3
"""
Prepare Git grounding context for a developer's local report.

This script reads Git history for a date range and optionally maps paths to named
components using a simple glob-based component map.

Example:
    python scripts/prepare_git_context.py \
      --repo /path/to/repo \
      --since 2026-04-14 \
      --until 2026-04-20 \
      --author "Alice Example" \
      --component-map config/component_map.example.json \
      --output out/git_context.json
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


def run_git(repo: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def load_component_map(path: Path | None) -> dict[str, list[str]]:
    if path is None:
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    mapping: dict[str, list[str]] = {}
    for entry in raw.get("components", []):
        mapping[entry["name"]] = entry.get("match", [])
    return mapping


def match_component(file_path: str, component_map: dict[str, list[str]]) -> str | None:
    for component_name, patterns in component_map.items():
        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return component_name
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--since", required=True)
    parser.add_argument("--until", required=True)
    parser.add_argument("--author")
    parser.add_argument("--component-map", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    git_args = [
        "log",
        f"--since={args.since}",
        f"--until={args.until}",
        "--numstat",
        "--format=COMMIT%x09%H%x09%ad%x09%s",
        "--date=short",
    ]
    if args.author:
        git_args.append(f"--author={args.author}")

    output = run_git(args.repo, git_args)
    component_map = load_component_map(args.component_map)

    commit_count = 0
    additions = 0
    deletions = 0
    files = {}
    top_paths = defaultdict(lambda: {"additions": 0, "deletions": 0})
    component_stats = defaultdict(lambda: {"files": set(), "additions": 0, "deletions": 0})

    for line in output.splitlines():
        if not line.strip():
            continue
        if line.startswith("COMMIT\t"):
            commit_count += 1
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add_s, del_s, path = parts
        if add_s == "-" or del_s == "-":
            continue
        try:
            add_i = int(add_s)
            del_i = int(del_s)
        except ValueError:
            continue
        additions += add_i
        deletions += del_i
        files[path] = True
        top_paths[path]["additions"] += add_i
        top_paths[path]["deletions"] += del_i
        component = match_component(path, component_map)
        if component:
            component_stats[component]["files"].add(path)
            component_stats[component]["additions"] += add_i
            component_stats[component]["deletions"] += del_i

    rendered_component_stats: dict[str, Any] = {}
    for name, stats in component_stats.items():
        rendered_component_stats[name] = {
            "files": len(stats["files"]),
            "additions": stats["additions"],
            "deletions": stats["deletions"],
        }

    result = {
        "repo_path": str(args.repo),
        "author": args.author or "",
        "since": args.since,
        "until": args.until,
        "commit_count": commit_count,
        "files_touched": len(files),
        "additions": additions,
        "deletions": deletions,
        "top_paths": [
            {"path": path, "additions": vals["additions"], "deletions": vals["deletions"]}
            for path, vals in sorted(
                top_paths.items(),
                key=lambda item: item[1]["additions"] + item[1]["deletions"],
                reverse=True,
            )[:10]
        ],
        "component_stats": rendered_component_stats,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote Git context to {args.output}")


if __name__ == "__main__":
    main()