# ADS cheatsheet (for the adopt-ads skill)

Condensed from the full standard. Bundled assets (`../assets/`) are **vendored copies** from the
doc-standard repo's `standard/templates/` and `standard/tools/`; the canonical source is the
repo. This cheatsheet is enough to scaffold correctly; consult the full `SPEC.md` for edge cases.

## Context file
- Every node has `AGENTS.md` (canonical). `CLAUDE.md` is a **symlink** to it (single source).
- Keep it small (~200 lines), and not empty either (~20 lines is a floor, §3.4.1); push
  detail into `docs/`.
- Structure: YAML frontmatter, then body sections, in order, omitting any with nothing
  admissible under them (§4.5):

  | Heading | Level | Note |
  |---|---|---|
  | `## Purpose` | REQUIRED | what this node is, and where its boundary runs |
  | `## Working here` | REQUIRED | build, test, lint, run; entry points |
  | `## Constraints` | RECOMMENDED | each names its enforcer, or is marked `(unenforced)` |
  | `## Traps` | OPTIONAL | what looks correct and is not |
  | `## Decisions in force` | OPTIONAL | one line + ADR link, never the rationale |
  | `## Principles` | OPTIONAL | **index only**; one line each, rationale in `concept/` |

- Delete headings you cannot fill; never pad them. Identical section sets across nodes mean
  the template was filled rather than the node described (§4.5.3).
- **Admissibility (A1-A4):** non-derivable, load-bearing, frequently relevant, stable. A3 is
  the one that licenses *removal*: true-but-occasional content moves to `docs/` behind a
  pointer, it is not deleted.
- Inadmissible: directory narration, restating the pointers, framework descriptions, generic
  advice, placeholders/TODO, **status of work in flight** (that is the tracker's, §7.3), and
  anything time-connotated (§4.7: `currently`, `recently`, `no longer`, `for now`, ...).

## Frontmatter

```yaml
# project-index (the root): exactly one per project
kind: project-index          # REQUIRED
title: <name>                # RECOMMENDED
topology: monorepo|polyrepo  # REQUIRED on the index; forbidden on modules
ref:                         # module map: list every module
  - { at: <module>/AGENTS.md, hint: <what it is> }
dep:                         # upstream you consume but don't own
  - { id: <id>, at: <path|git URL#file|https URL>, kind: repo|package|external-doc, hint: <what and why> }
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
- **`up`** (0..1) - parent context; module → index. Must resolve, be acyclic, and terminate at
  the index. "Zoom out."
- **`ref`** (0..n) - children (index → modules) or coupled siblings. Index should enumerate every
  module. "Zoom in / sideways."
- **`dep`** (0..n) - upstream, may cross repo boundaries (git URLs, external doc URLs, sibling
  paths). Read-only. "Go upstream." Capture only upstreams a human must reason about - not every
  transitive package.

Paths resolve relative to the declaring file's directory. `at` may append `#file` to a git URL to
name the file to read in that repo.

## Topology
- **monorepo** - one `.git`; modules are subdirs; `up`/`ref` are in-repo relative paths.
- **polyrepo** - root is a local workdir aggregating separate repos; cross-boundary pointers are
  `dep` git URLs. Same node structure either way.

## docs/ taxonomy
Every class in `docs/` is durable. Immutable-and-dated, or mutable-and-time-neutral (§7.1.3):

- `adr/` - `NNNN-slug.md`, frontmatter `status: proposed|accepted|superseded|deprecated`.
  Immutable once accepted; reverse via a new ADR. Also carries `normative-in:` (the doc
  allowed to state it as current fact) and `revisit-when:` (a *checkable* reopening
  condition; omitting it asserts permanence). It does **not** name an issue (§7.3.5.2).
- `decisions/` - lightweight, dated, append-only, never edited.
- `records/` - `YYYY-MM-DD-slug.md`. Dated, immutable records of *events*: upgrades,
  incidents, migrations, benchmark runs. An event has no alternatives; a decision does.
  Time-connotated prose is fine here, because the document is dated.
- `glossary.md` - one per project, in the **index's** `docs/`, found by convention not by
  pointer. Each entry: canonical term, definition, and the synonyms to avoid *with reasons*.
  The avoid-list is the load-bearing half; it is a grep pattern.
- `concept/` - durable design intent: purpose and drivers, principles' rationale, criteria.
  No planning state, no fulfilment prose.
- also: `guides/`, `runbooks/`, `references/`, `domain/`.

Scaffolding (`README.md`, `_`-prefixed files) is exempt from class rules anywhere in `docs/`
(§7.1.4), so a class template belongs in the class it serves.

## Substrates: docs describe, issues track
There is no `plans/` or `reviews/` class. **Status, sequencing, ownership and what-is-next
belong to the issue tracker**, never to `docs/` or a context file (§7.3). A document that
states status has no invalidation event its reader can see, so it rots silently. What still
has to happen when work lands is **distillation**: the constraint learned, the interface
fixed, the decision taken get written into the right class. The work's *state* stays put.

An ADR's own `status:` is the one exemption (§7.3.2): it reports whether the project is bound
by a decision, and a superseding ADR invalidates it visibly.

The tracker is addressed **once**, by the `tracker` key on the project index (§7.3.5). No
individual document links a tracker item (§7.3.5.2): a durable doc outlives the work that made
it, so *"which issue closed this?"* is deliberately not answerable from the repository.

## Routing: where a given piece of knowledge goes (§7.4)
Applied when content is written; first match wins.

| # | If the content is | It belongs in |
|---|---|---|
| R1 | status, sequencing, ownership, or what is next | the tracker |
| R2 | an invariant, command, trap or boundary needed on most tasks in a node | that node's `AGENTS.md` |
| R3 | a decision whose rationale would otherwise be re-litigated or silently reversed | `docs/adr/` |
| R4 | a decision that is thin, cheaply reversible, or closed without commitment | `docs/decisions/` |
| R5 | a completed event whose detail is worth keeping | `docs/records/` |
| R6 | explanatory or reference detail needed for a recognisable minority of tasks | the right durable class, reached by pointer |

Content **MUST NOT** be written twice; the second destination links instead (§7.4.2). Routing
itself is not mechanically checkable (§7.4.4) - tooling checks the taxonomy, not the routing.

## Conformance
- **L1** minimal: valid `AGENTS.md` per node; single reachable `project-index`; modules have valid
  `up`.
- **L2** navigable: index `ref` enumerates every module; cross-boundary deps declared; pointers
  resolve.
- **L3** documented: docs taxonomy in use; ADRs for major decisions; classes obey their own
  naming and mutability rules; size budget respected.

Levels certify **structure, not prose**: §4.5, §4.6, §4.7, §7.3 and §7.4 are normative but
not certified, so never present a level as evidence of them (§9).

Verify with `../assets/ads-lint.py --root <project>`.
