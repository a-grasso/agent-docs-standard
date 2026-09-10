---
id: ADR-0004
title: Work state leaves the repository
status: accepted
date: 2026-09-02
supersedes: ADR-0001
superseded-by: -
normative-in: ../../AGENTS.md
revisit-when: the tracker stops being the system of record for work, e.g. if issues move into
  the repository itself
---

# ADR-0004: Work state leaves the repository

## Context
ADR-0001 adopted the Agent Docs Standard and put feature work in per-module `docs/plans/` and
`docs/reviews/`. Three months of that produced the failure it was meant to prevent. The
throttling plan under `requira/docs/plans/` sat at `status: active` for two months after the
feature shipped. The review beside it recorded conclusions that had since been reversed. Both
read as current to any agent that loaded them, and nothing in the repository could tell that
they were not.

The reason is structural rather than a lapse in discipline. A tracker item is invalidated by
work happening, and the tracker observes work happening. A document has no observer, so a
document that states status has no invalidation event its reader can see. The garbage-
collection rule in the standard existed to compensate for that, and compensating rules are
executed by people who have already moved on to the next feature.

## Decision
Status, sequencing, ownership and what-is-next live in the **issue tracker**. The repository
describes; the tracker tracks. `docs/plans/` and `docs/reviews/` are removed, and no class
replaces them.

What a completed piece of work established is still written down: a constraint learned goes
to the owning node's `## Constraints`, a decision to an ADR or the decision log, an event to
`docs/records/`. What does not get written down is the work's state.

The tracker is named once, by the project index's `tracker` key, and nowhere else. No document
links an individual issue: a decision record outlives the work that produced it, so a pointer
to that work would resolve long after it stopped being the reason.

**What this does not reverse.** ADR-0001 decided three things: to adopt the standard, to run as
a monorepo, and to keep feature work in `plans/`/`reviews/`. Only the third is reversed here.
The first two remain in force, and this ADR carries them forward: the standard stays adopted and
the topology stays `monorepo`. Supersession is whole-document, so ADR-0001's status had to
change even though most of it still stands - which is the cost of recording three decisions in
one record.

## Consequences
- **Positive:** no document in the repository can go stale by describing work that has moved
  on, because no document describes work. The garbage-collection duty disappears with the
  documents that needed it.
- **Negative / cost:** the tracker becomes load-bearing for agents, and an agent without
  tracker access cannot answer "what is in flight" from the repository alone. That is the
  honest answer rather than a stale one.
- **Follow-ups:** the throttling plan and review were distilled into `requira`'s
  `## Decisions in force` and deleted.

## Alternatives considered
- **Keep the classes and enforce the lifecycle harder** (a stricter staleness gate in CI):
  rejected. It makes the compensating rule louder without giving the document an observer,
  and a gate that fires on documents nobody has re-read is a gate people learn to bypass.
- **Move the classes outside `docs/`** into a `work/` folder: rejected. It relocates the
  problem instead of removing it; the documents would still state status with nothing to
  invalidate them.
