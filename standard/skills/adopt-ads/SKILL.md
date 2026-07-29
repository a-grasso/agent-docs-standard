---
name: adopt-ads
description: >-
  Set up (or retrofit) the Agent Docs Standard (ADS) in a repository so AI agents can find
  context where and when they need it. Detects greenfield vs brownfield, infers repo topology
  and module boundaries, interrogates the user for dependency pointers (and where to find
  them), checks required tooling (git / grep / gh / glab / python3), scaffolds AGENTS.md +
  CLAUDE.md aliases + a docs/ skeleton from templates, and verifies the result with ads-lint.
  Use when the user wants to adopt, install, bootstrap, retrofit, or "set up the doc standard"
  in a project. User-invoked; do not auto-trigger.
---

# Adopt the Agent Docs Standard

Your job is to bring a target repository into conformance with the Agent Docs Standard (ADS)
and leave it **lint-clean**. Work in phases. Prefer **inference over interrogation** — detect
what you can, then confirm concisely; only ask the user what you genuinely cannot determine.

**Guardrails**
- **Additive only.** You create/modify docs (`AGENTS.md`, `CLAUDE.md`, `docs/`). Do **not**
  edit source code or move files around.
- **Never fabricate.** If you don't know a value (a dep URL, a build command, a constraint),
  write `<TODO: …>` and list it in the handoff. A wrong pointer is worse than a missing one.
- **Idempotent.** Safe to re-run. If a node already has `AGENTS.md`, treat this as
  upgrade/repair — lint first, fill gaps, don't clobber.
- **Confirm before bulk writes.** Show the plan (which files you'll create) before creating
  many files.

## Assets (bundled with this skill)

Resolve these relative to this SKILL.md's directory; if absent (e.g. you're running inside the
doc-standard source repo), fall back to the repo copies:

| Asset | Bundled path | Repo fallback |
|-------|--------------|---------------|
| Templates | `assets/templates/` | `standard/templates/` |
| Linter | `assets/ads-lint.py` | `standard/tools/ads-lint.py` |
| Spec (reference) | `references/spec-cheatsheet.md` | `standard/SPEC.md` |

Read `references/spec-cheatsheet.md` before scaffolding if you need the exact frontmatter rules.

---

## Phase 0 — Preflight: target + tooling

1. **Target root.** Default to the current working directory. If the user named a path, use it.
   If ambiguous, ask.
2. **Tooling check.** Run the detection below and report a short table of what's present. None of
   these are hard blockers except a shell; explain what each *enables* so the user understands
   any degraded features.

```bash
for t in git rg grep python3 gh glab jq; do
  if command -v "$t" >/dev/null 2>&1; then echo "$t: $(command -v "$t")"; else echo "$t: MISSING"; fi
done
```

| Tool | Used for | If missing |
|------|----------|-----------|
| `python3` | running `ads-lint` (verification) | skip lint; verify by hand against the cheatsheet |
| `git` | topology detection; discovering `dep:` URLs from remotes/submodules | ask the user for topology and dep URLs |
| `rg` (or `grep`) | scanning code for dependency references / API URLs | ask the user to name upstream deps |
| `gh` / `glab` | resolving org repos to canonical clone URLs; `--check-remote` verification | paste dep URLs manually; skip remote checks |

State plainly: ADS itself has **no runtime dependency** — it's Markdown + symlinks. The tools
above only assist *setup* and *verification*.

## Phase 1 — Greenfield or brownfield?

Gather signals, then classify:

```bash
git -C <root> rev-parse --is-inside-work-tree 2>/dev/null && echo "git: yes"
ls -A <root>                              # existing layout
find <root> -maxdepth 2 -name AGENTS.md -o -name CLAUDE.md 2>/dev/null   # already adopted?
# manifests hint at real code + build commands:
find <root> -maxdepth 3 \( -name package.json -o -name pyproject.toml -o -name go.mod \
  -o -name Cargo.toml -o -name pom.xml -o -name build.gradle -o -name '*.tf' \) 2>/dev/null
```

- **Greenfield** — empty or near-empty, no real source. → scaffold the skeleton; modules are
  aspirational (create what the user plans, or just the root).
- **Brownfield** — existing code. → detect structure and *document what exists*.
- **Already has AGENTS.md/CLAUDE.md** — upgrade/repair. Run the linter first (Phase 6) to see
  what's missing, then fill only the gaps.

If the signals are mixed, confirm with one `AskUserQuestion`.

## Phase 2 — Topology

Infer `monorepo` vs `polyrepo`:

- **monorepo** signals: single `.git` at root **and** a workspace file
  (`pnpm-workspace.yaml`, `package.json` `workspaces`, `turbo.json`, `lerna.json`, `go.work`,
  Cargo `[workspace]`, Nx, Bazel `WORKSPACE`).
- **polyrepo** signals: the target is a workdir aggregating multiple independent checkouts or
  git submodules (`.gitmodules`), each with its own `.git`.

Propose the inferred value and confirm. Topology only changes the *form* of cross-boundary
pointers (in-repo relative paths vs git URLs) — the structure is identical (SPEC §6.3).

## Phase 3 — Module boundaries

**Brownfield** — propose candidate modules, don't guess silently:

