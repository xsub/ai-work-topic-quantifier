# AI Work Topic Quantifier

A local-first, privacy-preserving quantification tool for engineering managers who want to understand **what their developers use AI for** without centralizing raw prompts, code, or chat histories.

The repository is designed for a week-one rollout:

- Developers generate a **local structured report** from their own AI-assisted work.
- The report can be grounded with **Git activity** and a **component map**.
- Only the structured JSON report is submitted upstream.
- The manager receives only **team-level aggregates**, not raw prompts and not per-person topic breakdowns.

This makes the tool useful on day one of a new role: by the end of the first week, you can already see which topics dominate, how much AI-assisted work is foundational vs. applied, and which components are absorbing most of the team's attention.

## What this measures

This repository separates three questions that are often incorrectly mixed together:

1. **Developer coverage**  
   What percentage of developers touched a topic at all?

2. **AI interaction share**  
   What percentage of AI-assisted work was about a topic?

3. **Depth of work**  
   How much of the work was foundational, applied implementation, or boilerplate?

The repository focuses on **AI interaction share** and **depth**, then derives team-level indicators from submitted weekly reports.

## Core ideas

- **Local-first classification**: raw prompts and local context stay on the developer's machine.
- **Structured output**: the developer submits strict JSON, not free-form prose.
- **Optional Git grounding**: touched files, churn, and components help anchor the classification.
- **Pseudonymous submission**: content records use a stable hash, not a human-readable identifier.
- **Manager-safe aggregation**: the team dashboard does not expose individual topic distributions.

## Repository layout

```text
ai-work-topic-quantifier/
├── README.md
├── LICENSE
├── .gitignore
├── config/
│   ├── topic_taxonomy.json
│   ├── question_modes.json
│   ├── question_levels.json
│   ├── depth_taxonomy.json
│   └── component_map.example.json
├── docs/
│   ├── architecture.md
│   ├── collector-contract.md
│   ├── privacy-model.md
│   └── rollout-plan.md
├── examples/
│   ├── developer_activity_note.example.md
│   ├── git_context.example.json
│   ├── developer_weekly_report.example.json
│   └── team_summary.example.json
├── prompts/
│   ├── daily_local_report_prompt.md
│   ├── weekly_local_report_prompt.md
│   └── manager_summary_prompt.md
├── schemas/
│   ├── developer_daily_report.schema.json
│   └── developer_weekly_report.schema.json
└── scripts/
    ├── build_prompt.py
    ├── prepare_git_context.py
    ├── pseudonymous_id.py
    └── aggregate_reports.py
```

## Week-one operating model

### Developer workflow

1. Create a local activity note for the day or week.
2. Run `prepare_git_context.py` to produce a Git-grounding JSON file.
3. Run `build_prompt.py` to render the full prompt.
4. Paste the prompt into Claude locally and save the returned JSON.
5. Submit only the JSON report.

### Manager workflow

1. Collect JSON reports for the team.
2. Run `aggregate_reports.py`.
3. Review the generated summary JSON and Markdown report.

## What the weekly report includes

Each weekly report captures:

- topic share
- depth share
- question level share
- question mode share
- optional component share
- confidence level
- bounded assumptions
- a single derived value: `fundamental_topic_share`

## Why not rely on self-report alone

This tool does **not** treat self-report as truth. It treats local reporting as one layer among several:

- developer activity note
- local AI-assisted summary
- optional Git grounding
- fixed taxonomy
- team-level aggregation

That is deliberate. Pure weekly self-report is too fragile. Pure central prompt mining is too invasive. The repository sits in the middle.

## Quick start

Generate a pseudonymous ID:

```bash
export AIQT_SALT="replace-with-org-secret"
python scripts/pseudonymous_id.py --identifier alice@example.com
```

Prepare Git context:

```bash
python scripts/prepare_git_context.py   --repo /path/to/repo   --since 2026-04-14   --until 2026-04-20   --author "Alice Example"   --component-map config/component_map.example.json   --output out/git_context.json
```

Render the weekly prompt:

```bash
python scripts/build_prompt.py   --mode weekly   --activity-note examples/developer_activity_note.example.md   --git-context out/git_context.json   --output out/weekly_prompt.md
```

Paste the generated prompt into Claude, save the JSON response, then aggregate all weekly reports:

```bash
python scripts/aggregate_reports.py   --reports-dir team_reports   --output-prefix out/team_week_17
```

This writes:

- `out/team_week_17.summary.json`
- `out/team_week_17.summary.md`

## Suggested first-week rollout

- Day 1: set the taxonomy and component map
- Day 1: distribute local instructions to developers
- Day 2-5: collect local daily or weekly reports
- Day 5: aggregate reports
- Day 6: review the first team-level topic picture

## Optional integration with Anthropic / Claude

Keep the core vendor-neutral.

If your organization uses Anthropic Enterprise or Claude Code analytics, you can merge **organization-level usage telemetry** with the local topic reports. Anthropic documents both an Enterprise Analytics API for aggregated usage and engagement data, and a Claude Code Analytics API for daily aggregated usage metrics. Those platform metrics are useful for adoption and usage volume, but they do **not** replace local semantic classification of topics. See Anthropic’s official docs and release notes for current details.

## Limits

- The classification is still an estimate.
- Git activity is only grounding context, not proof of topic intent.
- Manager-visible completion tracking should be stored separately from content records.
- Small teams need suppression rules to avoid accidental deanonymization.

