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

3.4.1. The budget has a **floor** as well as a ceiling. A context file of only a few lines is
evidence that admissible content (§4.6) was never written, not evidence of discipline. Absence
of content is not conformance.

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

4.5. **Body sections.** The Markdown body **SHOULD** use these headings, in this order,
omitting any that do not apply:

| Heading | Requirement | Content |
|---------|-------------|---------|
| `## Purpose` | **REQUIRED** | One or two sentences: what this node is and where its boundary runs. |
| `## Working here` | **REQUIRED** | How to build, test, lint, and run; local conventions; entry-point files. |
| `## Constraints` | **RECOMMENDED** | Invariants an agent **MUST** respect, each naming the mechanism that enforces it (§4.5.2); links to governing ADRs. |
| `## Traps` | OPTIONAL | Things that look correct and are not: the counter-intuitive fact that otherwise costs an agent a wasted attempt. |
| `## Decisions in force` | OPTIONAL | One line per decision an agent would otherwise undo, each linked to its ADR (§7.2.1) or `decisions/` entry (§7.2.2). |
| `## Principles` | OPTIONAL, `project-index` only | One line per principle that decides cases no constraint enumerates, each linked to its rationale in `concept/` (§7.2.4). |

4.5.1. Headings other than these **SHOULD NOT** appear. A section with no admissible content
(§4.6) **MUST** be omitted rather than retained empty or filled with placeholder text.

4.5.2. **Enforcers.** Each entry under `## Constraints` **SHOULD** name the test, lint rule, or
CI job that enforces it. A constraint with no such mechanism **SHOULD** be marked
`(unenforced)`, so that the difference between an invariant and an aspiration stays visible to
the reader. Naming the enforcer also makes the constraint checkable: an agent can run it.

4.5.3. A node's section set is determined by what that node has to say. It **MUST NOT** be
produced by applying a fixed template to every node: template-driven sections force authors to
fill headings that have no admissible content for that node, which is how derivable filler
(§4.6.3) enters a project at scale.

4.5.4. Off-repo context is carried by `dep` pointers (§5.3), **not** by a body section. Prose
that lists or narrates dependencies duplicates machine-readable frontmatter and is
inadmissible under §4.6.3. Where a pointer needs a one-line description of what lives at the
other end, that description belongs in the pointer's `hint` (§5.2.4), not in the body.

4.5.5. **Principles.** `## Principles` **MUST NOT** appear on a `module` node. A principle
that holds for only part of a project is a constraint (§4.5.2) and belongs beside its enforcer;
a principle proper is project-wide, which is why the section is index-only in the same way
`topology` is (§4.2). Entries **MUST** be one line each and **SHOULD** link their rationale in
`concept/` (§7.2.4): a principle whose statement needs a paragraph is being argued rather than
stated, and the argument belongs in the durable document.

> A constraint decides the cases a project enumerated. A principle decides the cases it did
> not. This is why principles are admissible under §4.6.1 despite belonging to no particular
> task: they bear on all of them.

4.6. **Content admissibility.** Context files are read on every task, so every line is paid for
again on every session, indefinitely. A line is admissible only if an agent would produce worse
work without it, often enough to justify that recurring cost.

4.6.1. An admissible line **SHOULD** satisfy all four tests:

| # | Test | Question it answers |
|---|------|---------------------|
| A1 | Non-derivable | Could an agent recover this by reading the tree or running the build? |
| A2 | Load-bearing | Does work actually go wrong without it? |
| A3 | Frequently relevant | Does it apply to most tasks in this node, rather than to a recognisable minority of them? |
| A4 | Stable | Will it still be true after the next few changes? |

A1 and A2 decide whether content may enter a context file at all. **A3 is the only test that
licenses removal of content that is true and useful**: such content is not deleted but
relocated to `docs/` (§7) and reached by pointer, so it is loaded when relevant instead of
always. A4 decides whether a line will still be worth its cost later.

4.6.2. **Admissible content.** The body **SHOULD** be limited to:

| # | Class | Note |
|---|-------|------|
| C1 | Commands | Only those not discoverable from the tree, or whose discoverable form is wrong here. |
| C2 | Constraints with enforcers | Per §4.5.2. |
| C3 | Traps | The counter-intuitive fact, stated as fact. |
| C4 | Decisions in force | One line and a link, not the rationale; the rationale lives in the ADR. |
| C5 | Purpose and boundary | What this node is, and what it is not responsible for. |

4.6.3. **Inadmissible content.** The following **SHOULD NOT** appear:

