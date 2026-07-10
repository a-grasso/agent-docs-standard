---
kind: module
title: requira
up: ../AGENTS.md
ref:
  - { at: ../functions/AGENTS.md, hint: source of telemetry.ingested events; owns alert dispatch }
docs: ./docs
updated: 2026-07-10
---

# requira

## Purpose
The rule engine ("requirements/rules"). Subscribes to `telemetry.ingested` events, evaluates
operator-defined alert rules against readings, and raises alerts (dispatched by `functions`).
Also back-tests rules against historical telemetry.

## Working here
- **Build / test:** `pnpm --filter requira build|test`
- **Entry points:** `src/engine.ts` (evaluation loop), `src/rules/` (rule primitives).
- **Local run:** `pnpm --filter requira dev` (replays a fixture event stream).

## Map
- `src/` — engine and rule primitives.
- `docs/adr/` — module decisions (e.g. the evaluation model).
- `docs/plans/`, `docs/reviews/` — **ephemeral**, feature-scoped. Currently: `alert-throttling`.

## Navigation (for agents)
- Follow **`up:`** for platform conventions and the append-only guarantee that makes back-
  testing sound (root ADR-0003).
- Follow **`ref:`** to `functions` for the event contract we consume and the dispatch path our
  alerts flow into (`docs/references/event-schema.md` there).
- **In-flight feature:** read `docs/plans/alert-throttling-plan.md` before touching throttling
  code; its review is in `docs/reviews/`.

## Constraints
- **Pure evaluation:** rule evaluation MUST be a pure function of (rule, readings) — no I/O in
  the evaluator — so back-tests and live runs agree (module ADR-0001).
- **Contracts only:** consume events, don't import `functions` source (root ADR-0002).
