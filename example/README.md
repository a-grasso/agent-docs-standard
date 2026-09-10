# CenterSight (example)

This is a **fictional** project included to demonstrate the [Agent Docs Standard](../standard/).
It is documentation-complete but only lightly stubbed in code - the point is the *shape* of the
docs, not a runnable app.

**To explore it the way an agent would, start at [`AGENTS.md`](./AGENTS.md)** and follow the
pointers: `ref:` to drill into modules, `up:` to come back, `dep:` to see upstream libraries.

## Layout

```
example/
  AGENTS.md            project index (kind: project-index, topology: monorepo)
  CLAUDE.md            symlink to AGENTS.md
  docs/                platform-wide durable docs
    glossary.md        the controlled vocabulary (§7.2.4)
    adr/               architecture decision records
    decisions/         lightweight decision log
    concept/           durable design intent (§7.2.5)
    records/           dated, immutable records of events (§7.2.3)
  functions/           module: backend ingestion and alert dispatch
  ui/                  module: Angular dashboard  (dep: ng-ui, ng-env)
  requira/             module: rule engine
  infra/               module: Terraform IaC
  .ads/                vendored conformance linter (keeps CI self-contained)
  .github/workflows/   ads-lint runs on every push / PR
```

Each module has an `AGENTS.md` (+ `CLAUDE.md` alias), a `docs/` folder, and an `up:` pointer
back to the root. Their **body sections differ**, and deliberately so (§4.5.3): `functions`
and `ui` carry `## Traps`, `requira` carries `## Decisions in force`, `infra` carries neither,
and `## Principles` appears only on the index, where §4.5.5 confines it. A node writes the
sections it has something to say in.

There is no `plans/` or `reviews/` here. Work in flight lives in the issue tracker, which is
the other substrate (§7.3): the ADRs name the issues they close via `decides:`.

This example claims **Level 3** conformance (see standard §9) and is **CI-verified**:
[`.github/workflows/ads-lint.yml`](./.github/workflows/ads-lint.yml) runs the vendored linter
(`.ads/ads-lint.py`) with `--strict` on every push and PR.
