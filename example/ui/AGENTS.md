---
kind: module
title: ui
up: ../AGENTS.md
dep:
  - { id: ng-ui,          at: git@github.com:centersight/ng-ui.git#AGENTS.md,  kind: repo,         hint: design-system components (buttons, charts, layout) — do not re-implement }
  - { id: ng-env,         at: git@github.com:centersight/ng-env.git#AGENTS.md, kind: repo,         hint: environment/config injection — read config via ng-env, never process.env }
  - { id: centersight-api, at: https://centersight-api-doc.com,                kind: external-doc, hint: REST API the dashboard reads telemetry & alerts from }
docs: ./docs
updated: 2026-07-10
---

# ui

## Purpose
The operator-facing Angular dashboard: live condition views per plant, alert inbox, and rule
management screens (which drive `requira` via the API).

## Working here
- **Build / test:** `pnpm --filter ui build|test`
- **Serve:** `pnpm --filter ui start` (proxies the API per `ng-env` config).
- **Entry points:** `src/app/dashboard.component.ts`, `src/app/app.routes.ts`.
- **Conventions:** standalone components; charts and shell come from `ng-ui` — do not fork them.

## Constraints
- **Consume, don't clone:** shared components come from `ng-ui`; config comes from `ng-env`.
- **API-only backend access:** never import `functions`/`requira` source (root ADR-0002).
