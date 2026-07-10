# CenterSight (example)

This is a **fictional** project included to demonstrate the [Agent Docs Standard](../standard/).
It is documentation-complete but only lightly stubbed in code — the point is the *shape* of the
docs, not a runnable app.

**To explore it the way an agent would, start at [`AGENTS.md`](./AGENTS.md)** and follow the
pointers: `ref:` to drill into modules, `up:` to come back, `dep:` to see upstream libraries.

## Layout

```
example/
  AGENTS.md            project index (kind: project-index, topology: monorepo)
  CLAUDE.md            → symlink to AGENTS.md
  docs/                platform-wide durable docs
    adr/               architecture decision records
    decisions/         lightweight decision log
  functions/           module: backend ingestion & alert dispatch
  ui/                  module: Angular dashboard  (dep: ng-ui, ng-env)
  requira/             module: rule engine  (has an in-flight feature: plans/ + reviews/)
  infra/               module: Terraform IaC
  .ads/                vendored conformance linter (keeps CI self-contained)
  .github/workflows/   ads-lint runs on every push / PR
```

Each module mirrors the same pattern: an `AGENTS.md` (+ `CLAUDE.md` alias), a `docs/` folder,
and an `up:` pointer back to the root. `requira/docs/` shows the **ephemeral** lifecycle — a
live feature plan and its review that will be garbage-collected once the feature lands.

This example claims **Level 3** conformance (see standard §9) and is **CI-verified**:
[`.github/workflows/ads-lint.yml`](./.github/workflows/ads-lint.yml) runs the vendored linter
(`.ads/ads-lint.py`) with `--strict` on every push and PR.
