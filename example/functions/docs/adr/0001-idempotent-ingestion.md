---
id: ADR-0001
title: Idempotent ingestion keyed on reading_id
status: accepted
date: 2026-06-22
normative-in: ../references/event-schema.md
revisit-when: the bus offers exactly-once delivery at the plant edge, not only within a region
supersedes: -
superseded-by: -
---

# ADR-0001 (functions): Idempotent ingestion keyed on reading_id

## Context
The event bus and the HTTP ingress both deliver **at-least-once**. Naive ingestion would write
duplicate readings on retry, corrupting counts and, combined with append-only storage
(root ADR-0003), leaving no way to "clean up" the duplicates.

## Decision
Ingestion is **idempotent**, keyed on the producer-supplied `reading_id`. A conditional write
("insert if `reading_id` absent") drops duplicates. `telemetry.ingested` is published only on a
first successful insert.

## Consequences
- **Positive:** retries are safe; downstream (`requira`) sees each reading once.
- **Negative / cost:** producers MUST supply a stable `reading_id`; documented in the event
  schema.
- **Follow-ups:** the dedupe index is provisioned in `infra`.

## Alternatives considered
- **Best-effort dedupe by (sensor, timestamp)** - rejected: two distinct readings can share a
  millisecond; would silently drop data.
