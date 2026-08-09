---
kind: module
title: <Module Name>
up: <../AGENTS.md>            # REQUIRED — path to the parent (usually the project index)
ref:                          # OPTIONAL — only tightly-coupled siblings
  - { at: ../<sibling>/AGENTS.md, hint: <why they are coupled> }
dep:                          # OPTIONAL — upstream this module specifically consumes
  - { id: <dep-id>, at: <path | git URL#file | https URL>, kind: external-doc, hint: <what & why> }
docs: ./docs
updated: <YYYY-MM-DD>
---

# <Module Name>

## Purpose
<One or two sentences: what this module owns and where its boundary is.>

## Working here
- **Build / test / run:** <module-specific commands, if they differ from the root>
- **Entry points:** <the files an agent should read first, e.g. src/index.ts>
- **Conventions:** <anything specific to this module>

## Constraints
- <Invariant an agent must respect when changing this module. Cite the ADR that governs it.>
