---
id: ADR-0001
title: Adopt the Agent Docs Standard in a monorepo
status: accepted
date: 2026-06-02
supersedes: -
superseded-by: -
---

# ADR-0001: Adopt the Agent Docs Standard in a monorepo

## Context
CenterSight is built primarily with AI agents. Our earlier layout had a single 900-line
`CLAUDE.md` at the root. Agents either loaded the whole thing (burning context and still
missing module specifics) or worked blind inside a module. We need documentation that lets an
agent find just the context a task requires.

We also had to choose a repo topology. The four modules ship together, share tooling, and
change in lockstep often enough that coordinating four repos was pure overhead.

## Decision
We will adopt the **Agent Docs Standard** and structure the repo as a **monorepo**
(`topology: monorepo`, root anchored at `.git`). Every module gets its own `AGENTS.md`
(+ `CLAUDE.md` symlink) with `up:`/`ref:`/`dep:` pointers; durable docs live in `docs/adr/` and
`docs/decisions/`; feature work lives in per-module `docs/plans/` and `docs/reviews/`.

## Consequences
- **Positive:** agents orient from the nearest `AGENTS.md` and pull deeper context by pointer;
  the root context file drops from 900 lines to ~40.
- **Negative / cost:** contributors must keep `ref:`/`up:` reciprocity correct and garbage-
  collect ephemeral docs; we add a CI check for both.
- **Follow-ups:** ADR-0002 (module isolation) and ADR-0003 (append-only telemetry) codify the
  cross-module constraints the standard's `## Constraints` sections point at.

## Alternatives considered
- **Keep the monolithic `CLAUDE.md`** — rejected: does not scale with the codebase or the
  context window.
- **Polyrepo** — rejected for now: the modules co-release; `dep:` still lets us split later
  without changing the doc model (standard §6.3.4).
