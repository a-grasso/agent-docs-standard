---
kind: project-index
title: CenterSight
topology: monorepo
ref:
  - { at: functions/AGENTS.md, hint: backend serverless functions - telemetry ingestion and alert dispatch }
  - { at: ui/AGENTS.md,        hint: Angular operator dashboard }
  - { at: requira/AGENTS.md,   hint: rule engine - evaluates alert rules against telemetry }
  - { at: infra/AGENTS.md,     hint: Terraform infrastructure-as-code }
dep:
  - { id: ng-env,         at: git@github.com:centersight/ng-env.git#AGENTS.md, kind: repo,         hint: shared Angular environment/config library }
  - { id: ng-ui,          at: git@github.com:centersight/ng-ui.git#AGENTS.md,  kind: repo,         hint: shared Angular component/design-system library }
  - { id: centersight-api, at: https://centersight-api-doc.com,                kind: external-doc, hint: the public CenterSight telemetry & alerts REST API }
tracker:
  at: https://github.com/centersight/platform/issues
  kind: github
  hint: work state - status, sequencing and what is next; none of it is in this repo
docs: ./docs
updated: 2026-09-10
---

# CenterSight

## Purpose
An industrial IoT condition-monitoring platform. It ingests sensor telemetry from customer
plants, evaluates configurable alert rules against that telemetry, and presents live condition
dashboards and alerts to operators.

## Working here
- **Build:** `pnpm -r build`
- **Test:** `pnpm -r test`
- **Run (local stack):** `pnpm dev` (starts functions + ui against a local emulator)
- **Conventions:** TypeScript everywhere except `infra` (HCL). Formatting via Prettier + the
  repo `.editorconfig`. Conventional Commits. One module = one deployable unit.

## Constraints
- **Module isolation:** a module MUST NOT import another module's source directly; cross-module
  communication goes through published contracts (events or the API). ADR-0002; enforced by
  the ESLint `no-restricted-imports` rule.
- **Telemetry is append-only:** ingestion MUST NOT mutate historical readings. ADR-0003;
  enforced by the store's write-once grant (`infra/main.tf`) and `functions` contract tests.
- **One vocabulary:** name domain concepts as `docs/glossary.md` names them, in identifiers,
  tests and commit messages alike. `(unenforced)` - the avoid-list is a search pattern, so this
  is mechanisable, but nothing greps it yet.
- **Work state is not in this repository:** status, sequencing and what is next live in the
  issue tracker, never in `docs/` or a context file. ADR-0004; enforced by `ads-lint`'s §7.3.2
  check. Completed events are written up in `docs/records/`.

## Principles
- **Evidence over convenience.** Where a design choice trades away the ability to reconstruct
  what a machine reported, it loses. See `docs/concept/01-purpose-and-drivers.md`.
- **Contracts are the durable artifact; module source is not.** Every module will be rewritten
  before the platform is; design for that. See `docs/concept/01-purpose-and-drivers.md`.
- **Reproducibility beats latency.** A slower answer that a back-test reproduces is worth more
  than a fast one that operators cannot check. See `docs/concept/01-purpose-and-drivers.md`.
