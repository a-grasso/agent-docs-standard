---
status: active
feature: alert-throttling
created: 2026-07-09
---

# Review: alert throttling

## What changed
Implements `docs/plans/alert-throttling-plan.md`: adds `src/rules/throttle.ts` and threads
`SuppressionState` through the engine loop. Back-test harness added.

## Findings
| Severity | Location | Finding | Status |
|----------|----------|---------|--------|
| high | `src/rules/throttle.ts:41` | Cooldown compared against `Date.now()` inside the evaluator — breaks purity (ADR-0001); live and back-test diverge. | open |
| med  | `src/engine.ts:88` | Suppression state never evicted — unbounded growth. Plan called for TTL. | open |
| low  | `src/rules/throttle.ts:12` | `clear+refire` behavior undocumented; plan left it open. | open |

## Verdict
**Needs work.** The high finding defeats the feature's own goal (reproducible back-tests). Pass
window bounds in as time; remove the clock read. Re-review after fixes.

## Durable takeaways
- The purity rule (ADR-0001) is easy to violate accidentally with stateful features. When this
  lands, **distill** into **requira ADR-0002** ("suppression state is an evaluator input") and
  add a lint rule banning `Date.now()` under `src/rules/`. Then garbage-collect this review and
  its plan (standard §7.4).
