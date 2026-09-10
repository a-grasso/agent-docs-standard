#!/usr/bin/env python3
"""ads-lint - conformance linter for the Agent Docs Standard (ADS).

Validates a project tree against standard/SPEC.md: frontmatter schema, the
up/ref/dep pointer graph, up/ref reciprocity, the docs/ taxonomy and its class
naming rules, and the two prose checks the spec invites - time neutrality
(§4.7.1) and the size floor (§3.4.1). Reports the achieved conformance level
(§9) and what blocks the next one.

Zero external dependencies (Python 3.8+ stdlib only). If PyYAML happens to be
installed it is used for frontmatter parsing; otherwise a built-in parser
handles the ADS frontmatter subset.

Usage:
    ads-lint.py [--root DIR] [--json] [--strict] [--check-remote]
                [--max-lines N] [--min-lines N]

Exit code: 1 if any ERROR (or any WARN under --strict), else 0.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass

ERROR, WARN, INFO = "error", "warn", "info"
SKIP_DIRS = {"node_modules", "dist", "build", "target", "vendor", ".venv", "__pycache__"}
POINTER_KINDS = {"repo", "package", "external-doc"}
ADR_STATUS = {"proposed", "accepted", "superseded", "deprecated"}
REMOTE_RE = re.compile(r"^(git@|ssh://|https?://|git://)")
SLUG = r"[a-z0-9][a-z0-9.-]*"          # §2
ADR_FILE_RE = re.compile(rf"^\d{{4}}-{SLUG}\.md$")
RECORD_FILE_RE = re.compile(rf"^\d{{4}}-\d{{2}}-\d{{2}}-{SLUG}\.md$")

# Classes whose documents are immutable and dated (§7.1.3): §4.7 does not
# reach them, because a dated document's reader can date what it says.
IMMUTABLE_CLASSES = {"adr", "decisions", "records"}

# §4.7.1. Deliberately excludes now/since/still/new/old/legacy: their innocent
# uses are common, and a check that fires on every "now" trains its readers to
# dismiss it. Those remain violations; they are caught by review, not by grep.
TIME_TERMS = [
    "currently", "recently", "no longer", "previously", "used to", "formerly",
    "as of", "we moved", "migrated from", "for now", "temporarily",
    "going forward", "TODO",
]
TIME_RE = re.compile(
    r"(?<![\w-])(" + "|".join(t.replace(" ", r"\s+") for t in TIME_TERMS) + r")(?![\w-])",
    re.IGNORECASE,
)


@dataclass
class Finding:
    level: str
    rule: str          # spec section, e.g. "§5.1"
    path: str          # repo-relative file/dir the finding concerns
    msg: str
    gate: str = ""     # "L1" | "L2" | "L3" - which level this blocks (optional)


# --------------------------------------------------------------------------- #
# Frontmatter parsing
# --------------------------------------------------------------------------- #
def split_frontmatter(text):
    """Return (frontmatter_text_or_None, total_line_count)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, len(lines)
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), len(lines)
    return None, len(lines)  # unterminated fence


def parse_frontmatter(fm_text):
    """Return (data_dict, error_str_or_None)."""
    try:
        import yaml  # optional
    except ImportError:
        return _minimal_parse(fm_text), None
    try:
        data = yaml.safe_load(fm_text)
    except Exception as e:  # noqa: BLE001
        return {}, f"YAML parse error: {e}"
    return (data if isinstance(data, dict) else {}), None


def _split_top(s, sep):
    """Split on `sep` at brace/quote depth 0."""
    parts, buf, quote, depth = [], [], None, 0
    for c in s:
        if quote:
            buf.append(c)
            if c == quote:
                quote = None
        elif c in ("'", '"'):
            quote = c
            buf.append(c)
        elif c in "{[":
            depth += 1
            buf.append(c)
        elif c in "}]":
            depth -= 1
            buf.append(c)
        elif c == sep and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(c)
    parts.append("".join(buf))
    return parts


def _strip_comment(s):
    """Drop a trailing ` # ...` comment that is outside quotes."""
    quote = None
    for j, c in enumerate(s):
        if quote:
            if c == quote:
                quote = None
        elif c in ("'", '"'):
            quote = c
        elif c == "#" and (j == 0 or s[j - 1].isspace()):
            return s[:j]
    return s


