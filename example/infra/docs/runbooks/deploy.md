# Runbook: deploy CenterSight

Operational procedure (durable). For *why* the infra is shaped this way, see the ADRs the
module `AGENTS.md` cites.

## Prerequisites
- Terraform >= 1.7, cloud credentials for the target env (`envs/<env>.tfvars`).
- Green CI on `main` (build + test + module-boundary check from root ADR-0002).

## Deploy
1. `terraform -chdir=infra plan -var-file=envs/prod.tfvars -out=plan.out`
2. Review the plan. **Refuse** any diff that would drop or alter a telemetry table — storage is
   append-only (root ADR-0003); destructive changes need a migration ADR first.
3. `terraform -chdir=infra apply plan.out`
4. Deploy code: `pnpm -r --filter "./functions" --filter "./requira" --filter "./ui" deploy`.

## Rollback
- Infra: `git revert` the change and re-apply. Never edit resources in the console (module
  constraint).
- Code: redeploy the previous release tag; ingestion is idempotent (functions ADR-0001), so
  replays are safe.

## Verify
- `/healthz` green on all modules; a synthetic reading flows ingest → `requira` → dispatch;
  dashboard renders it.
