# ADS cheatsheet (for the adopt-ads skill)

Condensed from the full standard. Bundled assets (`../assets/`) are **vendored copies** from the
doc-standard repo's `standard/templates/` and `standard/tools/`; the canonical source is the
repo. This cheatsheet is enough to scaffold correctly; consult the full `SPEC.md` for edge cases.

## Context file
- Every node has `AGENTS.md` (canonical). `CLAUDE.md` is a **symlink** to it (single source).
- Keep it small (~200 lines); push detail into `docs/`.
- Structure: YAML frontmatter, then body sections `## Purpose`, `## Working here`,
  `## Constraints` (omit any that don't apply).
- Body content rule: only what an agent cannot derive from the tree (invariants, decisions,
  commands, external pointers). No directory narration, no restating the pointers - routing
  info belongs in frontmatter `hint`s.

## Frontmatter

```yaml
# project-index (the root) — exactly one per project
kind: project-index          # REQUIRED
title: <name>                # RECOMMENDED
topology: monorepo|polyrepo  # REQUIRED on the index; forbidden on modules
ref:                         # module map — list every module
  - { at: <module>/AGENTS.md, hint: <what it is> }
dep:                         # upstream you consume but don't own
  - { id: <id>, at: <path|git URL#file|https URL>, kind: repo|package|external-doc, hint: <what & why> }
docs: ./docs                 # OPTIONAL (default ./docs)
updated: YYYY-MM-DD          # OPTIONAL

# module
kind: module                 # REQUIRED
title: <name>
up: <rel path to parent AGENTS.md>   # REQUIRED; forbidden on the index
ref: [ ... coupled siblings ... ]    # OPTIONAL
dep: [ ... module-specific upstreams ... ]   # OPTIONAL
docs: ./docs
```

## Pointer semantics
- **`up`** (0..1) — parent context; module → index. Must resolve, be acyclic, and terminate at
  the index. "Zoom out."
- **`ref`** (0..n) — children (index → modules) or coupled siblings. Index should enumerate every
  module. "Zoom in / sideways."
- **`dep`** (0..n) — upstream, may cross repo boundaries (git URLs, external doc URLs, sibling
  paths). Read-only. "Go upstream." Capture only upstreams a human must reason about — not every
  transitive package.

Paths resolve relative to the declaring file's directory. `at` may append `#file` to a git URL to
name the file to read in that repo.

## Topology
- **monorepo** — one `.git`; modules are subdirs; `up`/`ref` are in-repo relative paths.
- **polyrepo** — root is a local workdir aggregating separate repos; cross-boundary pointers are
  `dep` git URLs. Same node structure either way.

## docs/ taxonomy
Durable (permanent record):
- `adr/` — `NNNN-slug.md`, frontmatter `status: proposed|accepted|superseded|deprecated`.
  A `README.md` and `_`-prefixed files (e.g. `_template.md`) may sit alongside the records.
  Immutable once accepted; reverse via a new ADR.
- `decisions/` — lightweight, dated, append-only.
- also: `guides/`, `runbooks/`, `references/`, `domain/`.

Ephemeral (feature-scoped, garbage-collected):
- `plans/`, `reviews/` — filename `<feature-slug>-plan|review[-N].md`; frontmatter
  `status: draft|active|done|archived` + `feature:`.
- On feature completion: **distill** durable takeaways into ADRs/decisions, then **delete** or
  archive the ephemeral docs. No stale `active` docs.

## Conformance
- **L1** minimal: valid `AGENTS.md` per node; single reachable `project-index`; modules have valid
  `up`.
- **L2** navigable: index `ref` enumerates every module; cross-boundary deps declared; pointers
  resolve.
- **L3** documented: docs taxonomy in use; ADRs for major decisions; ephemeral lifecycle followed;
  size budget respected.

Verify with `../assets/ads-lint.py --root <project>`.
