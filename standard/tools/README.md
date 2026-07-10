# Tools

## `ads-lint.py` — conformance linter

Validates a project tree against [`../SPEC.md`](../SPEC.md) and reports the achieved
conformance level (§9). **Zero dependencies** — Python 3.8+ stdlib only (uses PyYAML for
frontmatter if it happens to be installed, otherwise a built-in parser for the ADS subset).

### Usage

```bash
python3 standard/tools/ads-lint.py --root <project>     # human-readable
python3 standard/tools/ads-lint.py --root <project> --json | jq   # machine-readable
```

| Flag | Effect |
|------|--------|
| `--root DIR` | Project root to lint (default `.`). |
| `--json` | Emit findings + conformance as JSON. |
| `--strict` | Exit non-zero on warnings too (not just errors). |
| `--check-remote` | Actually reach out to verify `dep:` git/https targets (needs network; off by default so the linter stays offline and fast). |
| `--max-lines N` | Context-file size budget (default 200; §3.4). |
| `--stale-days N` | Age past which an `active`/`draft` ephemeral doc is flagged stale (default 30; §7.4.2). |
| `--no-color` | Disable ANSI colour. |

**Exit code:** `1` if any **error** (or any **warn** under `--strict`), else `0`.

### What it checks

| Area | Rules |
|------|-------|
| Frontmatter | valid YAML block; `kind ∈ {project-index, module}`; exactly one reachable `project-index`; `project-index` has `topology` and no `up`; `module` has `up` (§3, §4, §6.3). |
| Pointer graph | `up`/`ref`/local-`dep` targets resolve; `up` is acyclic and terminates at the index; every module is enumerated in its parent's `ref`; `dep` entries well-formed (§5). |
| Aliases | a `CLAUDE.md` symlink to `AGENTS.md` exists beside each node (§3.2). |
| Docs taxonomy | ADR filenames `NNNN-slug.md` with a valid `status`; ephemeral `plans/`/`reviews/` filename grammar + `status`/`feature`; **stale** `active`/`draft` docs past `--stale-days` (§7). |
| Size budget | context files within `--max-lines` (§3.4). |

Findings carry a **severity** (`error`/`warn`/`info`), the **spec section**, the **path**, and
(where relevant) the **conformance level they gate** (`[L1]`/`[L2]`/`[L3]`).

### CI

GitHub Actions:

```yaml
# .github/workflows/ads-lint.yml
name: ads-lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: python3 standard/tools/ads-lint.py --root . --strict
```

GitLab CI:

```yaml
ads-lint:
  image: python:3.12-slim
  script:
    - python3 standard/tools/ads-lint.py --root . --strict
```

### Try it

```bash
# the bundled example is Level 3 clean:
python3 standard/tools/ads-lint.py --root example
# → conformance: L3 — fully conformant
```
