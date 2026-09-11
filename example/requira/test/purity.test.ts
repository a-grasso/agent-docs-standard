// Enforcer for the "Pure evaluation" constraint in ../AGENTS.md.
//
// Governing doc: module ADR-0001 - the evaluator is (rule, window[, state]) -> decision,
// with no I/O. If this test can be made to pass with an evaluator that touches the network,
// the clock or the store, the constraint has stopped being enforced.

import { describe, expect, it, vi } from "vitest";
import { evaluate } from "../src/rules";
import { rule, window } from "./fixtures";

describe("evaluate is pure", () => {
  it("is deterministic: same input, same decision", () => {
    expect(evaluate(rule, window, undefined)).toEqual(evaluate(rule, window, undefined));
  });

  it("does not mutate its arguments", () => {
    const frozen = Object.freeze(structuredClone(window));
    expect(() => evaluate(rule, frozen, undefined)).not.toThrow();
  });

  it("performs no I/O", () => {
    const fetch = vi.spyOn(globalThis, "fetch");
    const now = vi.spyOn(Date, "now");
    evaluate(rule, window, undefined);
    expect(fetch).not.toHaveBeenCalled();
    expect(now).not.toHaveBeenCalled(); // time is an input, not an ambient read
  });
});
