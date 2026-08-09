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

## Constraints
- **No manual console changes:** all infrastructure is defined here; drift is reconciled, not
  blessed. See `docs/runbooks/deploy.md`.
