# Privacy model

## What stays local

- raw prompts
- source code
- ticket references
- personal notes
- full AI conversations

## What leaves the laptop

Only a structured summary report such as:

- topic percentages
- depth percentages
- question level percentages
- question mode percentages
- component percentages
- confidence
- short assumptions

## Why this is not full anonymity

Stable hashed identifiers are best described as **pseudonymous**, not anonymous.
A small team can still be deanonymized indirectly if the dashboard is careless.

## Controls

- do not expose per-person topic charts to the manager
- suppress small groups
- separate completion tracking from content access
- forbid raw free-text export by default
- use an org secret when deriving stable hashes
- rotate the salt only with a migration plan

## Threat model

This repository reduces risk from casual over-collection.
It does not solve all insider risk or legal/compliance questions.
If you deploy this in a real company, involve legal, HR, and security early.