| Content | Why |
|---------|-----|
| Directory listings, file inventories, module maps | Derivable from the tree (A1). |
| Restatements or narration of frontmatter pointers | Duplicates machine-readable data (§4.5.4). |
| Explanation of the navigation protocol (§8) | Spec content, not instance content. |
| Descriptions of a language, framework, or tool | Available upstream, and better there. |
| Generic engineering advice | Not specific to this node (A2). |
| Aspirations, intentions, and unenforced conventions | Fail A2; if they are rules, give them enforcers (§4.5.2). |
| Placeholder or `TODO` text | Fails every test, and signals a template (§4.5.3). |
| Anything time-connotated | See §4.7. |

4.7. **Time neutrality.** A context file **MUST** describe only the current state of the node.
Statements about what was formerly true, what has changed, or why something is no longer done
**MUST NOT** appear.

4.7.1. The following are evidence of a violation and **SHOULD** be reported as findings by
conformance tooling: `currently`, `recently`, `now`, `still`, `no longer`, `previously`,
`used to`, `formerly`, `legacy`, `new` or `old` used to contrast two states, `since`,
`as of`, `we moved`, `migrated from`, `for now`, `temporarily`, and `TODO`. (The word
`deprecated` remains admissible as a declared ADR `status` (§7.2.1), but not as narration in a
context file body.)

4.7.2. Rationale: an agent reading such a statement cannot date it. "Recently migrated to X" is
indistinguishable from "migrated to X three years ago", and both are indistinguishable from "a
migration to X is in progress". The reader must then verify the claim against the tree, which
is precisely the cost the context file existed to remove.

4.7.3. Nothing is lost by the rule. Change history is recorded by version control; decision
history is recorded by `adr/` (§7.2.1) and `decisions/` (§7.2.2), which are dated and
immutable **by design** (§7.1.3). Removing history from a context file relocates it to the artifacts
that can carry a date honestly.

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

7.1.3. **Time semantics follow mutability.** Every durable document is either *immutable and
dated* or *mutable and time-neutral*. Its class decides which:

| Class | Mutability | Time |
|-------|------------|------|
| `adr/` (§7.2.1), `decisions/` (§7.2.2) | immutable once recorded | dated **by design**; these are the project's history |
| every other durable class (§7.2.3 onward) | edited in place | time-neutral; §4.7 applies |

A mutable document that narrates its own history has no reader who can date the narration and
no mechanism that keeps it true. The history of a mutable document is its diff; the history of
a decision is an ADR.

### 7.2 Durable classes (part of the permanent record)

7.2.1. **`adr/`** — Architecture Decision Records.
- Files **MUST** be named `NNNN-slug.md` (zero-padded sequence, e.g. `0007-event-schema.md`).
- A `README.md` and files prefixed `_` (e.g. `_template.md`) **MAY** sit alongside the records
  as directory scaffolding; the naming and status rules apply only to the records themselves.
- Each ADR **MUST** carry frontmatter `status: proposed | accepted | superseded | deprecated`.
- Once `accepted`, an ADR **MUST NOT** be edited except to change its status. A reversal is a
  **new** ADR that references the old one; the old one's status becomes `superseded` with a
  pointer to the successor.

7.2.2. **`decisions/`** — a lighter-weight decision log for choices too small for an ADR.
Append-only; entries **SHOULD** be dated.

7.2.3. **`glossary.md`** - the project's controlled vocabulary (its *ubiquitous language*).

- A project **SHOULD** maintain **exactly one** glossary, in the project index's `docs/`, so
  that one concept has one canonical term across every node.
- Each entry **MUST** give the canonical term and its definition. Each entry **SHOULD** also
  give the synonyms that are *not* to be used, and the reason each is rejected:

  ```markdown
  **Consumer**:
  Any client that reaches the platform through a published contract.
  Short form: none; always "Consumer".
  _Avoid_: "user" (conflates the person with the system), "client" (names the SDK).
  ```

- The rejected-synonym list is the load-bearing half of an entry. A glossary that only defines
  terms *records* vocabulary; one that names the terms to avoid *prevents drift*, and unlike a
  definition it is mechanically checkable, because an avoid-list is a search pattern.
- A glossary **MUST NOT** carry implementation detail or decisions. Its scope is naming:
  detail belongs to `AGENTS.md` (§4.5) or a durable class (§7.2.5), decisions to `adr/`
  (§7.2.1). A glossary **SHOULD** state this boundary in its own opening lines.
- Because nearly every task names some domain concept, the glossary is the one durable
  document a project index **SHOULD** point to directly (§5.2). It is nonetheless a `docs/`
  document and **MUST NOT** be inlined into a context file: it grows with the domain, while
  §3.4 bounds what may be read on every task.
- Generated output that names a domain concept - identifiers, test names, commit messages,
  issue titles, doc prose - **SHOULD** use the glossary's term. A concept absent from the
  glossary is a signal: either language is being invented that the project does not use, or
  the glossary has a real gap and **SHOULD** be extended by the same change.

