# Rollout plan

## Objective

Have a manager-visible team-level AI work map after the first week.

## Before day one

- choose the taxonomy
- define the component map
- generate or provision the org hash secret
- decide whether reporting is daily or weekly
- communicate the privacy model clearly

## Day one

- distribute the repository
- run `pseudonymous_id.py`
- create a local output directory for each developer
- test `prepare_git_context.py` against one repository
- render the first prompt with `build_prompt.py`

## During the first week

- developers generate local daily or weekly reports
- no raw prompts are uploaded
- if needed, refine the component map after day two

## End of the first week

- collect all JSON reports
- run `aggregate_reports.py`
- review the Markdown summary
- decide whether the taxonomy is too coarse or too fine

## What success looks like

By the end of week one, you can answer:

- Which technical topics dominate AI-assisted work?
- What share is foundational?
- What level are the questions?
- Which components are driving the activity?
- Is AI mostly used for debugging, design, implementation, or testing?