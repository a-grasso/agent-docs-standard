---
kind: project-index
title: <Project Name>
topology: monorepo            # monorepo | polyrepo
ref:                          # the module map: list every module
  - { at: <module-a>/AGENTS.md, hint: <one line: what it is> }
  - { at: <module-b>/AGENTS.md, hint: <one line: what it is> }
dep:                          # upstream you build on but do not own (repos, external docs)
  - { id: <dep-id>, at: <path | git URL#file | https URL>, kind: repo, hint: <what and why> }
tracker:
  at: <URL or org/repo where work state lives - the second substrate (SPEC 7.3.5)>
  kind: <github | gitlab | jira | linear | other>
  hint: <one line. Delete this key only if the project genuinely has no tracker.>
docs: ./docs
updated: <YYYY-MM-DD>
---

<!--
This is an authoring prompt, not a form (SPEC §4.5.3). Delete every heading you have
nothing admissible to say under: an empty or padded section is worse than an absent one
(§4.5.1). If your project index and your modules end up with the same section set, that is
the signal that headings were filled rather than nodes described.

Admissible: what an agent cannot derive from the tree, needs on most tasks here, and that
will still be true in a few changes' time (§4.6). Not admissible: directory listings,
restatements of the pointers above, framework descriptions, generic advice, status of work
in flight (that belongs to the tracker, §7.3), and anything time-connotated (§4.7).
-->

# <Project Name>

## Purpose
<One or two sentences: what this system is, and where its boundary runs. What it is not
responsible for is often the more useful half.>

## Working here
- **Build:** `<command>`
- **Test:** `<command>`
- **Run:** `<command>`
- **Conventions:** <only those an agent would otherwise get wrong; link a guide in docs/ for
  the rest>

## Constraints
- <Invariant every agent must respect.> <Cite the governing ADR.> Enforced by <test, lint
  rule, or CI job>.
- <Invariant with no mechanism behind it.> (unenforced)

## Traps
<Delete unless you have one. A trap is a thing that looks correct and is not: the
counter-intuitive fact that otherwise costs an agent a wasted attempt.>

## Decisions in force
- <One line per decision an agent would otherwise undo, and a link to its ADR. The line, not
  the rationale: the rationale is what the ADR is for.>

## Principles
<Index only (§4.5.5); a principle that holds for part of a project is a constraint. One line
each, each linking its rationale in docs/concept/. A constraint decides the cases you
enumerated; a principle decides the ones you did not.>
