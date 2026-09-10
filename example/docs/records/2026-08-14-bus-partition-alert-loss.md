# 2026-08-14: alerts lost during an event-bus partition

A network partition between the ingestion region and the bus lasted 41 minutes. Ingestion kept
accepting readings; `requira` stopped receiving `telemetry.ingested` events and raised no
alerts for the affected plants during that window.

## What happened

- **14:02** The bus's regional endpoint became unreachable from ingestion. Publishes began
  failing and were retried into the local buffer.
- **14:19** The buffer reached its cap. Publishes after this point were dropped, silently:
  the publish path logged failures but had no counter, so nothing alerted on it.
- **14:43** Connectivity returned. Buffered events drained; the dropped ones did not exist to
  drain.
- **15:30** A customer asked why a threshold breach visible in their own historian produced no
  CenterSight alert. That question is how we found out.

## What was affected

Readings were never lost: ingestion persists before publishing, so the store is complete for
the window. What was lost is the *evaluation* of those readings. Eleven plants, an estimated
four alerts that would have been raised.

## What changed as a result

- The publish path exports a dropped-publish counter, and the counter is alerted on.
- `requira` gained a back-fill entry point so an evaluation gap can be replayed from the store
  rather than reconstructed by hand.
- The buffer cap moved from a constant to a per-environment variable in `infra`.

The decision to keep at-least-once delivery rather than pursue exactly-once was re-examined
during the review and left standing (functions ADR-0001); this record is the evidence that
prompted the re-examination, not a reversal of it.
