# Agent Docs Standard (ADS) — Specification

**Version:** 1.0
**Status:** Draft

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHOULD**, **SHOULD NOT**,
**MAY**, and **OPTIONAL** in this document are to be interpreted as described in RFC 2119.

For the motivation behind these rules, see [`README.md`](./README.md).

---

## 1. Scope

This specification defines a filesystem-and-Markdown convention for documenting a software
project so that AI agents can locate and load relevant context efficiently. It defines:

- the **context file** and its dual naming (§3),
- **node kinds** and the **frontmatter** schema (§4),
- the **pointer graph** and its three edge types (§5),
- the **discovery and rooting** algorithm agents use (§6),
- the **`docs/` taxonomy** and the durable/ephemeral lifecycle (§7),
- the **agent navigation protocol** (§8),
- **conformance levels** (§9).

It is deliberately silent on programming language, build system, and directory names for code.

ADS is a **profile of [AGENTS.md](https://agents.md)**, not a competing convention. The
context file is a standard `AGENTS.md` exactly as existing tools consume it (a plain-Markdown
file, nearest-file precedence); everything this specification adds — the frontmatter, the
pointer graph, the `docs/` taxonomy, the lifecycle — layers on top of what AGENTS.md
deliberately leaves unspecified. Every ADS-conformant project is a valid AGENTS.md project.

---

## 2. Terminology

- **Node** — a unit of the project that owns a context file: either the *project index* (the
  root) or a *module*.
- **Context file** — the Markdown file at a node's root that an agent reads first. Canonically
  `AGENTS.md`, aliased by `CLAUDE.md` (§3).
- **Pointer** — a typed, directed edge from one node to another location, declared in
  frontmatter. One of `up`, `ref`, `dep` (§5).
- **Pointer graph** — the directed graph formed by all pointers across all nodes.
- **Durable doc** — a long-lived document (ADR, decision, guide) that is part of the permanent
  record (§7.2).
- **Ephemeral doc** — a short-lived, feature-scoped working document (plan, review) subject to
  garbage collection (§7.3).

---

## 3. The context file

3.1. Every node **MUST** have a context file named **`AGENTS.md`** at its root directory.
`AGENTS.md` is the **canonical** file.

3.2. A node **SHOULD** also expose the file under the name **`CLAUDE.md`**, for tools that look
for that name. When both exist they **MUST** resolve to identical content; the **RECOMMENDED**
mechanism is a symbolic link `CLAUDE.md → AGENTS.md` so there is a single source of truth.

> Where symlinks are impractical (e.g. Windows checkouts without Developer Mode), `CLAUDE.md`
> **MAY** instead be a one-line stub whose entire body is the import line `@AGENTS.md` —
> Claude Code's import syntax, which loads the target at session start. (A plain Markdown
> link is **not** auto-loaded and does not qualify.) Duplicating content between the two is
> **NOT** conformant — it guarantees drift.

3.3. A context file **MUST** consist of a YAML **frontmatter** block (§4) followed by a
Markdown **body** (§4.5).

3.4. Context files are **read on every task**; they **MUST** be kept small (a soft budget of
**~200 lines** is **RECOMMENDED**). Detail belongs in `docs/` (§7), reached by pointer.

---

## 4. Node kinds and frontmatter

4.1. Frontmatter **MUST** be a valid YAML mapping delimited by `---` fences at the very top of
the file.

4.2. **Required and optional keys:**

| Key | Type | Requirement | Meaning |
|-----|------|-------------|---------|
| `kind` | enum | **REQUIRED** | `project-index` or `module`. |
| `title` | string | **RECOMMENDED** | Human-readable name of the node. |
| `up` | pointer | **REQUIRED** for `module`; **MUST NOT** appear on `project-index` | Parent context file (§5.1). |
| `ref` | list of pointers | OPTIONAL | Child / related peer context files (§5.2). |
| `dep` | list of dep-pointers | OPTIONAL | Upstream dependencies (§5.3). |
| `topology` | enum | **REQUIRED** on `project-index`; **MUST NOT** appear on `module` | `monorepo` or `polyrepo` (§6.3). |
| `docs` | path | OPTIONAL | Location of this node's docs folder; defaults to `./docs`. |
| `updated` | date | OPTIONAL | ISO-8601 date the file was last meaningfully changed. |

