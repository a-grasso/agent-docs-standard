---
id: ADR-0001
title: Rules are pure functions over a windowed reading stream
status: accepted
date: 2026-06-25
decides: centersight/platform#147
normative-in: ../../AGENTS.md
supersedes: -
superseded-by: -
---

# ADR-0001 (requira): Rules are pure functions over a windowed reading stream

## Context
We must evaluate the same rules two ways: **live** (as events arrive) and **back-tested**
(replayed over history). If evaluation depended on wall-clock time or external I/O, the two
paths would diverge and operators couldn't trust a back-test.

## Decision
A rule is a **pure function** `(rule, window) -> AlertDecision`, where `window` is an immutable
slice of readings for a sensor/metric. Time is an input (the window bounds), never read from the
clock inside the evaluator. All I/O (fetching windows, raising alerts) lives outside the
evaluator, in the engine loop.

## Consequences
- **Positive:** identical results live and in back-test; trivially unit-testable; parallelizable.
- **Negative / cost:** the engine loop must assemble windows before calling the evaluator.
- **Follow-ups:** the `alert-throttling` feature adds stateful suppression - see its plan for
  how it stays compatible with purity (state passed in, not read inside).

## Alternatives considered
- **Evaluator reads DB/clock directly** - rejected: non-reproducible, untestable, live≠backtest.
