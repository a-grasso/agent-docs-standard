---
kind: module
title: infra
up: ../AGENTS.md
docs: ./docs
updated: 2026-09-10
---

# infra

## Purpose
Infrastructure-as-code (Terraform) for CenterSight: the event bus, the append-only telemetry
store and its cold-tiering, the dedupe index, and per-module deploy targets.

## Working here
- **Plan / apply:** `terraform -chdir=infra plan|apply`. This module is HCL, not TypeScript,
  and is excluded from pnpm; see the root decision log.
- **Entry points:** `main.tf` (topology), `modules/` (reusable stacks), `envs/` (dev/prod vars).

## Constraints
- **No manual console changes:** all infrastructure is defined here; drift is reconciled, not
  blessed. Enforced by the nightly `terraform plan` drift job, which fails on a non-empty plan.
  Procedure in `docs/runbooks/deploy.md`.
- **Write-once telemetry grant:** the store's IAM policy grants no update or delete on
  readings. Root ADR-0003; enforced by `test/policy.tftest.hcl`.
