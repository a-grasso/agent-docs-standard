# Glossary

The controlled vocabulary for CenterSight. One concept, one term, everywhere: identifiers,
test names, commit messages, issue titles, doc prose.

This page is about **naming only**. Implementation detail belongs to a module's `AGENTS.md`,
decisions to `docs/adr/`. A concept missing here is a signal: either language is being
invented that the platform does not use, or the glossary has a gap and the same change should
fill it.

---

**Reading**:
One sensor sample: a value, a unit, a source sensor, and the instant it was taken.
_Avoid_: "measurement" (used by customers for a derived aggregate), "datapoint" (names the
chart pixel, not the sample), "event" (reserved for bus messages).

**Rule**:
An operator-defined condition evaluated against readings, which raises an alert when it holds.
_Avoid_: "alarm rule" (an alert is not an alarm), "trigger" (names the mechanism, not the
definition), "requirement" (the module is called `requira`; the noun is still "rule").

**Alert**:
The record that a rule held for a given plant at a given time. Raised by `requira`, delivered
by `functions`.
_Avoid_: "alarm" (industry term for the plant's own local annunciation, which CenterSight does
not own), "notification" (names the delivery, which is "dispatch").

**Dispatch**:
Delivery of an alert to a channel. A single alert may be dispatched several times.
_Avoid_: "send", "notify" (both hide that delivery is retried and separately observable).

**Channel**:
A configured destination for dispatch: email or webhook.
_Avoid_: "integration", "sink".

**Plant**:
A customer site: the unit that owns sensors and to which operators are scoped.
_Avoid_: "site", "facility", "tenant" (a tenant is a customer and may own several plants).

**Operator**:
The human who watches dashboards and acts on alerts.
_Avoid_: "user" (conflates the operator with the API consumer and with the account owner).
