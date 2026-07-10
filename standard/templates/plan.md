---
# EPHEMERAL — feature-scoped. File name: <feature-slug>-plan[-N].md
# Garbage-collected when the feature lands (standard §7.4): distill durable
# decisions into ADRs, then delete or move to docs/archive/.
status: draft               # draft | active | done | archived
feature: <feature-slug>
created: <YYYY-MM-DD>
---

# Plan: <feature title>

## Goal
<What we are building and the definition of done. Link the issue/ticket if any.>

## Context an agent needs
<Pointers to the exact files, modules, and docs relevant to this work.
Use ref/dep-style links so the plan is a launchpad, not a wall of text.>
- Touches module(s): <...>
- Governing ADRs / constraints: <...>
- Upstream contracts (dep): <...>

## Steps
1. <step>
2. <step>
3. <step>

## Risks & open questions
- <risk / unknown to resolve before or during the work>

## Decisions made while planning
<Anything decided here that is durable MUST be distilled into an ADR or decision log
when the feature lands. Note it as you go so nothing is lost.>
