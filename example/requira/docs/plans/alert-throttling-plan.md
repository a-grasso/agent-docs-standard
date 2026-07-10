---
status: active
feature: alert-throttling
created: 2026-07-06
---

# Plan: alert throttling

## Goal
Stop alert storms: when a rule fires repeatedly within a window, raise **one** alert and
suppress the rest until it clears or a cooldown elapses. Done = a flapping sensor produces ≤1
alert per cooldown, and back-tests over last month's data reproduce identical suppression.

## Context an agent needs
- Touches: `requira/src/engine.ts`, new `requira/src/rules/throttle.ts`.
- Governing constraints: module **ADR-0001** (evaluation must stay pure) and root **ADR-0003**
  (append-only history makes back-testing sound).
- Upstream/lateral (`ref:`): `functions` owns dispatch — throttling happens **before** we hand
  an alert to it; no change to the event contract expected.

## Steps
1. Add a `SuppressionState` value passed *into* the evaluator (keeps it pure per ADR-0001).
2. Implement `throttle(rule, window, state) -> { decision, nextState }`.
3. Engine loop persists `nextState` per (rule, sensor) outside the evaluator.
4. Back-test harness: replay June telemetry, assert ≤1 alert/cooldown.

## Risks & open questions
- **Cooldown vs. clear-then-refire:** should a cleared-then-refired condition re-alert
  immediately or wait out the cooldown? → leaning "re-alert on clear+refire". **Decide & record.**
- State growth per (rule, sensor) — cap with TTL eviction.

## Decisions made while planning
- Suppression state is an **evaluator input**, not read inside it — preserves ADR-0001 purity.
  → **DISTILL** into a follow-up ADR when this lands (candidate: requira ADR-0002).
