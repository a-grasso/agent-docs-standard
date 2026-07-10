# Event contracts (published by `functions`)

These are the **boundary** other modules depend on (root ADR-0002). Treat them as versioned
contracts: additive changes are minor; removals/renames require a new major and a note to every
`ref:`/consumer.

## `telemetry.ingested` (v1)
Published once per newly-persisted reading (idempotent — see module ADR-0001).

```json
{
  "event": "telemetry.ingested",
  "version": 1,
  "reading_id": "r_01HZ...",         // stable, producer-supplied; dedupe key
  "sensor_id": "sns_4412",
  "plant_id": "plant_muc",
  "metric": "bearing_temp_c",
  "value": 74.2,
  "observed_at": "2026-07-10T09:14:22.031Z",  // ISO-8601 UTC (decision log)
  "correction_of": null               // reading_id this corrects, or null (root ADR-0003)
}
```

**Consumers:** `requira` (rule evaluation). See `../../requira/AGENTS.md`.
