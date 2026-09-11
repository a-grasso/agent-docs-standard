---
kind: module
title: ui
up: ../AGENTS.md
dep:
  - { id: ng-ui,          at: git@github.com:centersight/ng-ui.git#AGENTS.md,  kind: repo,         hint: design-system components (buttons, charts, layout) - do not re-implement }
  - { id: ng-env,         at: git@github.com:centersight/ng-env.git#AGENTS.md, kind: repo,         hint: environment/config injection - read config via ng-env, never process.env }
  - { id: centersight-api, at: https://centersight-api-doc.com,                kind: external-doc, hint: REST API the dashboard reads telemetry & alerts from }
docs: ./docs
---

# ui

## Purpose
The operator-facing Angular dashboard: live condition views per plant, alert inbox, and rule
management screens (which drive `requira` via the API).

## Working here
- **Build / test:** `pnpm --filter ui build|test`
- **Serve:** `pnpm --filter ui start` (proxies the API per `ng-env` config).
- **Entry points:** `src/app/dashboard.component.ts`, `src/app/app.routes.ts`.
- **Conventions:** standalone components; charts and shell come from `ng-ui`, never forked.

## Constraints
- **Consume, do not clone:** shared components come from `ng-ui`; config comes from `ng-env`.
  Enforced by the `no-forked-components` lint rule and a `process.env` ban in ESLint.
- **API-only backend access:** never import `functions`/`requira` source. Root ADR-0002;
  enforced by the ESLint `no-restricted-imports` rule.

## Traps
- `ng-ui` chart components take readings in the API's wire shape, not the view model. Mapping
  them first produces an empty chart with no error.
- The dev proxy reads `ng-env` config at build time, so changing an environment file needs a
  restart of `pnpm --filter ui start`, not just a reload.
