#!/usr/bin/env python3
"""Tests for ads-lint: the docs/ class rules (§7.1.4, §7.2.x), the substrate
check (§7.3.2), time neutrality (§4.7.1), the size floor (§3.4.1), and
case-sensitive pointer resolution (§5).

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
        args = argparse.Namespace(max_lines=200, min_lines=0, check_remote=False)
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
        args = argparse.Namespace(max_lines=200, min_lines=0, check_remote=False)
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


class DocsCase(AdrCase):
    """Same fixture root, with an ADR present so `saw_adr` is satisfied."""

    def setUp(self):
        super().setUp()
        self.adr_file("0001-use-postgres.md")

    def doc(self, relpath, body):
        _write(os.path.join(self.root, "docs", *relpath.split("/")), body)


class ScaffoldingIsTreeWide(DocsCase):
    """§7.1.4: class rules bind records, not the files that help write them."""

    def test_underscore_file_in_any_class_is_exempt(self):
        self.doc("records/_template.md", "# Record template\n")
        self.assertEqual(for_file(self.lint(), "_template.md"), [], msgs(self.lint()))

    def test_class_readme_is_exempt(self):
        self.doc("records/README.md", "# Records\n\nWhat belongs here.\n")
        self.assertEqual(for_file(self.lint(), "README.md"), [])

    def test_a_misnamed_record_is_still_flagged(self):
        self.doc("records/upgrade-notes.md", "# Notes\n")
        found = for_file(self.lint(), "upgrade-notes.md")
        self.assertEqual(len(found), 1, msgs(found))
        self.assertEqual(found[0].rule, "§7.2.3")


class RecordNaming(DocsCase):
    """§7.2.3: the date is the filename's job."""

    def test_dated_filename_is_clean(self):
        self.doc("records/2026-09-09-collector-0.156.md", "# Upgrade\n")
        self.assertEqual(for_file(self.lint(), "2026-09-09-collector-0.156.md"), [])

    def test_undated_filename_warns(self):
        self.doc("records/collector-upgrade.md", "# Upgrade\n")
        found = for_file(self.lint(), "collector-upgrade.md")
        self.assertEqual(len(found), 1, msgs(found))
        self.assertIn("YYYY-MM-DD-slug.md", found[0].msg)
        self.assertEqual(found[0].gate, "L3")

    def test_a_record_may_narrate_time(self):
        """§7.1.3: a dated document's reader can date what it says."""
        self.doc("records/2026-09-09-collector-0.156.md",
                 "# Upgrade\n\nWe previously pinned 0.155; it was recently dropped.\n")
        self.assertEqual(for_file(self.lint(), "2026-09-09-collector-0.156.md"), [])

    def test_an_adr_may_narrate_time(self):
        self.adr_file("0002-drop-pinning.md",
                      "---\nkind: adr\nstatus: accepted\n---\n\n"
                      "# Drop pinning\n\nWe previously pinned every release.\n")
        self.assertEqual(for_file(self.lint(), "0002-drop-pinning.md"), [])


class TimeNeutrality(DocsCase):
    """§4.7.1 in context files, §7.1.3 in mutable durable docs."""

    def test_mutable_doc_narrating_a_change_warns(self):
        self.doc("guides/deploy.md", "# Deploy\n\nWe migrated from Ansible to Nix.\n")
        found = for_file(self.lint(), "deploy.md")
        self.assertEqual(len(found), 1, msgs(found))
        self.assertEqual(found[0].rule, "§7.1.3")
        self.assertIn("migrated from", found[0].msg)

    def test_mutable_doc_stating_current_state_is_clean(self):
        self.doc("guides/deploy.md", "# Deploy\n\nDeploys run through Nix.\n")
        self.assertEqual(for_file(self.lint(), "deploy.md"), [])

    def test_context_file_narrating_a_change_warns(self):
        _write(os.path.join(self.root, "AGENTS.md"),
               INDEX_AGENTS + "\n## Working here\n\nTests currently run under pytest.\n")
        found = [f for f in self.lint() if f.rule == "§4.7.1"]
        self.assertEqual(len(found), 1, msgs(found))
        self.assertIn("currently", found[0].msg)

    def test_a_quoted_rule_may_name_the_terms_it_forbids(self):
        self.doc("guides/style.md",
                 "# Style\n\n> Avoid 'currently' and 'no longer'.\n\nState the present.\n")
        self.assertEqual(for_file(self.lint(), "style.md"), [])

    def test_innocent_terms_do_not_fire(self):
        """now/since/still/new/old are review-only, by §4.7.1."""
        self.doc("guides/deploy.md",
                 "# Deploy\n\nThe new runner is still supported since it "
                 "knows how to now-cast old jobs.\n")
        self.assertEqual(for_file(self.lint(), "deploy.md"), [], msgs(self.lint()))


