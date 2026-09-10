# Purpose and drivers

## Why CenterSight exists

Industrial plants instrument their machines long before anyone can act on what the instruments
say. Readings land in historians nobody opens, and the condition of a machine is known to the
one engineer who happens to remember it. CenterSight exists to turn that stream into something
an operator can act on within their shift.

## The forces the design is built against

**A reading is evidence, not an opinion.** Condition monitoring is used in disputes: warranty
claims, insurance, regulator questions. Evidence that can be edited is not evidence, which is
where the append-only constraint comes from (ADR-0003) rather than from any storage concern.

**Operators do not trust what they cannot reproduce.** A rule that fires differently in a
back-test than it did in production destroys confidence in every other rule. Evaluation is
therefore a pure function of rule and readings (requira ADR-0001), so the same inputs give the
same answer whenever they are run.

**Plants are not always reachable.** Connectivity at a plant is intermittent by nature, so the
bus delivers at-least-once and every handler dedupes (functions ADR-0001). Exactly-once
delivery is not available at the network's edge, so it is not designed for.

**The platform outlives its modules.** Each of the four modules will be rewritten before the
platform is retired. Contracts between them are the durable artifact and the source is not,
which is what module isolation buys (ADR-0002).

## Criteria

The design is met when:

- an operator sees a condition change within one minute of the reading that caused it;
- a rule back-tested over historical telemetry raises exactly the alerts it would have raised
  live;
- no reading in the store has ever been mutated after write;
- any one module can be replaced without touching another module's source.

How far each criterion is met is measured, not documented: it is asserted by tests and by
the SLO dashboards, or written once as a dated assessment in `records/`.
