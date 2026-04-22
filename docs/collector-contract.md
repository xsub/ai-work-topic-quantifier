# Collector contract

This repository does not implement the uploader, but the uploader contract is intentionally simple.

## Content upload

### Request body

```json
{
  "schema_version": "1.0.0",
  "submitter_hash": "0fcb4d80a1d7e0e5",
  "team": "platform",
  "report_kind": "weekly",
  "timebox": {
    "start": "2026-04-14",
    "end": "2026-04-20"
  },
  "payload": { "...weekly report JSON..." }
}
```

### Server-side rules

- store `submitter_hash`
- store `submitted_at`
- validate schema
- reject malformed percentage sections
- never store raw prompts or chat logs
- support immutable content records per `(submitter_hash, timebox)`

## Completion registry

Use a separate table or service for completion status:

- employee identifier
- team
- week
- submitted boolean
- submitted_at

The manager may need visibility into completion status. That does not require access to content records.

## Suppression rules

The dashboard should suppress or merge views when:

- fewer than 5 reports are present
- a subgroup is small enough for easy deanonymization
- a dominant component or topic obviously points to a single person