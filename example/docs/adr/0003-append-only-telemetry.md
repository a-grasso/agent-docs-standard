---
id: ADR-0003
title: Telemetry storage is append-only
status: accepted
date: 2026-06-15
supersedes: -
superseded-by: -
---

# ADR-0003: Telemetry storage is append-only

## Context
Operators and auditors must be able to trust that a historical reading is exactly what the
sensor reported. Correcting data in place would make dashboards and alert history
non-reproducible and would break the rule engine's back-testing (`requira`).

## Decision
The telemetry store is **append-only**. Ingestion (`functions`) MUST NOT update or delete
readings. Corrections are represented as new readings with a `correction_of` field; consumers
resolve the latest correction at read time.

## Consequences
- **Positive:** reproducible dashboards, auditable history, safe back-testing of alert rules.
- **Negative / cost:** read paths must resolve corrections; storage grows monotonically
  (mitigated by cold-tiering older partitions in `infra`).
- **Follow-ups:** `functions` ingestion pipeline enforces this; `requira` back-tests rely on it.

## Alternatives considered
- **Mutable rows with an audit table** - rejected: two sources of truth, easy to desync.