```bash
# workspace members, if declared:
cat <root>/pnpm-workspace.yaml 2>/dev/null; jq -r '.workspaces?' <root>/package.json 2>/dev/null
# else: top-level dirs that own a manifest are strong module candidates:
find <root> -maxdepth 2 \( -name package.json -o -name pyproject.toml -o -name go.mod \
  -o -name Cargo.toml -o -name '*.tf' \) -not -path '*/node_modules/*' 2>/dev/null
```

Also look at conventional roots: `services/`, `packages/`, `apps/`, `modules/`, `cmd/`, `libs/`.
Present the candidate list via `AskUserQuestion` (multiSelect) so the user can confirm, drop, or
add. Each confirmed module becomes a `module` node; the root becomes the `project-index`.

**Greenfield** — ask what modules they intend (or agree to start with just the root and add
modules later). Don't over-scaffold empty dirs.

## Phase 4 — Interrogate dependencies (the important part)

For the project and **each module**, determine its upstream `dep:` pointers and *where each
points*. This is what lets an agent later answer "what do I build on, and where's its doc?".

**Assist yourself first**, then ask only about what's left:

```bash
git -C <root> remote -v                          # canonical origin / sibling repos
git -C <root> config --file .gitmodules --list 2>/dev/null   # submodule URLs (polyrepo/deps)
# significant upstreams only — internal shared libs, sibling repos, external APIs:
jq -r '.dependencies // {} | keys[]' <module>/package.json 2>/dev/null   # filter to the ones that matter
# external API/doc URLs referenced in code:
rg -oN --no-heading 'https?://[a-zA-Z0-9./_-]*(api|docs?)[a-zA-Z0-9./_-]*' <module> 2>/dev/null | sort -u
```

Then for each candidate dependency, resolve the four fields. Use `AskUserQuestion` when a value
isn't derivable — **ask specifically "where does `<dep>` live / what should its pointer target?"**

| Field | How to fill |
|-------|-------------|
| `id` | short stable name (from the package/repo name) |
| `at` | git URL `…#AGENTS.md`, an `https://` doc URL, or a local/sibling path. Prefer a remote's URL from `git remote`/submodules; if `gh`/`glab` is present, resolve `org/repo` to a canonical clone URL. |
| `kind` | `repo` \| `package` \| `external-doc` |
| `hint` | one line: what it is and why this module depends on it |

Do **not** dump every transitive package into `dep:`. Capture the upstreams a human would need
to reason about: shared internal libraries, sibling services, and external API contracts. When
unsure whether a dep matters, ask in a batched question rather than guessing.

## Phase 5 — Scaffold

Read the templates, then write real files (fill placeholders; leave `<TODO>` for unknowns):

1. **Root `AGENTS.md`** from `AGENTS.project-index.md`: set `kind: project-index`, `title`,
   `topology`, `ref:` (every confirmed module), `dep:` (project-level upstreams), `docs: ./docs`.
2. **Each module `AGENTS.md`** from `AGENTS.module.md`: set `kind: module`, `up:` (relative path
   to the root's `AGENTS.md`), `ref:` (only tightly-coupled siblings), module-specific `dep:`.
   Delete the `ref:`/`dep:` line entirely when a node has none - never leave it empty.
3. **Fill `## Working here` from reality** (brownfield): pull build/test/run commands from
   manifests, `Makefile`/`Justfile`, or CI config. Populate `## Map` from the actual directories.
   Leave `## Constraints` minimal — capture only invariants the user states or that are obvious
   from config; don't invent rules.
4. **CLAUDE.md aliases** — in each node directory:
   ```bash
   ln -sf AGENTS.md <node-dir>/CLAUDE.md
   ```
   (On Windows checkouts without symlink support, instead write a one-line stub whose entire
   body is `@AGENTS.md` — Claude Code's import line, which auto-loads the target. A plain
   Markdown link is **not** loaded; never duplicate content.)
5. **docs/ skeleton** at the root (and per module where it earns it):
   `docs/adr/`, `docs/decisions/`. Create `docs/plans/` and `docs/reviews/` lazily, when a
   feature actually starts.
6. **Seed ADR-0001** at `docs/adr/0001-adopt-agent-docs-standard.md` from `adr.md`, recording the
   decision to adopt ADS and the chosen topology. This is both useful and a worked example of
   the durable record.
7. **Fold any pre-existing `CLAUDE.md`** content into the new `AGENTS.md` (then replace it with
   the symlink) — do not silently discard what was there. Show the user the merge.

## Phase 6 — Verify

Run the linter and drive it to clean:

```bash
python3 <assets>/ads-lint.py --root <root>            # or --json for detail
```

Fix every **error** and every **L2/L3-gated warn** you reasonably can (broken pointers, missing
aliases, un-enumerated modules, malformed docs). Remaining warns that need human input (a
`<TODO>` dep URL, a size-budget trim) go into the handoff. Re-run until the reported
conformance level is as high as the inputs allow.

## Phase 7 — Handoff

Report concisely:
- **What was created** (file count + the tree of new `AGENTS.md`/`CLAUDE.md`/`docs/`).
- **Conformance level** achieved (from the linter) and what blocks the next level.
- **Open `<TODO>`s** the user must fill (usually dep URLs and a few commands).
- **Suggested next steps:** wire `ads-lint` into CI (see the tools README), and capture existing
  tribal knowledge as ADRs over time.

Offer, but don't assume: converting more existing decisions into ADRs, or splitting an
oversized legacy `CLAUDE.md` into per-module context files.
