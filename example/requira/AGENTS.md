---
kind: module
title: requira
up: ../AGENTS.md
ref:
  - { at: ../functions/AGENTS.md, hint: source of telemetry.ingested events; owns alert dispatch }
docs: ./docs
---

# requira

## Purpose
The rule engine. Subscribes to `telemetry.ingested` events, evaluates
operator-defined alert rules against readings, and raises alerts (dispatched by `functions`).
Also back-tests rules against historical telemetry.

## Working here
- **Build / test:** `pnpm --filter requira build|test`
- **Entry points:** `src/engine.ts` (evaluation loop), `src/rules/` (rule primitives).
- **Local run:** `pnpm --filter requira dev` (replays a fixture event stream).

## Constraints
- **Pure evaluation:** rule evaluation is a pure function of (rule, readings), with no I/O in
  the evaluator, so that back-tests and live runs agree. Module ADR-0001; enforced by
  [`test/purity.test.ts`](test/purity.test.ts) and the `no-io-in-evaluator` ESLint rule.
- **Contracts only:** consume events, do not import `functions` source. Root ADR-0002;
  enforced by the ESLint `no-restricted-imports` rule.

## Decisions in force
- Evaluation is pure and I/O-free, so back-tests are trustworthy (module ADR-0001).
- Alerts are raised here and dispatched by `functions`; this module never delivers
  (root ADR-0002).
- Suppression state is passed into the evaluator and persisted by the engine loop, never read
  inside the evaluator: that is what keeps throttling compatible with purity
  (decision log, 2026-08-30).
- A cleared-then-refired condition re-alerts immediately rather than waiting out the cooldown
  (decision log, 2026-08-30).
