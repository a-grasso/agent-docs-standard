---
kind: project-index
title: <Project Name>
topology: monorepo            # monorepo | polyrepo
ref:                          # the module map — list every module
  - { at: <module-a>/AGENTS.md, hint: <one line: what it is> }
  - { at: <module-b>/AGENTS.md, hint: <one line: what it is> }
dep:                          # upstream you build on but don't own (repos, external docs)
  - { id: <dep-id>, at: <path | git URL#file | https URL>, kind: repo, hint: <what & why> }
docs: ./docs
updated: <YYYY-MM-DD>
---

# <Project Name>

## Purpose
<One or two sentences: what this system is and its boundary. Who/what it serves.>

## Working here
- **Build:** `<command>`
- **Test:** `<command>`
- **Run:** `<command>`
- **Conventions:** <language, formatting, commit style — or link to a guide in docs/>

## Constraints
- <Project-wide invariant every agent must respect. Cite the governing ADR, e.g. see ADR-0001.>
