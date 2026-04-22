# Architecture

## Design target

A privacy-preserving engineering analytics flow that gives a manager a useful topic picture after the first week without collecting raw AI prompts centrally.

## Logical components

1. **Local developer workspace**
   - developer activity note
   - optional local chat export or local session notes
   - optional Git-derived context
   - prompt builder
   - Claude classification step
   - JSON report file

2. **Submission layer**
   - pseudonymous identifier
   - upload endpoint or drop-folder
   - timestamped receipt
   - content store

3. **Team aggregation layer**
   - report validation
   - percentage sanity checks
   - aggregation
   - Markdown and JSON summary generation

4. **Manager dashboard**
   - team-level topic and depth distributions
   - completion rate
   - no raw prompts
   - no per-person topic charts

## Data flow

```text
Developer note + Git context
        ↓
  build_prompt.py
        ↓
     Claude local
        ↓
 structured JSON report
        ↓
 pseudonymous submission
        ↓
 aggregate_reports.py
        ↓
 team_summary.json + team_summary.md
```

## Separation of concerns

The architecture deliberately separates:

- **content records**: structured topic reports keyed by pseudonymous hash
- **completion records**: whether a report was submitted for a given timebox
- **identity mapping**: any mapping from a human identity to a stable hash

A direct join between manager-facing completion tracking and manager-facing content views should be avoided.

## Optional telemetry merge

If the organization has vendor telemetry such as Claude Enterprise Analytics or Claude Code Analytics, merge those metrics only at the **team-week** level. Use them for adoption and volume. Do not confuse them with semantic topic classification.

## Why Git grounding exists

Git activity is not a substitute for semantic understanding. It exists to answer a narrower question:

> Which technical components were probably involved in the week being classified?

That is enough to anchor component share and reduce fantasy in the classification output.