// Telemetry ingestion handler.
//
// Governing docs (follow the pointers in ../AGENTS.md):
//   - root ADR-0003: telemetry is append-only - never update/delete a reading.
//   - module ADR-0001: idempotent, keyed on reading_id (bus is at-least-once).
//   - docs/references/event-schema.md: the telemetry.ingested contract.

import type { Reading, Bus, Store } from "./domain/types";

export async function ingest(reading: Reading, store: Store, bus: Bus): Promise<void> {
  // Idempotent conditional insert (module ADR-0001). Returns false if reading_id already exists.
  const inserted = await store.insertIfAbsent(reading.readingId, reading);
  if (!inserted) return; // duplicate delivery - drop silently, publish nothing.

  // Publish only on first successful insert (event-schema.md).
  await bus.publish("telemetry.ingested", { version: 1, ...reading });
}