class StatusBelongsToTheTracker(DocsCase):
    """§7.3.2: a doc that states its own status is an issue in disguise."""

    def test_durable_doc_with_status_warns(self):
        self.doc("guides/rollout.md",
                 "---\nstatus: active\n---\n\n# Rollout\n\nHow rollout works.\n")
        found = for_file(self.lint(), "rollout.md")
        self.assertEqual(len(found), 1, msgs(found))
        self.assertEqual(found[0].rule, "§7.3.2")
        self.assertEqual(found[0].gate, "",
                         "§9 places §7.3 outside the conformance levels, so the "
                         "substrate check must report without gating one")

    def test_yaml_null_status_is_not_a_status(self):
        """`~` is a null. Findings must not depend on which parser is installed."""
        self.doc("guides/a.md", "---\nstatus: ~\n---\n\n# A\n\nText.\n")
        self.assertEqual(for_file(self.lint(), "a.md"), [])

    def test_adr_status_is_exempt(self):
        """An ADR's status is the decision's lifecycle, not a work report."""
        self.adr_file("0002-use-nix.md")
        self.assertEqual(for_file(self.lint(), "0002-use-nix.md"), [])

    def test_doc_without_status_is_clean(self):
        self.doc("guides/rollout.md", "# Rollout\n\nHow rollout works.\n")
        self.assertEqual(for_file(self.lint(), "rollout.md"), [])


class GlossaryPlacement(DocsCase):
    """§7.2.4: exactly one glossary, beside the project index."""

    def test_glossary_at_the_index_is_clean(self):
        self.doc("glossary.md", "# Glossary\n\n**Reading**: a sensor sample.\n")
        self.assertEqual(for_file(self.lint(), "glossary.md"), [])

    def test_glossary_under_a_module_warns(self):
        _write(os.path.join(self.root, "widgets", "AGENTS.md"),
               "---\nkind: module\ntitle: Widgets\nup: ../AGENTS.md\n---\n\n# Widgets\n")
        _write(os.path.join(self.root, "widgets", "CLAUDE.md"), "@AGENTS.md")
        _write(os.path.join(self.root, "widgets", "docs", "glossary.md"),
               "# Glossary\n\n**Widget**: a widget.\n")
        found = for_file(self.lint(), "glossary.md")
        self.assertEqual(len(found), 1, msgs(found))
        self.assertEqual(found[0].rule, "§7.2.4")


class SizeFloor(DocsCase):
    """§3.4.1: absence of content is not conformance."""

    def lint_with(self, min_lines):
        args = argparse.Namespace(max_lines=200, min_lines=min_lines,
                                  check_remote=False)
        return ads_lint.Linter(self.root, args).run()

    def test_short_context_file_is_reported_as_info(self):
        found = [f for f in self.lint_with(20) if f.rule == "§3.4.1"]
        self.assertEqual(len(found), 1, msgs(found))
        self.assertEqual(found[0].level, ads_lint.INFO)
        self.assertEqual(found[0].gate, "", "the floor must not gate a level")

    def test_floor_can_be_disabled(self):
        self.assertEqual([f for f in self.lint_with(0) if f.rule == "§3.4.1"], [])


if __name__ == "__main__":
    unittest.main()


class RootMustBeANode(unittest.TestCase):
    """§3.1/§6.2: --root is the project index, not "wherever a node turns up".

    Without this the walk adopts any conformant subtree and reports it as the
    whole project, so a non-conformant root passes with a clean bill of health.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)

    def lint(self):
        args = argparse.Namespace(root=self.tmp, max_lines=200, min_lines=20,
                                  check_remote=False)
        return ads_lint.Linter(self.tmp, args).run()

    def test_conformant_subtree_does_not_certify_the_root(self):
        _write(os.path.join(self.tmp, "example", "AGENTS.md"), INDEX_AGENTS)
        found = [f for f in self.lint() if f.rule == "§3.1"]
        self.assertTrue(found, "a root with no AGENTS.md must be an error")
        self.assertEqual(found[0].level, ads_lint.ERROR)
        self.assertEqual(ads_lint.conformance(self.lint())[0], "none")

    def test_root_with_a_node_is_fine(self):
        _write(os.path.join(self.tmp, "AGENTS.md"), INDEX_AGENTS)
        self.assertEqual([f for f in self.lint() if f.rule == "§3.1"], [])


class ClassRulesBindDocsOnly(DocsCase):
    """§7.1.4 is scoped "Within `docs/`" - source folders are not classes."""

    def test_adr_named_source_folder_is_not_an_adr_class(self):
        _write(os.path.join(self.root, "src", "adr", "notes.md"), "# notes\n")
        _write(os.path.join(self.root, "src", "adr", "README.md"), "# readme\n")
        self.assertEqual(for_file(self.lint(), "notes.md"), [])
        self.assertEqual(for_file(self.lint(), "README.md"), [])

    def test_records_named_source_folder_is_not_a_records_class(self):
        _write(os.path.join(self.root, "pkg", "records", "store.md"), "# store\n")
        self.assertEqual(for_file(self.lint(), "store.md"), [])


class RecordDatesAreReal(DocsCase):
    """§7.2.3: the date is the filename's job, so it has to be a date."""

    def test_impossible_date_is_reported(self):
        self.doc("records/2026-99-99-x.md", "# x\n")
        found = for_file(self.lint(), "2026-99-99-x.md")
        self.assertTrue(found, "99-99 is not a calendar date")
        self.assertEqual(found[0].rule, "§7.2.3")

    def test_real_date_passes(self):
        self.doc("records/2026-08-14-bus-partition.md", "# incident\n")
        self.assertEqual(for_file(self.lint(), "2026-08-14-bus-partition.md"), [])