def _unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


def _parse_flow_map(s):
    s = s.strip()
    if s.startswith("{"):
        s = s[1:]
    if s.endswith("}"):
        s = s[:-1]
    d = {}
    for part in _split_top(s, ","):
        if ":" in part:
            k, _, v = part.partition(":")
            d[k.strip()] = _unquote(v)
    return d


def _parse_flow_seq(s):
    """Parse `[a, b]` / `[{ id: x }]` / `[]` into a list, matching what PyYAML
    would produce - without this, `dep: []` parses as the string "[]" and is
    then reported as an unresolvable pointer."""
    s = s.strip()
    if s.startswith("["):
        s = s[1:]
    if s.endswith("]"):
        s = s[:-1]
    items = []
    for part in _split_top(s, ","):
        part = part.strip()
        if not part:
            continue
        items.append(_parse_flow_map(part) if part.startswith("{") else _unquote(part))
    return items


def _minimal_parse(fm_text):
    """Parse the ADS frontmatter subset: scalars, flow sequences (`[a, b]`),
    and block lists whose items are flow-maps (`- { a: b }`), block-maps
    (`- a: b` + indented `c: d`), or plain scalars (`- foo`)."""
    data = {}
    lines = fm_text.split("\n")
    i, n = 0, len(lines)
    while i < n:
        line = _strip_comment(lines[i])
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent != 0 or ":" not in line:
            i += 1
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val:
            data[key] = _parse_flow_seq(val) if val.startswith("[") else _unquote(val)
            i += 1
            continue
        # Block value follows.
        i += 1
        items = []
        while i < n:
            l2 = _strip_comment(lines[i])
            if not l2.strip():
                i += 1
                continue
            ind2 = len(l2) - len(l2.lstrip())
            if ind2 == 0:
                break
            s2 = l2.strip()
            if not s2.startswith("- "):
                i += 1
                continue
            item = s2[2:].strip()
            if item.startswith("{"):
                items.append(_parse_flow_map(item))
                i += 1
            elif ":" in item:
                d = {}
                k, _, v = item.partition(":")
                d[k.strip()] = _unquote(v)
                i += 1
                while i < n:  # gather indented continuation keys
                    l3 = _strip_comment(lines[i])
                    if not l3.strip():
                        i += 1
                        continue
                    ind3 = len(l3) - len(l3.lstrip())
                    s3 = l3.strip()
                    if ind3 <= ind2 or s3.startswith("- ") or ":" not in s3:
                        break
                    k2, _, v2 = s3.partition(":")
                    d[k2.strip()] = _unquote(v2)
                    i += 1
                items.append(d)
            else:
                items.append(_unquote(item))
                i += 1
        data[key] = items
    return data


# --------------------------------------------------------------------------- #
# Path resolution
# --------------------------------------------------------------------------- #
def exists_case_sensitive(path, stop_at=None):
    """`os.path.exists`, but case-sensitive on every host filesystem.

    macOS (APFS/HFS+) and Windows resolve `../agents.md` against a file named
    `AGENTS.md`, so a pointer with the wrong case passes locally and 404s on
    Linux CI - the one failure a conformance linter exists to catch. Each
    component is confirmed against the exact spelling its parent lists.

    `stop_at` bounds the walk: components above the project root are supplied
    by the checkout, not written by an author, so they are not the linter's to
    judge.
    """
    p = os.path.normpath(os.path.abspath(path))
    if not os.path.exists(p):
        return False
    stop = os.path.normpath(os.path.abspath(stop_at)) if stop_at else None
    while p != stop:
        parent, name = os.path.split(p)
        if not name or parent == p:
            return True          # reached the filesystem root
        try:
            if name not in os.listdir(parent):
                return False
        except OSError:
            return False
        p = parent
    return True


def case_note(path, stop_at=None):
    """Suffix naming a case mismatch, for a target that exists case-blindly."""
    if os.path.exists(path) and not exists_case_sensitive(path, stop_at):
        return (" (case mismatch: the target exists under a different spelling, "
                "so this resolves on macOS/Windows and fails on Linux)")
    return ""


