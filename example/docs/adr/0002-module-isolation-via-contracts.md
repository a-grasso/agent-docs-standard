---
id: ADR-0002
title: Module isolation via published contracts
status: accepted
date: 2026-06-09
supersedes: -
superseded-by: -
decides: centersight/platform#88
normative-in: ../../AGENTS.md
revisit-when: a module needs a synchronous call to another module that the API cannot serve
  within its latency budget
---

# ADR-0002: Module isolation via published contracts

## Context
In a monorepo it is tempting to import another module's internals directly. That couples
deploy units, lets agents reach across boundaries without reading the target module's rules,
and turns four deployables into one tangled unit.

## Decision
Modules MUST communicate only through **published contracts**:
- asynchronous **domain events** on the shared bus (schemas in `functions/docs/references/`),
  and
- the **REST API** documented at the `centersight-api` upstream (`dep:`).

Direct source imports across module boundaries are forbidden and enforced by an ESLint
`no-restricted-imports` rule and a CI boundary check.

## Consequences
- **Positive:** each module stays independently deployable and reviewable; an agent changing
  one module needs only that module's context plus the contract, not the whole repo.
- **Negative / cost:** cross-module changes require a contract version step; more upfront schema
  work.
- **Follow-ups:** every module's `AGENTS.md` `## Constraints` cites this ADR.

## Alternatives considered
- **Shared internal library** - rejected: becomes a god-module and a coupling magnet.
- **Allow imports, rely on discipline** - rejected: not enforceable, and invisible to agents.
