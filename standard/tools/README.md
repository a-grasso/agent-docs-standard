# Tools

## `ads-lint.py` - conformance linter

Validates a project tree against [`../SPEC.md`](../SPEC.md) and reports the achieved
conformance level (§9). **Zero dependencies**: Python 3.8+ stdlib only (uses PyYAML for
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
| `--min-lines N` | Context-file size floor (default 20; §3.4.1). Set `0` to disable. |
| `--stale-days N` | Removed in 2.0. Accepted and ignored, so a 1.0 CI job does not break. |
| `--no-color` | Disable ANSI colour. |

**Exit code:** `1` if any **error** (or any **warn** under `--strict`), else `0`.

### What it checks

| Area | Rules |
|------|-------|
| Frontmatter | valid YAML block; `kind ∈ {project-index, module}`; exactly one reachable `project-index`; `project-index` has `topology` and no `up`; `module` has `up` (§3, §4, §6.3). |
| Pointer graph | `up`/`ref`/local-`dep` targets resolve **case-sensitively**, on every host filesystem; `up` is acyclic and terminates at the index; every module is enumerated in its parent's `ref`; `dep` entries well-formed (§5). Only *declared* `dep`s: nothing here reads source, so an undeclared dependency is invisible (§5.3.5). |
| Aliases | a `CLAUDE.md` symlink to `AGENTS.md` exists beside each node (§3.2). |
| Docs taxonomy | ADR filenames `NNNN-slug.md` with a valid `status`; record filenames `YYYY-MM-DD-slug.md`; one glossary, at the index; `README.md` and `_`-prefixed files exempt everywhere in `docs/` (§7.1.4). |
| Substrates | a durable doc that declares `status:` is stating work state, which belongs to the tracker (§7.3.2). `adr/` is exempt: its status is the decision's own lifecycle. Reported **ungated**: §9 places the substrate rule outside the conformance levels, so this finding never changes the reported level. Use `--strict` to gate CI on it. |
| Time neutrality | context-file bodies (§4.7.1) and mutable `docs/` classes (§7.1.3) are checked for narration of change. The term list deliberately excludes `now`/`since`/`still`/`new`/`old`: a check that fires on those trains its readers to ignore it. |
| Enforcers | a path named under `## Constraints` must resolve, so a constraint cannot name a test that is not there (§4.5.2.1). Only tokens with a directory component and an extension count as paths, so `no-restricted-imports` and `terraform plan` are left alone. Reported **ungated**: §9 keeps §4.5 out of the levels. |
| Vocabulary | every rejected synonym in the project's `glossary.md` avoid-list is grepped over context files and mutable `docs/` classes (§7.2.4). A synonym that is another entry's canonical term is skipped, because a grep cannot tell which entry a sentence is about. Reported **ungated**. |
| Size budget | context files within `--max-lines` (§3.4), and not under `--min-lines` (§3.4.1). |

Findings carry a **severity** (`error`/`warn`/`info`), the **spec section**, the **path**, and
(where relevant) the **conformance level they gate** (`[L1]`/`[L2]`/`[L3]`). Findings for the
clauses §9 leaves uncertified (§4.5.2.1 enforcers, §4.7 time neutrality, §7.2.4 vocabulary,
§7.3.2 substrates, §3.4.1's floor) carry **no gate** by design: they are reported, and they fail `--strict`, but they never move the
level. A level certifies structure, never prose.

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

### Tests

Stdlib `unittest`, no dependencies. Covers the `docs/` class rules (§7.1.4, §7.2.1, §7.2.3,
§7.2.4), the substrate check (§7.3.2), enforcer resolution (§4.5.2.1), the glossary avoid-list
(§7.2.4), time neutrality (§4.7.1), the size floor (§3.4.1) and case-sensitive pointer
resolution (§5):

```bash
python3 standard/tools/test_ads_lint.py
python3 -m unittest discover -s standard/tools -p 'test_*.py'
```

### Try it

```bash
# the bundled example is Level 3 clean:
python3 standard/tools/ads-lint.py --root example
# conformance: L3, fully conformant
```
