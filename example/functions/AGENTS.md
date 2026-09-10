---
kind: module
title: functions
up: ../AGENTS.md
ref:
  - { at: ../requira/AGENTS.md, hint: consumes the telemetry.ingested events we publish }
dep:
  - { id: centersight-api, at: https://centersight-api-doc.com, kind: external-doc, hint: REST contract we serve for alert dispatch }
docs: ./docs
updated: 2026-07-10
---

# functions

## Purpose
Backend serverless functions. Owns two flows: **telemetry ingestion** (validate incoming
sensor readings, persist them append-only, publish `telemetry.ingested` events) and **alert
dispatch** (deliver alerts raised by `requira` to email/webhook channels).

## Working here
- **Build / test:** `pnpm --filter functions build|test`
- **Entry points:** `src/ingest.ts` (ingestion handler), `src/dispatch.ts` (alert dispatch).
- **Local run:** `pnpm --filter functions dev` (uses the local event-bus emulator).

## Constraints
- **Append-only ingestion:** never update or delete a reading; corrections are new readings.
  Root ADR-0003; enforced by the store's write-once grant and `test/ingest.contract.test.ts`.
- **Idempotent handlers:** the bus delivers at-least-once; ingestion dedupes on `reading_id`.
  Module ADR-0001; enforced by `test/ingest.idempotency.test.ts`.
- **Contracts only:** do not import `requira`/`ui` source; communicate via events or the API.
  Root ADR-0002; enforced by the ESLint `no-restricted-imports` rule.
- **Persist before publish:** a reading is stored before its event is published. (unenforced)

## Traps
- A retried delivery arrives with a **new** `message_id` but the same `reading_id`. Dedupe on
  `reading_id`; `message_id` looks like the natural key and is not.
- The local emulator accepts readings the deployed validator rejects: it does not check unit
  codes. A payload that works in `pnpm dev` can still 400 in production.
- `dispatch.ts` retries per channel, not per alert. Adding a channel to an alert already in
  flight dispatches to it too, which surprises tests that count deliveries.
