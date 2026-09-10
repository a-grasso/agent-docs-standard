# `.ads/` - Agent Docs Standard tooling (vendored)

`ads-lint.py` in this directory is the Agent Docs Standard conformance linter, placed in the
repo so CI is self-contained - no network fetch, and reproducible at the version you pinned.
Canonical source: the doc-standard repo's `standard/tools/ads-lint.py`.

> In a **real adoption** this is a vendored copy of that file. In *this* repo the example
> lives beside the canonical linter, so it is a symlink instead - one source of truth, no
> drift between copies.

Run it locally:

```bash
python3 .ads/ads-lint.py --root . --strict
```

CI runs the same command on every push/PR via
[`../.github/workflows/ads-lint.yml`](../.github/workflows/ads-lint.yml).

**Updating (real adoptions):** re-copy the canonical `ads-lint.py` over this file when the
standard's tooling changes. (The linter is skipped by its own scan - `.ads/` is a
dot-directory - so it never shows up as project content.)
