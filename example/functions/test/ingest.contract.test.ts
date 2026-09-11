// Enforcer for the "Append-only ingestion" constraint in ../AGENTS.md.
//
// Governing doc: root ADR-0003 - a reading is never updated or deleted; a correction is a
// new reading. The store's write-once IAM grant enforces this in production
// (../../infra/test/policy.tftest.hcl); this test enforces it against the handler, so the
// violation is caught before it reaches a grant that would reject it.

import { describe, expect, it } from "vitest";
import { ingest } from "../src/ingest";
import { fakeBus, fakeStore, reading } from "./fixtures";

describe("ingestion is append-only", () => {
  it("only ever inserts", async () => {
    const store = fakeStore();
    await ingest(reading, store, fakeBus());
    expect(store.calls.map((c) => c.op)).toEqual(["insertIfAbsent"]);
  });

  it("writes a correction as a new reading, leaving the original intact", async () => {
    const store = fakeStore();
    const correction = { ...reading, readingId: "r-2", value: 41.8, corrects: "r-1" };
    await ingest(reading, store, fakeBus());
    await ingest(correction, store, fakeBus());
    expect(store.get("r-1")?.value).toBe(reading.value);
    expect(store.get("r-2")?.corrects).toBe("r-1");
  });
});
