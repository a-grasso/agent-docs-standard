#!/usr/bin/env python3
"""Tests for ads-lint: docs/adr/ checks (§7.2.1) and case-sensitive resolution (§5).

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


MODULE_AGENTS = """---
kind: module
title: Widgets
up: ../{up}
---

# Widgets
"""


class CaseSensitiveResolution(unittest.TestCase):
    """Pointer targets must resolve with the case they are written in (§5).

    On macOS/APFS and Windows a pointer written `../agents.md` resolves against
    a file named `AGENTS.md`, so the project lints green locally and 404s on
    Linux CI. These tests are no-ops on a case-sensitive filesystem, where the
    wrong-case target simply does not exist - the finding is the same either
    way, which is the point.
    """

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = tmp.name

    def lint(self):
        args = argparse.Namespace(max_lines=200, stale_days=30, check_remote=False)
        return ads_lint.Linter(self.root, args).run()

    def index(self, ref):
        _write(os.path.join(self.root, "AGENTS.md"),
               "---\nkind: project-index\ntopology: monorepo\nref:\n"
               f"  - {ref}\n---\n\n# Fixture project\n")
        _write(os.path.join(self.root, "CLAUDE.md"), "@AGENTS.md")

    def module(self, up):
        _write(os.path.join(self.root, "widgets", "AGENTS.md"),
               MODULE_AGENTS.format(up=up))
        _write(os.path.join(self.root, "widgets", "CLAUDE.md"), "@AGENTS.md")

    def errors(self, rule):
        return [f for f in self.lint()
                if f.level == ads_lint.ERROR and f.rule == rule]

    # -- the helper itself ------------------------------------------------

    def test_helper_accepts_the_exact_spelling(self):
        _write(os.path.join(self.root, "docs", "AGENTS.md"), "x")
        self.assertTrue(ads_lint.exists_case_sensitive(
            os.path.join(self.root, "docs", "AGENTS.md")))

    def test_helper_rejects_a_miscased_filename(self):
        _write(os.path.join(self.root, "docs", "AGENTS.md"), "x")
        self.assertFalse(ads_lint.exists_case_sensitive(
            os.path.join(self.root, "docs", "agents.md")))

    def test_helper_rejects_a_miscased_directory(self):
        _write(os.path.join(self.root, "docs", "AGENTS.md"), "x")
        self.assertFalse(ads_lint.exists_case_sensitive(
            os.path.join(self.root, "Docs", "AGENTS.md")))

    def test_helper_rejects_a_missing_path(self):
        self.assertFalse(ads_lint.exists_case_sensitive(
            os.path.join(self.root, "nope.md")))

    def test_helper_traverses_dot_dot(self):
        _write(os.path.join(self.root, "widgets", "AGENTS.md"), "x")
        _write(os.path.join(self.root, "AGENTS.md"), "x")
        self.assertTrue(ads_lint.exists_case_sensitive(
            os.path.join(self.root, "widgets", "..", "AGENTS.md")))

    # -- the three pointer kinds ------------------------------------------

    def test_ref_with_wrong_case_is_an_error(self):
        self.index("widgets/agents.md")
        self.module("AGENTS.md")
        found = self.errors("§5.2")
        self.assertEqual(len(found), 1, msgs(self.lint()))
        self.assertIn("ref target does not exist", found[0].msg)

    def test_ref_with_right_case_is_clean(self):
        self.index("widgets/AGENTS.md")
        self.module("AGENTS.md")
        self.assertEqual(self.errors("§5.2"), [], msgs(self.lint()))

    def test_up_with_wrong_case_is_an_error(self):
        self.index("widgets/AGENTS.md")
        self.module("agents.md")
        found = self.errors("§5.1")
        self.assertEqual(len(found), 1, msgs(self.lint()))
        self.assertIn("up target does not resolve", found[0].msg)

    def test_local_dep_with_wrong_case_is_an_error(self):
        self.index("widgets/AGENTS.md")
        _write(os.path.join(self.root, "docs", "references", "schema.md"), "# S\n")
        _write(os.path.join(self.root, "widgets", "AGENTS.md"),
               "---\nkind: module\ntitle: Widgets\nup: ../AGENTS.md\ndep:\n"
               "  - { id: schema, at: ../docs/references/Schema.md,"
               " kind: repo, hint: event schema }\n---\n\n# Widgets\n")
        _write(os.path.join(self.root, "widgets", "CLAUDE.md"), "@AGENTS.md")
        found = self.errors("§5.3.3")
        self.assertEqual(len(found), 1, msgs(self.lint()))
        self.assertIn("local dep target does not exist", found[0].msg)

    def test_local_dep_with_right_case_is_clean(self):
        self.index("widgets/AGENTS.md")
        _write(os.path.join(self.root, "docs", "references", "schema.md"), "# S\n")
        _write(os.path.join(self.root, "widgets", "AGENTS.md"),
               "---\nkind: module\ntitle: Widgets\nup: ../AGENTS.md\ndep:\n"
               "  - { id: schema, at: ../docs/references/schema.md,"
               " kind: repo, hint: event schema }\n---\n\n# Widgets\n")
        _write(os.path.join(self.root, "widgets", "CLAUDE.md"), "@AGENTS.md")
        self.assertEqual(self.errors("§5.3.3"), [], msgs(self.lint()))

    # -- the diagnostic ----------------------------------------------------

    def test_case_mismatch_is_named_in_the_message(self):
        """Only meaningful where the filesystem is case-insensitive."""
        self.index("widgets/agents.md")
        self.module("AGENTS.md")
        target = os.path.join(self.root, "widgets", "agents.md")
        if not os.path.exists(target):
            self.skipTest("case-sensitive filesystem: nothing to disambiguate")
        self.assertIn("case mismatch", self.errors("§5.2")[0].msg)


if __name__ == "__main__":
    unittest.main()
