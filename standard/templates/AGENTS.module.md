---
kind: module
title: <Module Name>
up: <../AGENTS.md>            # REQUIRED: path to the parent (usually the project index)
ref:                          # OPTIONAL: only tightly-coupled siblings
  - { at: ../<sibling>/AGENTS.md, hint: <why they are coupled> }
dep:                          # OPTIONAL: upstream this module specifically consumes
  - { id: <dep-id>, at: <path | git URL#file | https URL>, kind: external-doc, hint: <what and why> }
docs: ./docs
---

<!--
An authoring prompt, not a form (SPEC §4.5.3). Delete every heading with nothing admissible
under it (§4.5.1). `## Principles` is absent by design: it is index-only (§4.5.5), and a
principle that holds for one module is a constraint.
-->

# <Module Name>

## Purpose
<One or two sentences: what this module owns and where its boundary is.>

## Working here
- **Build / test:** <module-specific commands, if they differ from the root>
- **Entry points:** <the files an agent should read first, e.g. src/index.ts>
- **Conventions:** <anything specific to this module>

## Constraints
- <Invariant an agent must respect when changing this module.> <Cite the ADR that governs
  it.> Enforced by <lint rule or CI job, named in prose>, or by a file in this repo written
  as a relative link: [`<test/path.test.ts>`](<test/path.test.ts>) (§4.5.2.1). Mark an
  invariant with no mechanism `(unenforced)` rather than naming one that is not there.

## Traps
<Delete unless you have one. The counter-intuitive fact, stated as fact.>

## Decisions in force
- <One line and a link to the ADR, for a decision an agent would otherwise undo.>
