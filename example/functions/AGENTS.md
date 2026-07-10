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

## Map
- `src/` — one file per handler; handlers are thin, logic in `src/domain/`.
- `docs/references/event-schema.md` — the published event contracts (the boundary from ADR-0002).
- `docs/adr/` — decisions scoped to this module.

## Navigation (for agents)
- Follow **`up:`** for platform conventions, commands, and the append-only rule (ADR-0003).
- Follow **`ref:`** to `requira` — it consumes our events; changing an event schema affects it.
- Follow **`dep:`** to the external API doc for the alert-dispatch REST contract we must satisfy.

## Constraints
- **Append-only ingestion:** never update/delete a reading; corrections are new readings
  (root ADR-0003).
- **Idempotent handlers:** the bus delivers at-least-once; ingestion must dedupe on
  `reading_id` (module ADR-0001).
- **Contracts only:** do not import `requira`/`ui` source; communicate via events/API
  (root ADR-0002).
