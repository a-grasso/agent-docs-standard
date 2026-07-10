---
# EPHEMERAL — feature-scoped. File name: <feature-slug>-review[-N].md
# Garbage-collected with its feature (standard §7.4).
status: draft               # draft | active | done | archived
feature: <feature-slug>
created: <YYYY-MM-DD>
---

# Review: <feature title>

## What changed
<Summary of the change under review; link the plan it implements.>

## Findings
| Severity | Location | Finding | Status |
|----------|----------|---------|--------|
| <high/med/low> | `<file:line>` | <what's wrong / risky> | <open/fixed/won't-fix> |

## Verdict
<Ship / needs work / blocked — and why.>

## Durable takeaways
<Lessons or constraints worth keeping. These MUST be distilled into an ADR, a decision-log
entry, or the module's AGENTS.md before this review is garbage-collected.>