# --------------------------------------------------------------------------- #
# Node model
# --------------------------------------------------------------------------- #
@dataclass
class Node:
    path: str          # abspath of AGENTS.md
    real: str          # realpath (dedupe / pointer-match key)
    directory: str
    fm: dict
    fm_error: str
    line_count: int


def is_scaffolding(name):
    """§7.1.4. A README or an `_`-prefixed file helps an author write records;
    it is not one, so class naming and lifecycle rules do not bind it."""
    return name.lower() == "readme.md" or name.startswith("_")


def _aslist(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _pointer_target(entry):
    """A ref/dep entry may be a string or a mapping with `at`."""
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        return entry.get("at")
    return None


def discover_nodes(root):
    nodes = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
        ]
        if "AGENTS.md" in filenames:
            p = os.path.join(dirpath, "AGENTS.md")
            try:
                with open(p, encoding="utf-8") as fh:
                    text = fh.read()
            except OSError:
                continue
            fm_text, line_count = split_frontmatter(text)
            if fm_text is None:
                fm, err = {}, "missing or unterminated frontmatter"
            else:
                fm, err = parse_frontmatter(fm_text)
            real = os.path.realpath(p)
            nodes[real] = Node(p, real, dirpath, fm or {}, err or "", line_count)
    return nodes


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #
class Linter:
    def __init__(self, root, args):
        self.root = os.path.abspath(root)
        self.args = args
        self.findings = []

    def rel(self, p):
        return os.path.relpath(p, self.root)

    def add(self, level, rule, path, msg, gate=""):
        self.findings.append(Finding(level, rule, self.rel(path), msg, gate))

    def run(self):
        nodes = discover_nodes(self.root)
        if not nodes:
            self.add(ERROR, "§3.1", self.root, "no AGENTS.md found under root", "L1")
            return self.findings
        self.check_nodes(nodes)
        self.check_graph(nodes)
        index = next((n for n in nodes.values()
                      if n.fm.get("kind") == "project-index"), None)
        self.check_docs(self._docs_dir(index) if index else None)
        return self.findings

    # -- per-node frontmatter & aliases -----------------------------------
    def check_nodes(self, nodes):
        indexes = [n for n in nodes.values() if n.fm.get("kind") == "project-index"]
        if len(indexes) == 0:
            self.add(ERROR, "§4.3", self.root,
                     "no node with kind: project-index (need exactly one)", "L1")
        elif len(indexes) > 1:
            for n in indexes:
                self.add(ERROR, "§4.3", n.path,
                         "multiple project-index nodes; exactly one required", "L1")

        for n in nodes.values():
            if n.fm_error:
                self.add(ERROR, "§4.1", n.path, n.fm_error, "L1")
                continue
            kind = n.fm.get("kind")
            if kind not in ("project-index", "module"):
                self.add(ERROR, "§4.2", n.path,
                         f"kind must be project-index|module (got {kind!r})", "L1")
            if kind == "project-index":
                if "up" in n.fm:
                    self.add(ERROR, "§4.2", n.path,
                             "project-index must not declare up", "L1")
                topo = n.fm.get("topology")
                if topo not in ("monorepo", "polyrepo"):
                    self.add(ERROR, "§6.3.1", n.path,
                             f"project-index must set topology=monorepo|polyrepo "
                             f"(got {topo!r})", "L1")
            if kind == "module":
                if not n.fm.get("up"):
                    self.add(ERROR, "§5.1.2", n.path, "module must declare up", "L1")
                if "topology" in n.fm:
                    self.add(WARN, "§4.2", n.path,
                             "topology belongs on project-index, not module")
            # size budget: a ceiling (§3.4) and a floor (§3.4.1)
            if n.line_count > self.args.max_lines:
                self.add(WARN, "§3.4", n.path,
                         f"context file is {n.line_count} lines "
                         f"(> {self.args.max_lines} budget); move detail into docs/",
                         gate="L3")
            elif n.line_count < self.args.min_lines:
                self.add(INFO, "§3.4.1", n.path,
                         f"context file is {n.line_count} lines "
                         f"(< {self.args.min_lines}); absence of content is not "
                         f"conformance - check what §4.6 admits here")
            self._check_time_neutral(n.path, "§4.7.1")
            self.check_alias(n)

    def check_alias(self, n):
        claude = os.path.join(n.directory, "CLAUDE.md")
        if not os.path.lexists(claude):
            self.add(WARN, "§3.2", n.directory,
                     "no CLAUDE.md alias beside AGENTS.md (symlink recommended)")
            return
        if os.path.islink(claude):
            tgt = os.readlink(claude)
            if os.path.basename(tgt) != "AGENTS.md":
                self.add(WARN, "§3.2", claude,
                         f"CLAUDE.md symlink points to {tgt!r}, not AGENTS.md")
        else:
            try:
                with open(claude, encoding="utf-8") as f:
                    body = f.read().strip()
            except OSError:
                body = None
            if body != "@AGENTS.md":
                self.add(WARN, "§3.2", claude,
                         "CLAUDE.md is a regular file; make it a symlink to AGENTS.md, "
                         "or a stub whose entire body is the import line '@AGENTS.md'")

    # -- pointer graph ----------------------------------------------------
    def check_graph(self, nodes):
        by_real = nodes  # keyed by realpath

        # up resolution + acyclicity + termination
        for n in nodes.values():
            if n.fm.get("kind") != "module":
                continue
            up = n.fm.get("up")
            if not up:
                continue
            self._walk_up(n, nodes)

        # ref target existence + parent/child enumeration
        child_refs = {}  # parent_real -> set(child_real) that parent enumerates
        for n in nodes.values():
            for entry in _aslist(n.fm.get("ref")):
                tgt = _pointer_target(entry)
                if not tgt:
                    self.add(WARN, "§5.2.4", n.path,
                             f"ref entry has no target: {entry!r}")
                    continue
                joined = os.path.join(n.directory, tgt)
                real = os.path.realpath(joined)
                if not exists_case_sensitive(joined, self.root):
                    self.add(ERROR, "§5.2", n.path,
                             f"ref target does not exist: {tgt}"
                             f"{case_note(joined, self.root)}", "L2")
                elif os.path.basename(real) not in ("AGENTS.md", "CLAUDE.md"):
                    self.add(WARN, "§5.2", n.path,
                             f"ref target is not a context file: {tgt}")
                child_refs.setdefault(n.real, set()).add(real)

        # every module should be enumerated by its parent (§5.2.2)
        for n in nodes.values():
            if n.fm.get("kind") != "module":
                continue
            up = n.fm.get("up")
            if not up:
                continue
            parent_real = os.path.realpath(os.path.join(n.directory, up))
            if parent_real not in nodes:
                continue  # broken up already reported by _walk_up
            if n.real not in child_refs.get(parent_real, set()):
                self.add(WARN, "§5.2.2", nodes[parent_real].path,
                         f"does not enumerate child module in ref: "
                         f"{self.rel(n.path)}", gate="L2")

        # dep checks
        for n in nodes.values():
            self._check_deps(n)

    def _walk_up(self, start, nodes):
        seen = set()
        cur = start
        while True:
            up = cur.fm.get("up")
            if not up:
                if cur.fm.get("kind") != "project-index":
                    self.add(ERROR, "§5.1.2", start.path,
                             "up chain ends at a node that is not project-index",
                             "L1")
                return
            joined = os.path.join(cur.directory, up)
            parent_real = os.path.realpath(joined)
            if parent_real == cur.real or parent_real in seen:
                self.add(ERROR, "§5.5.1", start.path,
                         "up pointer forms a cycle", "L1")
                return
            if parent_real not in nodes or not exists_case_sensitive(
                    joined, self.root):
                self.add(ERROR, "§5.1", cur.path,
                         f"up target does not resolve to a node: {up}"
                         f"{case_note(joined, self.root)}", "L1")
                return
            seen.add(cur.real)
            cur = nodes[parent_real]

    def _check_deps(self, n):
        for entry in _aslist(n.fm.get("dep")):
            if isinstance(entry, str):
                self.add(WARN, "§5.3.2", n.path,
                         f"dep should be a mapping with id/at/hint: {entry!r}")
                at, dep_id, kind = entry, None, None
            elif isinstance(entry, dict):
                at, dep_id, kind = entry.get("at"), entry.get("id"), entry.get("kind")
                if not dep_id:
                    self.add(WARN, "§5.3.2", n.path, f"dep missing id: {entry!r}")
                if kind and kind not in POINTER_KINDS:
                    self.add(WARN, "§5.3.2", n.path,
                             f"dep kind {kind!r} not in {sorted(POINTER_KINDS)}")
            else:
                self.add(WARN, "§5.3", n.path, f"malformed dep entry: {entry!r}")
                continue
            if not at:
                self.add(ERROR, "§5.3.2", n.path, f"dep missing at: {entry!r}", "L2")
                continue
            if REMOTE_RE.match(at):
                if self.args.check_remote:
                    self._check_remote(n, dep_id or at, at)
            else:  # local path
                local = at.split("#", 1)[0]
                joined = os.path.join(n.directory, local)
                if not exists_case_sensitive(joined, self.root):
                    self.add(ERROR, "§5.3.3", n.path,
                             f"local dep target does not exist: {at}"
                             f"{case_note(joined, self.root)}", "L2")

    def _check_remote(self, n, dep_id, at):
        url = at.split("#", 1)[0]
        if url.startswith(("http://", "https://")):
            ok = _http_ok(url)
        else:
            ok = _git_ok(url)
        if ok is False:
            self.add(WARN, "§5.3.3", n.path, f"dep {dep_id} unreachable: {url}")

    # -- docs taxonomy ----------------------------------------------------
    def check_docs(self, index_docs=None):
        saw_adr = False
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [
                d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
            ]
            parent = os.path.basename(dirpath)
            in_docs = "docs" in os.path.relpath(dirpath, self.root).split(os.sep)
            for f in filenames:
                if not f.endswith(".md"):
                    continue
                full = os.path.join(dirpath, f)
                if in_docs and is_scaffolding(f):
                    continue          # §7.1.4: class rules bind records only
                if parent == "adr":
                    saw_adr = True
                    self._check_adr(full, f)
                    continue
                if parent == "records":
                    self._check_record(full, f)
                    continue
                if not in_docs:
                    continue
                if f == "glossary.md":
                    self._check_glossary_placement(full, dirpath, index_docs)
                self._check_status_frontmatter(full)
                if parent not in IMMUTABLE_CLASSES:
                    self._check_time_neutral(full, "§7.1.3")
        if not saw_adr:
            self.add(INFO, "§7.2.1", self.root,
                     "no docs/adr/ found; major decisions should be ADRs", gate="L3")

    def _read_fm(self, full):
        try:
            with open(full, encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            return {}, "unreadable"
        fm_text, _ = split_frontmatter(text)
        if fm_text is None:
            return {}, "missing frontmatter"
        fm, err = parse_frontmatter(fm_text)
        return fm, err

    def _check_adr(self, full, name):
        if not ADR_FILE_RE.match(name):
            self.add(WARN, "§7.2.1", full,
                     "ADR filename must be NNNN-slug.md", gate="L3")
        fm, err = self._read_fm(full)
        status = fm.get("status")
        if status not in ADR_STATUS:
            self.add(WARN, "§7.2.1", full,
                     f"ADR status must be one of {sorted(ADR_STATUS)} (got {status!r})",
                     gate="L3")

    def _check_record(self, full, name):
        """§7.2.3. The date is the filename's job, so the class sorts and every
        document in it is dated by construction."""
        if not RECORD_FILE_RE.match(name):
            self.add(WARN, "§7.2.3", full,
                     "record filename must be YYYY-MM-DD-slug.md", gate="L3")

    @staticmethod
    def _docs_dir(node):
        return os.path.realpath(
            os.path.join(node.directory, str(node.fm.get("docs") or "./docs")))

    def _check_glossary_placement(self, full, dirpath, index_docs):
        """§7.2.4. Exactly one glossary, beside the project index, so that one
        concept has one canonical term across every node."""
        if index_docs and os.path.realpath(dirpath) != index_docs:
            self.add(WARN, "§7.2.4", full,
                     "a project has exactly one glossary, in the project index's "
                     "docs/; this one is under a module", gate="L3")

    def _check_status_frontmatter(self, full):
        """§7.3.2. A durable document that states its own status is an issue
        wearing a document's clothes. `adr/` is exempt: its status is the
        decision's own lifecycle, not a report on work in flight."""
        fm, _ = self._read_fm(full)
        if fm.get("status") is not None:
            self.add(WARN, "§7.3.2", full,
                     f"durable doc declares status: {fm['status']!r}; status "
                     "belongs to the tracker, not the repository", gate="L3")

    def _check_time_neutral(self, full, rule):
        """§4.7.1. Narration of a change, in a document nobody can date."""
        try:
            with open(full, encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            return
        fm_text, _ = split_frontmatter(text)
        body = text[text.index(fm_text) + len(fm_text):] if fm_text else text
        hits = []
        for line in body.splitlines():
            if line.lstrip().startswith(">"):
                continue          # a quoted rule may name the terms it forbids
            m = TIME_RE.search(line)
            if m and m.group(0).lower() not in hits:
                hits.append(m.group(0).lower())
        if hits:
            self.add(WARN, rule, full,
                     "time-connotated prose in a document its reader cannot date: "
                     + ", ".join(f"{h!r}" for h in hits[:5]))


def _http_ok(url):
    try:
        import urllib.request
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=8) as r:  # noqa: S310
            return 200 <= r.status < 400
    except Exception:  # noqa: BLE001
        return False


def _git_ok(url):
    try:
        r = subprocess.run(["git", "ls-remote", url], capture_output=True,
                           timeout=15)
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


# --------------------------------------------------------------------------- #
# Conformance & reporting
# --------------------------------------------------------------------------- #
def conformance(findings):
    has_error = any(f.level == ERROR for f in findings)
    l2_block = any(f.gate == "L2" for f in findings)
    l3_block = any(f.gate == "L3" for f in findings)
    if has_error:
        return "none", "errors present - fix before claiming any level"
    if l2_block:
        return "L1", "graph gaps block L2 (see L2-gated findings)"
    if l3_block:
        return "L2", "docs/ taxonomy gaps block L3 (see L3-gated findings)"
    return "L3", "fully conformant"


COLORS = {ERROR: "\033[31m", WARN: "\033[33m", INFO: "\033[36m", "reset": "\033[0m"}


def report_text(findings, level, note, use_color):
    def c(k):
        return COLORS.get(k, "") if use_color else ""

    order = {ERROR: 0, WARN: 1, INFO: 2}
    for f in sorted(findings, key=lambda x: (order[x.level], x.path)):
        gate = f" [{f.gate}]" if f.gate else ""
        print(f"{c(f.level)}{f.level.upper():5}{c('reset')} {f.rule:8} "
              f"{f.path}{gate}\n      {f.msg}")
    ne = sum(f.level == ERROR for f in findings)
    nw = sum(f.level == WARN for f in findings)
    ni = sum(f.level == INFO for f in findings)
    print(f"\n{len(findings)} finding(s): {ne} error, {nw} warn, {ni} info")
    print(f"conformance: {c(ERROR if level=='none' else WARN if level!='L3' else INFO)}"
          f"{level}{c('reset')} - {note}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lint a project against the Agent Docs Standard.")
    ap.add_argument("--root", default=".", help="project root to lint (default: .)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--strict", action="store_true", help="exit non-zero on warnings too")
    ap.add_argument("--check-remote", action="store_true",
                    help="verify remote dep targets (git/https); needs network")
    ap.add_argument("--max-lines", type=int, default=200,
                    help="context-file size budget (default: 200)")
    ap.add_argument("--min-lines", type=int, default=20,
                    help="context-file size floor (default: 20; §3.4.1)")
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args(argv)

    findings = Linter(args.root, args).run()
    level, note = conformance(findings)

    if args.json:
        print(json.dumps({
            "root": os.path.abspath(args.root),
            "conformance": level,
            "note": note,
            "counts": {
                "error": sum(f.level == ERROR for f in findings),
                "warn": sum(f.level == WARN for f in findings),
                "info": sum(f.level == INFO for f in findings),
            },
            "findings": [vars(f) for f in findings],
        }, indent=2))
    else:
        use_color = sys.stdout.isatty() and not args.no_color
        report_text(findings, level, note, use_color)

    has_error = any(f.level == ERROR for f in findings)
    has_warn = any(f.level == WARN for f in findings)
    return 1 if (has_error or (args.strict and has_warn)) else 0


if __name__ == "__main__":
    sys.exit(main())
