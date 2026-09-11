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

Every file-shaped enforcer named under `## Constraints` is a relative link to a file that is
really there (§4.5.2.1): `requira/test/purity.test.ts`, `infra/test/policy.tftest.hcl`, and
two under `functions/test/`. They are stubs like the rest of the code here, which is the
point - `ads-lint` checks that the path resolves, not that the test is any good, and a
constraint that names a test which is not there is worse than one marked `(unenforced)`.
`functions/AGENTS.md` carries the one constraint with no mechanism behind it, marked as such.

There is no `plans/` or `reviews/` here. Work in flight lives in the issue tracker, which is
the other substrate (§7.3) and is addressed once, by the `tracker` key on the project index
(§7.3.5). No document here links an issue.

This example claims **Level 3** conformance (see standard §9), verified by running the vendored
linter over it: `python3 .ads/ads-lint.py --root . --strict` reports zero findings.
[`.github/workflows/ads-lint.yml`](./.github/workflows/ads-lint.yml) is a **reference workflow**
to copy into a real adoption. It does not run here: GitHub only reads workflows from
`.github/workflows/` at a repository root, and this example is a subdirectory.

> **On dates in this example.** CenterSight is fiction, authored as a single set. Its ADR and
> record dates position the documents relative to each other; they are not a record of when
> anything was really accepted. §7.2.1's rule that an accepted ADR must not be edited binds
> real projects, where acceptance is an event with witnesses. Do not read edits to this
> example's ADRs as a demonstration that editing accepted ADRs is allowed.
