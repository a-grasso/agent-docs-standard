// Enforcer for the "Idempotent handlers" constraint in ../AGENTS.md.
//
// Governing doc: module ADR-0001 - the bus delivers at-least-once, so redelivery must be a
// no-op. The second half matters as much as the first: a duplicate must publish nothing, or
// every consumer downstream inherits the duplicate.

import { describe, expect, it } from "vitest";
import { ingest } from "../src/ingest";
import { fakeBus, fakeStore, reading } from "./fixtures";

describe("ingestion is idempotent on reading_id", () => {
  it("stores a redelivered reading once", async () => {
    const store = fakeStore();
    await ingest(reading, store, fakeBus());
    await ingest(reading, store, fakeBus());
    expect(store.size).toBe(1);
  });

  it("publishes telemetry.ingested once", async () => {
    const store = fakeStore();
    const bus = fakeBus();
    await ingest(reading, store, bus);
    await ingest(reading, store, bus);
    expect(bus.published).toHaveLength(1);
  });
});
