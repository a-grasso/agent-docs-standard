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

## Constraints
- **Pure evaluation:** rule evaluation MUST be a pure function of (rule, readings) — no I/O in
  the evaluator — so back-tests and live runs agree (module ADR-0001).
- **Contracts only:** consume events, don't import `functions` source (root ADR-0002).
