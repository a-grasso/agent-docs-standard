---
kind: project-index
title: CenterSight
topology: monorepo
ref:
  - { at: functions/AGENTS.md, hint: backend serverless functions — telemetry ingestion & alert dispatch }
  - { at: ui/AGENTS.md,        hint: Angular operator dashboard }
  - { at: requira/AGENTS.md,   hint: rule engine — evaluates alert rules against telemetry }
  - { at: infra/AGENTS.md,     hint: Terraform infrastructure-as-code }
dep:
  - { id: ng-env,         at: git@github.com:centersight/ng-env.git#AGENTS.md, kind: repo,         hint: shared Angular environment/config library }
  - { id: ng-ui,          at: git@github.com:centersight/ng-ui.git#AGENTS.md,  kind: repo,         hint: shared Angular component/design-system library }
  - { id: centersight-api, at: https://centersight-api-doc.com,                kind: external-doc, hint: the public CenterSight telemetry & alerts REST API }
docs: ./docs
updated: 2026-07-10
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

## Map
- `ref:` above is the authoritative module list — four modules, each independently deployable.
- `docs/adr/` — platform-wide architecture decisions.
- `docs/decisions/` — the lighter decision log.
- Feature-scoped work (plans, reviews) lives **inside the owning module's** `docs/`.

## Navigation (for agents)
- Follow **`ref:`** to enter a module; read its `AGENTS.md` before editing it.
- Follow **`dep:`** to understand the shared Angular libraries (`ng-env`, `ng-ui`) or the
  external telemetry API. These are read-only upstreams — we consume them, we don't change them
  here.
- This is the root (`kind: project-index`); every module's `up:` leads back to this file.
- Read `docs/adr/` before any cross-module or architectural change.

## Constraints
- **Module isolation:** a module MUST NOT import another module's source directly; cross-module
  communication goes through published contracts (events or the API). See ADR-0002.
- **Telemetry is append-only:** ingestion MUST NOT mutate historical readings. See ADR-0003.
