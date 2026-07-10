# Decision log (platform-wide)

Lightweight decisions too small for an ADR. Newest first. Promote to an ADR if one later
turns out to be architectural (standard §7.2.2).

---

## Use pnpm workspaces for the monorepo
**Date:** 2026-06-03 · **Tags:** [tooling, build]

**Decision:** Manage the monorepo with pnpm workspaces (`pnpm -r`).

**Why:** Fast, disk-efficient, first-class workspace support; matches ADR-0001's monorepo.

**Scope:** All TypeScript modules. `infra` is excluded (HCL/Terraform).

---

## Conventional Commits + squash merge
**Date:** 2026-06-04 · **Tags:** [process, git]

**Decision:** Conventional Commits on every PR; squash-merge to `main`.

**Why:** Machine-readable history for changelogs and for agents summarizing what changed.

**Scope:** All modules.

---

## ISO-8601 UTC timestamps everywhere
**Date:** 2026-06-18 · **Tags:** [convention, data]

**Decision:** All timestamps are ISO-8601 in UTC, at millisecond precision.

**Why:** Telemetry crosses time zones; mixing formats caused two alerting bugs. Consistency
lets `requira` compare readings without conversion guesswork.

**Scope:** All modules and the API contract.