7.2.4. **`concept/`** - the project's durable design intent: the reasoning that shaped the
system and still governs how it is extended.

- It **SHOULD** cover, in whatever division suits the project: **purpose and drivers** (why the
  system exists, and the forces it was built against), **principles** (the rationale behind
  each entry in the project index's `## Principles`, §4.5.5), and **criteria** (what the system
  must achieve for its design to be considered met).
- Files **MAY** be numbered `NN-slug.md` to fix a reading order, so that an agent can load the
  document in the order its argument develops rather than alphabetically.
- **Planning state MUST NOT appear.** Phasing, roadmaps, risk registers, open-item lists, and
  any statement of how far the design has been realised describe the project's current
  *position*, not its *intent*, and `docs/` holds durable knowledge (§7.1.2). Such state
  belongs to the issue tracker or to an ephemeral class (§7.3), never here.
- **Fulfilment MUST NOT be authored.** Criteria state what must be true; how much is true is a
  *measurement*. A measurement written as prose cannot be dated by its reader (§4.7.2), so
  fulfilment **MUST** be either generated from tests and checks, or recorded as a dated and
  immutable assessment. It is never a maintained document.
- Description a reader could obtain from the tree - component inventories, module diagrams,
  configuration listings - **SHOULD NOT** appear: it is derivable (A1) and it rots (A4).

7.2.5. Other **RECOMMENDED** durable classes: `guides/` (how-to), `runbooks/` (operational),
`references/` (specs, schemas), `domain/` (domain rules and invariants that hold independently
of any implementation of them).

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

### 7.5 Routing content to a destination

7.5.1. Sections 3 and 7 define **where** knowledge may live. This section defines **which**
destination a given piece of knowledge belongs in. Each piece of durable knowledge has exactly
one home. The following rules **SHOULD** be applied in order; the first that matches wins.

| # | If the content is | It belongs in |
|---|-------------------|---------------|
| R1 | an invariant, command, trap, or boundary an agent needs on most tasks in a node | that node's `AGENTS.md` (§3, §4.5) |
| R2 | a decision whose rationale would otherwise be re-litigated or silently reversed | `docs/adr/` (§7.2.1) |
| R3 | a decision that is thin, cheaply reversible, or was closed without commitment | `docs/decisions/` (§7.2.2) |
| R4 | explanatory or reference detail needed for a recognisable minority of tasks | the appropriate durable class (§7.2.5), reached by pointer |
| R5 | specific to work in flight | an ephemeral class (§7.3), subject to the lifecycle in §7.4 |

7.5.2. Content **MUST NOT** be written to two destinations. Where a second destination needs
it, that destination **MUST** link to the first rather than restate it. Two copies of a rule
are two rules, and they will diverge.

7.5.3. A rule and the prose describing it are **substitutes, not complements**. When a
constraint gains an enforcer (§4.5.2), the prose arguing for it **SHOULD** be reduced to the
one-line statement plus the enforcer's name; the argument belongs in the ADR that decided it.

7.5.4. **On checking §7.5.** Routing is a judgment made at the moment content is written, and
it **cannot be reliably recovered afterwards**: a paragraph that should have been an ADR is not
distinguishable, after the fact, from a paragraph that belongs where it sits. Conformance
tooling therefore checks the **taxonomy** (that destinations exist and obey their own rules,
per §7.1 to §7.4) and **not** the routing. A misroute is nonetheless detectable *indirectly*,
by the symptom it leaves in the destination that wrongly received it:

| Symptom | Likely misroute |
|---------|-----------------|
| A context file over the §3.4 budget | detail that belongs in a durable class (R4) |
| Time-connotated prose in a context file (§4.7) | rationale that belongs in an ADR (R2) |
| An ADR of two lines with no rationale | a `decisions/` entry (R3) |
| An edited `decisions/` entry | a choice that deserved an ADR (R2) |
| A durable doc no context file points to | content that was never routed, only filed |
| An `active` ephemeral doc older than its feature | a §7.4 distillation that never happened |

Because §7.5 is applied when content is written, it **SHOULD** be reachable from the project
index, so that it governs at authoring time rather than at review time.

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

> **Levels certify structure, not content.** The body-section requirements (§4.5), enforcer
> naming (§4.5.2), content admissibility (§4.6), time neutrality (§4.7) and routing (§7.5) are
> **normative but not certified**. They are properties of prose rather than of the tree, and a
> level that claimed to verify them would claim more than tooling can establish (§7.5.4).
> A project **MAY** report them as separately reviewed; it **MUST NOT** present a conformance
> level as evidence of them.

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