4.3. **Exactly one** node in a reachable graph **MUST** have `kind: project-index`. It is the
**root** and **MUST NOT** declare `up`.

4.4. Unknown frontmatter keys **MAY** be present (for local extensions) and **MUST** be ignored
by conformant tooling.

4.5. **Body sections.** The Markdown body **SHOULD** use these headings, in this order, omitting
any that do not apply:

- `## Purpose` — one or two sentences: what this node is and its boundary.
- `## Working here` — how to build, test, and run; local conventions; entry-point files.
- `## Constraints` — invariants an agent MUST respect; links to governing ADRs.

4.6. **Content admissibility.** The body **SHOULD** contain only information an agent cannot
derive from the tree itself (or can only derive at disproportionate cost): invariants,
decisions, commands, and pointers to context outside the node. Prose that restates the
directory listing, re-narrates the frontmatter pointers, or explains the navigation protocol
(§8 — spec content, not instance content) **SHOULD NOT** appear. Routing information belongs
in frontmatter `hint`s, not body prose.

---

## 5. Pointers

A pointer's target is resolved **relative to the directory of the file that declares it**,
unless it is an absolute URL.

### 5.1 `up` — parent (cardinality 0..1)

5.1.1. `up` points to the context file of the node one level broader in ownership (a module's
`up` points at the project index, or at an intermediate parent module).

5.1.2. Every `module` **MUST** declare exactly one `up`. Following `up` transitively **MUST**
terminate at the `project-index` (no cycles — §5.5).

5.1.3. Semantics: **"zoom out."** An agent follows `up` to obtain broader context — project-wide
conventions, the module map, global constraints.

### 5.2 `ref` — children / related peers (cardinality 0..n)

5.2.1. `ref` is a list of pointers to context files that are **narrower** (children) or
**laterally related** (coupled siblings).

5.2.2. On the project index, `ref` **SHOULD** enumerate **every** module (it is the module
map). On a module, `ref` **SHOULD** list only siblings with which it is tightly coupled.

5.2.3. Semantics: **"zoom in / go sideways."**

5.2.4. `ref` entries **MAY** be plain path strings, or objects `{ at: <path>, hint: <string> }`
where `hint` is a one-line description of what lives there.

### 5.3 `dep` — upstream dependencies (cardinality 0..n)

5.3.1. `dep` is a list of pointers to context this node **builds on but does not own**. Targets
**MAY** lie outside the repository entirely (other repos, package registries, external doc
sites) — these are the *arbitrary upstream pointers*.

> A node with no upstreams **SHOULD** omit the `dep` key entirely. An empty list
> (`dep: []`) is valid and equivalent to omitting it; the same applies to `ref`.

5.3.2. Each `dep` entry **SHOULD** be an object:

```yaml
dep:
  - id: ng-ui                                   # short stable identifier   (REQUIRED)
    at: git@github.com:acme/ng-ui.git#AGENTS.md # path | git URL | https URL (REQUIRED)
    kind: repo                                  # repo | package | external-doc (RECOMMENDED)
    hint: shared Angular component library      # one line: what & why       (RECOMMENDED)
```

5.3.3. `at` **MAY** be: an in-repo path, a sibling-workdir path (polyrepo), a git URL
(optionally with a `#path` fragment naming the file to read in that repo), or an `https://`
URL to external documentation.

5.3.4. Semantics: **"go upstream."** `dep` targets are **read-only** from this project's
perspective. An agent follows `dep` to understand an interface or contract it consumes.

### 5.4 Direction and reciprocity

5.4.1. `up` and `ref` **SHOULD** be reciprocal where they describe the same parent/child
relationship: if index `ref`s module *M*, then *M* **MUST** `up` to the index. Tooling **MAY**
verify this.

