// Rule evaluation engine loop.
//
// Governing docs (see ../AGENTS.md):
//   - module ADR-0001: the evaluator is PURE - (rule, window[, state]) -> decision.
//     All I/O (windows, state, dispatch) lives HERE in the loop, never in a rule.

import type { Reading, Rule, AlertSink, WindowStore, StateStore } from "./domain/types";
import { evaluate } from "./rules";

export async function onReading(
  reading: Reading,
  rules: Rule[],
  windows: WindowStore,
  state: StateStore, // suppression state persisted OUTSIDE the evaluator (keeps it pure)
  alerts: AlertSink, // -> functions dispatch; see ../functions/AGENTS.md
): Promise<void> {
  for (const rule of rules) {
    const window = await windows.forRule(rule, reading); // I/O: gather immutable slice
    const prev = await state.get(rule.id, reading.sensorId);

    const { decision, nextState } = evaluate(rule, window, prev); // PURE

    if (decision.raise) await alerts.raise(decision.alert);
    await state.put(rule.id, reading.sensorId, nextState);
  }
}
