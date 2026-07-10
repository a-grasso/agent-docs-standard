---
kind: module
title: infra
up: ../AGENTS.md
docs: ./docs
updated: 2026-07-10
---

# infra

## Purpose
Infrastructure-as-code (Terraform) for CenterSight: the event bus, the append-only telemetry
store and its cold-tiering, the dedupe index, and per-module deploy targets.

## Working here
- **Plan / apply:** `terraform -chdir=infra plan|apply` (this module is HCL, not TypeScript —
  excluded from pnpm; see root decision log).
- **Entry points:** `main.tf` (topology), `modules/` (reusable stacks), `envs/` (dev/prod vars).

## Map
- `main.tf`, `modules/`, `envs/`.
- `docs/runbooks/` — operational procedures (deploy, incident response, tiering).

## Navigation (for agents)
- Follow **`up:`** for platform conventions and the constraints this infra must satisfy:
  append-only storage (root ADR-0003) drives cold-tiering; idempotent ingestion
  (functions ADR-0001) requires the dedupe index provisioned here.
- No `ref:`/`dep:` — infra provisions the substrate the other modules run on; it depends on
  their *requirements* (via ADRs), not their source.

## Constraints
- **No manual console changes:** all infrastructure is defined here; drift is reconciled, not
  blessed. See `docs/runbooks/deploy.md`.