5.4.2. `dep` is **not** reciprocal; upstream nodes are unaware of their consumers.

### 5.5 Acyclicity

5.5.1. The `up` relation **MUST** be acyclic (it is a tree toward the root). `ref` and `dep`
**MAY** form cycles; agents traversing them **MUST** track visited nodes to terminate.

---

## 6. Discovery, rooting, and topology

### 6.1 Nearest-context discovery

6.1.1. An agent beginning work in directory *D* **MUST** locate its **current node** by taking
*D*, and if it contains no `AGENTS.md`/`CLAUDE.md`, walking up the directory tree to the nearest
ancestor that does. That file governs work in *D*.

### 6.2 Rooting

6.2.1. To reach the **project index** from any node, an agent follows `up` transitively until it
reaches the node with `kind: project-index`. This is guaranteed to terminate by §5.1.2 and
§5.5.1.

6.2.2. An agent **SHOULD** read the project index early: it holds the topology, the global
conventions, and the complete `ref` module map.

### 6.3 Topology

6.3.1. The project index **MUST** declare `topology`.

6.3.2. **`monorepo`** — all modules are subdirectories under the root, which is anchored at the
`.git` directory. `up`/`ref` pointers are in-repo relative paths.

6.3.3. **`polyrepo`** — the root is a **local workdir** that aggregates independently-versioned
module repos (e.g. as sibling checkouts or submodules). Cross-module pointers that cross a repo
boundary **MUST** be expressed as `dep` with a git URL (or a documented sibling-workdir path).

6.3.4. The node structure, frontmatter, and navigation protocol are **identical** across
topologies. Only pointer *target forms* differ (§5.3.3).

---

## 7. The `docs/` folder

### 7.1 Structure

7.1.1. Any node **MAY** have a `docs/` folder (at the path given by `docs`, default `./docs`).

7.1.2. Documents are partitioned by **subfolder**, each subfolder being one document *class*.
Classes are either **durable** (§7.2) or **ephemeral** (§7.3). The standard defines the classes
below; projects **MAY** add classes, declaring each as durable or ephemeral.

### 7.2 Durable classes (part of the permanent record)

7.2.1. **`adr/`** — Architecture Decision Records.
- Files **MUST** be named `NNNN-slug.md` (zero-padded sequence, e.g. `0007-event-schema.md`).
- Each ADR **MUST** carry frontmatter `status: proposed | accepted | superseded | deprecated`.
- Once `accepted`, an ADR **MUST NOT** be edited except to change its status. A reversal is a
  **new** ADR that references the old one; the old one's status becomes `superseded` with a
  pointer to the successor.

7.2.2. **`decisions/`** — a lighter-weight decision log for choices too small for an ADR.
Append-only; entries **SHOULD** be dated.

7.2.3. Other **RECOMMENDED** durable classes: `guides/` (how-to), `runbooks/` (operational),
`references/` (specs, schemas), `domain/` (domain/glossary knowledge).

### 7.3 Ephemeral classes (feature-scoped, garbage-collected)

7.3.1. **`plans/`** — implementation plans for in-flight work.

7.3.2. **`reviews/`** — reviews of features or changes.

7.3.3. Ephemeral files **MUST** be named `<feature-slug>-<class>[-<n>].md`
(e.g. `alert-throttling-plan.md`, `alert-throttling-review-2.md`) and **MUST** carry
frontmatter:

```yaml
status: draft | active | done | archived   # REQUIRED
feature: alert-throttling                   # REQUIRED — the feature slug
created: 2026-07-10                         # RECOMMENDED
```

### 7.4 Lifecycle of ephemeral docs

