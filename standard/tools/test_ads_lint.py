#!/usr/bin/env python3
"""Tests for the ads-lint docs/adr/ checks (SPEC §7.2.1).

Stdlib only, matching the linter's own zero-dependency constraint. Run with:

    python3 standard/tools/test_ads_lint.py
    python3 -m unittest discover -s standard/tools -p 'test_*.py'
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_ads_lint():
    """`ads-lint.py` is not an importable module name, so load it by path.

    Registered in sys.modules before exec because @dataclass resolves the
    defining module through it.
    """
    path = os.path.join(_HERE, "ads-lint.py")
    spec = importlib.util.spec_from_file_location("ads_lint", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


ads_lint = _load_ads_lint()

# Minimal L1 root so the linter reaches check_docs instead of bailing on §3.1.
INDEX_AGENTS = """---
kind: project-index
topology: monorepo
---

# Fixture project
"""

ADR_RECORD = """---
kind: adr
status: accepted
---

# Use Postgres
"""


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def for_file(findings, name):
    return [f for f in findings if os.path.basename(f.path) == name]


def missing_adr_info(findings):
    return [f for f in findings
            if f.level == ads_lint.INFO and "no docs/adr/" in f.msg]


def msgs(findings):
    return " | ".join(f"{f.level} {f.rule} {f.path}: {f.msg}" for f in findings)


class AdrCase(unittest.TestCase):
    """Builds a minimal project root, drops files into docs/adr/, lints it."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = tmp.name
        _write(os.path.join(self.root, "AGENTS.md"), INDEX_AGENTS)
        _write(os.path.join(self.root, "CLAUDE.md"), "@AGENTS.md")

    def adr_file(self, name, body=ADR_RECORD):
        _write(os.path.join(self.root, "docs", "adr", name), body)

    def lint(self):
        args = argparse.Namespace(max_lines=200, stale_days=30, check_remote=False)
        findings = ads_lint.Linter(self.root, args).run()
        self.assertEqual([f for f in findings if f.level == ads_lint.ERROR], [],
                         f"fixture root should be error-free: {msgs(findings)}")
        return findings


class AdrRecordRules(AdrCase):
    """The naming and status rules that apply to records themselves."""

    def test_wellformed_record_is_clean(self):
        self.adr_file("0001-use-postgres.md")
        findings = self.lint()
        self.assertEqual([f for f in findings if f.rule == "§7.2.1"], [],
                         msgs(findings))

    def test_filename_not_nnnn_slug_warns(self):
        self.adr_file("badly-named.md")
        found = for_file(self.lint(), "badly-named.md")
        self.assertEqual(len(found), 1, msgs(found))
        self.assertEqual(found[0].level, ads_lint.WARN)
        self.assertEqual(found[0].rule, "§7.2.1")
        self.assertEqual(found[0].gate, "L3")
        self.assertIn("NNNN-slug.md", found[0].msg)

    def test_missing_status_warns(self):
        self.adr_file("0002-no-status.md", "---\nkind: adr\n---\n\n# Decision\n")
        found = for_file(self.lint(), "0002-no-status.md")
        self.assertEqual(len(found), 1, msgs(found))
        self.assertIn("status must be one of", found[0].msg)

    def test_invalid_status_warns(self):
        self.adr_file("0003-bad-status.md",
                      "---\nkind: adr\nstatus: agreed\n---\n\n# Decision\n")
        found = for_file(self.lint(), "0003-bad-status.md")
        self.assertEqual(len(found), 1, msgs(found))
        self.assertIn("status must be one of", found[0].msg)
        self.assertIn("'agreed'", found[0].msg)


class AdrScaffoldingExemption(AdrCase):
    """README.md and `_`-prefixed files are directory scaffolding, not records."""

    def test_readme_is_exempt(self):
        self.adr_file("0001-use-postgres.md")
        self.adr_file("README.md", "# Decision records\n\nHow this dir works.\n")
        self.assertEqual(for_file(self.lint(), "README.md"), [])

    def test_readme_is_exempt_case_insensitively(self):
        self.adr_file("0001-use-postgres.md")
        self.adr_file("Readme.md", "# Decision records\n")
        self.assertEqual(for_file(self.lint(), "Readme.md"), [])

    def test_underscore_prefixed_file_is_exempt(self):
        self.adr_file("0001-use-postgres.md")
        self.adr_file("_template.md",
                      "---\nkind: adr\nstatus: <proposed|accepted>\n---\n\n# Title\n")
        self.assertEqual(for_file(self.lint(), "_template.md"), [])

    def test_scaffolding_alone_does_not_satisfy_saw_adr(self):
        self.adr_file("README.md", "# Decision records\n")
        self.adr_file("_template.md", "---\nkind: adr\n---\n\n# Title\n")
        findings = self.lint()
        self.assertEqual(len(missing_adr_info(findings)), 1, msgs(findings))

    def test_a_real_record_satisfies_saw_adr(self):
        self.adr_file("0001-use-postgres.md")
        findings = self.lint()
        self.assertEqual(missing_adr_info(findings), [])


if __name__ == "__main__":
    unittest.main()
