# The Agent Docs Standard — Vision & Design

> The normative rules live in [`SPEC.md`](./SPEC.md). This document explains the *why* — the
> design principles the spec encodes. Read this to understand the standard; read the spec to
> implement it.

## The problem, precisely

An AI agent operating in a repository is not like a new engineer who can absorb the codebase
over weeks. On every task it starts cold, with:

1. a **finite context window** (a hard budget — every token spent on irrelevant context is a
   token not spent on the task), and
2. a **filesystem** it can read on demand.

So the entire game is: *get the right context into the window at the right moment, and nothing
else.* A documentation layout is good for agents exactly to the degree that it makes this
easy. ADS is a set of conventions optimized for that single objective.

## Five design principles

### 1. Locality of reference

Context lives **next to the thing it describes**. The rules for the `ui` module are in
`ui/AGENTS.md` and `ui/docs/`, not in a central wiki. An agent editing a file in `ui/` finds
its governing context by looking *up from where it already is*, not by knowing where a central
doc store lives. This mirrors how code locality works and makes the "nearest context" cheap to
find.

### 2. Progressive disclosure over exhaustive dumps

A context file is an **entry point and a router**, not an encyclopedia. It states what the unit
is, how to work in it, and — crucially — *where to go for more*. An agent reads a small file,
then follows pointers to pull deeper context only when the task demands it. The alternative (a
giant `CLAUDE.md` that tries to say everything) fails twice: it's too big to keep in context,
and too big to keep current.

### 3. Typed navigation

Links between context files carry **meaning**, so an agent follows them *purposefully*:

- **`up:`** answers *"what's the broader picture / the project-wide rule?"* — traverse it to
  reach global conventions and the module map.
- **`ref:`** answers *"where's the related area?"* — the index's `ref:` is the module map;
  a module's `ref:` names siblings it's coupled to.
- **`dep:`** answers *"what do I build on that I don't own?"* — upstream repos and external
  docs, which may live entirely outside this repository.

Because the edge is typed, the agent knows *why* it's following a link and *what shape* of
information waits on the other side. This is the difference between a graph an agent can plan
over and a pile of undifferentiated hyperlinks.

### 4. Durable and ephemeral are different materials

- **Durable** docs (ADRs, decision logs, guides) are the **permanent record** — the answer to
  *"why is it like this?"* They are small, curated, and long-lived.
- **Ephemeral** docs (plans, reviews) are **working artifacts** tied to a single feature — the
  answer to *"what are we doing right now?"* They are numerous, disposable, and short-lived.

Mixing them is the classic docs-rot trap: the permanent record drowns in transient noise. ADS
keeps them in separate folders with an explicit lifecycle — ephemeral docs are **distilled**
into durable ones when a feature lands, then **garbage-collected**. This keeps the durable
record small enough to trust and cheap enough to load.

### 5. Topology- and tool-agnostic

- **Repo topology:** the same node structure works for a **monorepo** (root anchored at
  `.git`, modules are subdirectories) and a **polyrepo** (root is a local workdir, modules are
  separate repos, `dep:` pointers become git URLs). The pointer graph spans repo boundaries by
  design — that's what `dep:` is for.
- **Agent tool:** `AGENTS.md` is the canonical file — ADS is a *profile* of the
  [AGENTS.md](https://agents.md) convention (governed by the Linux Foundation's Agentic AI
  Foundation), adding only what it deliberately leaves unspecified. `CLAUDE.md` is an alias
  (a symlink) so Claude Code and other tools each find a file under the name they look for,
  with **one source of truth** behind both.

## Why a *graph*, and not a tree

A tree (index → modules) captures ownership, but real dependencies aren't a tree:

- `ui` depends on the shared `ng-ui` component library (another repo).
- `functions` calls an external API documented at `centersight-api-doc.com`.
- `requira` is coupled to `functions` as a sibling.

`up:`/`ref:` give you the ownership tree; `dep:` adds the **cross-cutting edges** that turn it
into the graph that actually describes the system. An agent asked *"is it safe to change this
API call?"* follows `dep:` to the upstream doc — a question a pure tree can't answer.

## What an agent actually does with this

The payoff is a small, repeatable **navigation protocol** (specified in `SPEC.md §8`). A few
examples:

| The agent needs… | It does… |
|---|---|
| project-wide build/test commands & conventions | follow `up:` to the project index; read it |
| to safely change module *X* | from the index, follow `ref:` → *X*'s `AGENTS.md`; read `X/docs/adr/` for constraints |
| to understand an upstream dependency | read `dep:`; follow the pointer to the repo's `AGENTS.md` or the external doc URL |
| to know *why* something is built this way | read the nearest `docs/adr/` and `docs/decisions/` |
| to start feature *F* | create `docs/plans/F-plan.md` from the template; on completion, write a review, distill decisions into ADRs, delete the plan |

The agent never has to *guess* where information lives, and never has to load more than the
current hop of the graph.

## Non-goals

- **Not a replacement for good code.** Self-documenting code and types come first; ADS
  documents the *why* and the *where*, not the *what* that code already states.
- **Not a heavy process.** The minimum conformant project is one `AGENTS.md` at the root.
  Everything else is added when a unit is big enough to earn it.
- **Not tied to one vendor.** `CLAUDE.md` is an alias, not the canonical name; the standard
  works with any agent that reads a Markdown context file.

## Tooling

The standard ships with two tools so conformance is enforceable, not aspirational:

- **[`tools/ads-lint.py`](./tools/ads-lint.py)** — a zero-dependency linter that checks a project
  against `SPEC.md` and reports its conformance level (§9). See [`tools/README.md`](./tools/README.md).
- **[`skills/adopt-ads/`](./skills/adopt-ads/)** — a Claude Code skill that adopts/retrofits the
  standard in a repository, interrogating for dependency pointers and verifying with the linter.

## Next

Continue to [`SPEC.md`](./SPEC.md) for the normative rules, or explore
[`../example/`](../example/) to see it in practice.