class TimeNeutralityReporting(DocsCase):
    """§4.7.1 in a mutable class (§7.1.3)."""

    def test_every_term_on_a_line_is_reported(self):
        self.doc("guides/g.md",
                 "# G\n\nWe recently moved and previously it was formerly fine.\n")
        found = for_file(self.lint(), "g.md")
        self.assertTrue(found)
        self.assertIn("recently", found[0].msg)
        self.assertIn("previously", found[0].msg)
        self.assertIn("formerly", found[0].msg)

    def test_fenced_code_is_not_prose(self):
        self.doc("guides/h.md",
                 "# H\n\n```sh\n# TODO: currently broken\n```\n\nStable text.\n")
        self.assertEqual(for_file(self.lint(), "h.md"), [])


class SizeFloorCountsTheBody(unittest.TestCase):
    """§3.4.1 says "body", so pointer-heavy frontmatter must not mask an empty one."""

    def test_long_frontmatter_does_not_clear_the_floor(self):
        refs = "\n".join(f"  - m{i}/AGENTS.md" for i in range(20))
        text = f"---\nkind: project-index\ntopology: monorepo\nref:\n{refs}\n---\n\n# P\n"
        self.assertLess(ads_lint.body_line_count(text), 20)
        self.assertGreater(len(text.splitlines()), 20)


class BomDoesNotBreakFrontmatter(unittest.TestCase):
    """A byte-order mark must not read as "no frontmatter"."""

    def test_bom_prefixed_frontmatter_parses(self):
        fm, _ = ads_lint.split_frontmatter("\ufeff---\nkind: module\n---\n\n# M\n")
        self.assertIsNotNone(fm)
        self.assertIn("kind: module", fm)


class TrackerIsAddressedOnce(unittest.TestCase):
    """§7.3.5. A standard built on typed pointers cannot leave its second
    substrate unaddressed, and it is a project property, so it appears once."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)

    def lint(self):
        args = argparse.Namespace(root=self.tmp, max_lines=200, min_lines=0,
                                  check_remote=False)
        return ads_lint.Linter(self.tmp, args).run()

    def _index(self, extra=""):
        _write(os.path.join(self.tmp, "AGENTS.md"),
               "---\nkind: project-index\ntopology: monorepo\n" + extra + "---\n\n# P\n")

    def _t(self):
        return [f for f in self.lint() if f.rule.startswith("\u00a77.3.5")]

    def test_missing_tracker_is_reported(self):
        self._index()
        self.assertTrue(self._t(), "an index with no tracker should be reported")

    def test_url_tracker_passes(self):
        self._index("tracker:\n  at: https://github.com/acme/p/issues\n  kind: github\n")
        self.assertEqual(self._t(), [], msgs(self.lint()))

    def test_org_repo_tracker_passes(self):
        self._index("tracker:\n  at: acme/platform\n")
        self.assertEqual(self._t(), [], msgs(self.lint()))

    def test_nonsense_target_is_reported(self):
        self._index("tracker:\n  at: somewhere\n")
        self.assertTrue(self._t())

    def test_tracker_never_gates_a_level(self):
        """\u00a79 keeps the substrate rule out of the conformance levels."""
        self._index()
        self.assertTrue(all(f.gate == "" for f in self._t()))

    def test_module_must_not_declare_one(self):
        self._index("tracker:\n  at: acme/p\nref:\n  - m/AGENTS.md\n")
        _write(os.path.join(self.tmp, "m", "AGENTS.md"),
               "---\nkind: module\nup: ../AGENTS.md\ntracker:\n  at: acme/p\n---\n\n# M\n")
        self.assertTrue([f for f in self.lint() if f.rule == "\u00a77.3.5.1"])


class FallbackParserHandlesNestedMaps(unittest.TestCase):
    """The built-in parser must accept what PyYAML accepts, or a project's
    findings depend on whether PyYAML happens to be installed."""

    def test_nested_block_mapping(self):
        d = ads_lint._minimal_parse(
            "kind: project-index\ntracker:\n  at: acme/p\n  kind: github\ndocs: ./docs\n")
        self.assertEqual(d["tracker"], {"at": "acme/p", "kind": "github"})
        self.assertEqual(d["docs"], "./docs")

    def test_block_sequence_still_works(self):
        d = ads_lint._minimal_parse("ref:\n  - { at: a/AGENTS.md }\n  - b/AGENTS.md\n")
        self.assertEqual(d["ref"], [{"at": "a/AGENTS.md"}, "b/AGENTS.md"])