7.4.1. When a feature completes, any durable knowledge in its ephemeral docs (decisions,
learned constraints, interface changes) **MUST** be **distilled** into the appropriate durable
class (an ADR, a `decisions/` entry, or an update to a module's `AGENTS.md`).

7.4.2. After distillation, the ephemeral docs **SHOULD** be **garbage-collected**: either
deleted, or moved to `docs/archive/` with `status: archived`. They **MUST NOT** be left as
`active`/`draft` indefinitely — stale plans mislead agents.

7.4.3. Rationale: the durable record is what agents load to understand the system; keeping it
small and free of transient noise is what makes it loadable and trustworthy.

---

## 8. Agent navigation protocol

A conformant agent **SHOULD** follow this protocol. It is the operational payoff of the
standard.

8.1. **Orient.** On starting a task in directory *D*, discover the current node (§6.1). Read its
context file frontmatter and body.

8.2. **Widen only as needed.** If the task needs project-wide conventions, build/test commands,
or the module map, follow `up` to the project index (§6.2) and read it. Do **not** load
unrelated modules.

8.3. **Traverse by intent.** Resolve the task to a pointer:

| Intent | Traversal |
|---|---|
| project-wide rule / command / module map | `up` → project index (+ its `docs/`) |
| work inside another module *X* | index `ref` → *X*'s `AGENTS.md` → `X/docs/adr/` |
| understand a consumed interface/contract | `dep` → target repo's `AGENTS.md` or external doc |
| *why* is it built this way | nearest `docs/adr/` then `docs/decisions/` |
| current state of feature *F* | `docs/plans/F-*.md` (ignore `status: archived`) |

8.4. **Respect constraints.** Before changing a node, read its `## Constraints` and the ADRs it
cites. An `accepted` ADR is binding (§7.2.1).

8.5. **Write to the right place.** When producing durable output, use this decision order:

1. Architectural / hard-to-reverse decision → **new ADR** in the nearest owning node's `adr/`.
2. Smaller but lasting choice → **`decisions/`** entry.
3. In-flight planning or a change review → **`plans/`** / **`reviews/`** (ephemeral).
4. A stable rule about *how to work in this node* → edit the node's **`AGENTS.md`**.

8.6. **Close the loop.** When a feature lands, perform §7.4 distillation and garbage collection.

8.7. **Budget.** Prefer the smallest set of hops that answers the task. Every pointer not
followed is context budget preserved.

---

## 9. Conformance levels

A project **MAY** claim one of three cumulative levels.

**Level 1 — Minimal (navigable root).**
- The root has an `AGENTS.md` with `kind: project-index` and `topology`.
- Every module (if any) has an `AGENTS.md` with `kind: module` and a valid `up`.
- The project index is reachable from every node via `up` (§6.2).

**Level 2 — Navigable graph.**
- All of L1, plus: the index's `ref` enumerates every module (§5.2.2), and every cross-boundary
  dependency is declared as a `dep` (§5.3).
- `up`/`ref` reciprocity holds (§5.4.1).

**Level 3 — Documented & maintained.**
- All of L2, plus: the `docs/` taxonomy (§7) is in use; major decisions are captured as ADRs;
  the ephemeral lifecycle (§7.4) is followed (no stale `active` plans); context files respect
  the size budget (§3.4).

---

## Appendix A — Minimal conformant project

```
my-project/
  AGENTS.md          # kind: project-index, topology: monorepo
  CLAUDE.md          # symlink → AGENTS.md
```

## Appendix B — Frontmatter quick reference

```yaml
# project index
---
kind: project-index
title: My Project
topology: monorepo
ref:
  - { at: services/api/AGENTS.md, hint: HTTP API }
  - { at: web/AGENTS.md,          hint: web client }
dep:
  - { id: shared-ui, at: git@github.com:acme/shared-ui.git#AGENTS.md, kind: repo, hint: design system }
docs: ./docs
updated: 2026-07-10
---

# module
---
kind: module
title: API service
up: ../../AGENTS.md
ref:
  - { at: ../worker/AGENTS.md, hint: shares the job queue }
dep:
  - { id: payments-api, at: https://docs.payments.example/api, kind: external-doc }
docs: ./docs
updated: 2026-07-10
---
```

See [`templates/`](./templates/) for full, copy-ready files.
