#!/usr/bin/env python3
"""derive_public_tree.py -- build the PUBLIC-SAFE derived tree for the 2026-09-14 work meeting
(lane PUB-1 of CFL's week map; Jon 2026-09-02: "Professionalism must ensure i can share the
public github with work in this wikiskills context and beyond").

HOW THIS DIFFERS FROM scripts/lanes/derive_depii_branch.sh (READ THIS BEFORE EDITING EITHER)
-------------------------------------------------------------------------------------------
`derive_depii_branch.sh` is a REDACTING deriver: its STRIP class publishes a file with identifier
spans rewritten in place, and its SUMMARIZE class replaces a file with a stub. Both are
MODIFICATIONS OF THE RECORD, and this lane is forbidden to make them:

    Jon, 2026-08-11 (Claude Personal trunk, wiki/sources/jon-messages/jon-0740-rulings-2026-08-11.md):
    "please don't make key PII info harder to use it's often relevent" ...
    "It's fine in any file the resident can read."

Over-scrubbing is a violation, not a safe default, and it is the direction with no alarm. So this
script has exactly TWO dispositions:

    INCLUDE   copied byte-identical from the source ref
    EXCLUDE   absent entirely, and LOGGED (path, class, line) in DERIVATION-LOG.md

There is no third. A file with one hit is excluded WHOLE. Nothing is ever rewritten, and nothing
in the working tree is ever touched -- the output is a separate directory.

WHAT THE SCAN IS
----------------
Not a new lexicon. It reuses, unchanged, the two instruments that already carry the measurements:
  * scripts/audit/depii_lexicon.py -- L1 structured identifiers + the file-backed name gazetteer,
    with the precision fixes Soul measured on this corpus (ACCOUNT 203->1, CARD 35->0).
  * scripts/audit/ingest_gate.py fence v2 -- card_true_positive_hits(), financial_content_hits(),
    XC_EXCHEQUER_DIR_RX, FENCE_PATH_RX. Fence v2 is the version carrying Professional's 09:2x
    correction: the XC-Exchequer invariant is about CONTENT LEAVING THE DIRECTORY, not the NAME
    being spoken.

A KNOWN LIMIT, STATED HERE BECAUSE CODE CANNOT FIX IT: if no gazetteer file exists, NAME coverage
is ZERO. depii_lexicon.load_gazetteer() prints a loud line and returns []. This script re-prints
it as a first-class finding and stamps it into DERIVATION-LOG.md, because a scan that looked for
no names is an UNARMED scan, not a clean one, and UNKNOWN never rounds to PASS.

Usage:
  derive_public_tree.py --repo REPO --out DIR [--ref HEAD]
  derive_public_tree.py --src-mode fs --src-root DIR --out DIR   # leak-control harness mode
"""
import argparse
import hashlib
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import depii_lexicon
import ingest_gate

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# --- INCLUDE SPEC (path level) --------------------------------------------------------------
# Allow-list, not deny-list. A path matching nothing here is NOT CONSIDERED. The deny list below
# is defence in depth only, for classes that must never appear even by an editing accident.

EXACT_INCLUDE = {
    "wiki/WIKISKILLS-PROTOTYPE.md",
    "wiki/skills-gate/GATE-SPEC.md",
    "wiki/skills-gate/LEDGER.md",
    "wiki/skills-gate/INGEST-LEDGER.md",
    "wiki/skills-gate/skill-impact.md",
}
PREFIX_INCLUDE = (
    "wiki/patterns/",
    "wiki/concepts/",
    "wiki/references/",
    "wiki/entities/",
    "wiki/sources/",
    "wiki/skills-gate/validation/",
    ".claude/hooks/",
)
# plus: scripts/audit/*.py  (source only)
# plus: skills/*/SKILL.md and skills/*/PURPOSE.md

# --- THE EXCLUSION SET IS READ FROM A FILE, NEVER INFERRED FROM PROSE -----------------------
# Professional's finding, 2026-09-02: an exclusion set derived from repo prose has a hole exactly
# at XC-Exchequer, because that invariant lives in the UNIVERSAL layer, not in every trunk's
# documents. So the set is an explicit, checked list. Missing file => abort. XC-Exchequer absent
# from DIR_NAME => abort. Both are hard assertions, not warnings.
EXCLUSIONS_FILE = os.path.join(HERE, "public_exclusions.txt")
REQUIRED_DIR_NAMES = ("XC-Exchequer",)


KNOWN_KEYS = ("PATH_PREFIX", "PATH_EXACT", "DIR_NAME", "CONTENT_CLASS", "TRUNK_ALLOW",
              "ENTITY_TYPE_ALLOW", "FM_HELD_KEY", "FM_HELD_VALUE", "VALUE_WALK", "SHAPE_SCAN")


def load_exclusions(path=EXCLUSIONS_FILE):
    if not os.path.isfile(path):
        raise SystemExit("ABORT [fail-closed]: exclusion list missing at %s. The set is never "
                         "inferred; nothing was written." % path)
    spec = {}
    comments = {}
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            raw = ln
            ln = ln.split("  #", 1)[0].split(" #", 1)[0].rstrip()  # trailing comment
            comment = raw[len(ln):].strip().lstrip("#").strip()
            key, _, val = ln.partition(" ")
            val = val.strip()
            if comment:
                # PUB-2d, Professional's v3 verification: a PATH_EXACT row's comment is the
                # only place the WITHHOLD basis is written; it travels into the log with the row.
                comments[(key.strip(), val)] = comment
            if not val:
                raise SystemExit("ABORT: malformed exclusion directive: %r" % ln)
            key = key.strip()
            if key not in KNOWN_KEYS:
                # 2026-09-02: two semantic WITHHOLD rows were written as bare paths and
                # parsed as directive keys -- silently honoured as nothing. Unknown = abort.
                raise SystemExit("ABORT: unknown exclusion directive key %r in line %r" % (key, ln))
            spec.setdefault(key, []).append(val)
    spec["_COMMENTS"] = comments
    for req in ("PATH_PREFIX", "DIR_NAME", "CONTENT_CLASS", "TRUNK_ALLOW",
                "ENTITY_TYPE_ALLOW", "FM_HELD_KEY", "FM_HELD_VALUE"):
        if not spec.get(req):
            raise SystemExit("ABORT [fail-closed]: exclusion list has no %s entries." % req)
    for req in REQUIRED_DIR_NAMES:
        if req not in spec["DIR_NAME"]:
            raise SystemExit("ABORT [fail-closed]: exclusion list does not name %r as a "
                             "DIR_NAME. That invariant is universal-layer and must be written "
                             "out explicitly; nothing was written." % req)
    return spec


def _exclusions_sha(path=EXCLUSIONS_FILE):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


EX = load_exclusions()
DENY_PREFIX = tuple(EX["PATH_PREFIX"])
DENY_EXACT = set(EX.get("PATH_EXACT", []))  # whole-file semantic WITHHOLD rows
EX_COMMENTS = EX.get("_COMMENTS", {})        # (KEY, value) -> trailing comment text
# VALUE_WALK <literal>  # class -- Professional's quarantine finding, 2026-09-02: withholding the
# file that INTRODUCES an identifier does not withhold the identifier (a Drive folder id withheld
# with one SKILL.md was found again in a wiki source page). Each literal is walked, fixed-string
# and case-sensitive, over every INCLUDED file after derivation. The literal itself is NEVER
# printed to the log or stdout -- only sha256[:8] and its class -- so the log cannot leak what
# it guards. Treat public_exclusions.txt as sensitive input for the same reason.
VALUE_WALK = [(lit, EX_COMMENTS.get(("VALUE_WALK", lit), "(no class)"))
              for lit in EX.get("VALUE_WALK", [])]
# SHAPE_SCAN <name> <regex> -- Professional's amendment after running the value walk (it found
# two more Google resource ids the file-level pass had missed): a DETECTOR for token SHAPES
# (e.g. 33- and 44-char mixed-case-plus-digit ids), bounded by non-token characters. It feeds a
# human decision and carries NO exit code. The token is never printed -- only its LENGTH.
_TOKEN_CH = r"[A-Za-z0-9_\-]"
SHAPE_SCAN = []
for _v in EX.get("SHAPE_SCAN", []):
    _name, _, _rx = _v.partition(" ")
    if not _rx.strip():
        raise SystemExit("ABORT: SHAPE_SCAN row needs `<name> <regex>`: %r" % _v)
    SHAPE_SCAN.append((_name.strip(),
                       re.compile(r"(?<!%s)(?:%s)(?!%s)" % (_TOKEN_CH, _rx.strip(), _TOKEN_CH))))
DENY_DIR_NAMES = set(EX["DIR_NAME"])
CONTENT_CLASSES = set(EX["CONTENT_CLASS"])
# CLASSES THAT REPORT AND DO NOT CUT. The per-file loop does `if hits: continue`, so ANY row a
# classifier returns withholds the file -- which makes a "report-only" verdict a LIE unless it
# travels in a different list. [2026-09-13 00:2x: the first version of the T5 fix returned
# FM-HELD-PROSE as a normal row; it would have renamed the reason and still cut the page. Caught by
# reading the call site instead of trusting the classifier's own vocabulary.]
REPORT_ONLY_CLASSES = {"FM-HELD-PROSE", "FM-STATUS-HELD-PROSE"}
ENTITY_TYPE_ALLOW = set(x.lower() for x in EX["ENTITY_TYPE_ALLOW"])
TRUNK_ALLOW = set(x.lower() for x in EX["TRUNK_ALLOW"])

HELD_KEY_RX = re.compile("|".join(re.escape(x) for x in EX["FM_HELD_KEY"]), re.I)
HELD_VAL_RX = re.compile("|".join(r"\b%s\b" % re.escape(x) for x in EX["FM_HELD_VALUE"]), re.I)


# --- INCLUDE SPEC, made overridable 2026-09-11 (PUB-2) --------------------------------
# Professional, 2026-09-11: run 2 over N:\claude-professional never CONSIDERED 3,055 of 3,320
# paths, because this spec was hard-coded to CFL's shape -- that trunk's instruments live at
# scripts/*.py and scripts/*.sh and match nothing here. A 243-included count off another
# trunk's spec is not coverage of that trunk, and a clean number for the wrong reason is the
# failure this whole pipeline exists to prevent.
#
# So each SOURCE ROOT may now carry its own spec beside its own log, which is the same shape
# as the two-runs/two-outputs decision. --include-spec is OPTIONAL and the default is exactly
# the values above, so CFL's runs are byte-identical without it.
#
# FAIL-CLOSED, like the exclusions file and for the same reason: a spec that is missing, empty,
# unparseable, or carries no include keys ABORTS. It must never silently fall back to the
# built-in list, because that would publish one trunk's tree under another trunk's rules.
INCLUDE_SPEC_KEYS = ("EXACT_INCLUDE", "PREFIX_INCLUDE", "SUFFIX_UNDER", "BASENAME_UNDER")
_SPEC = None  # set by load_include_spec(); None means "use the built-ins"


def load_include_spec(path):
    """Parse a key-prefixed include spec. Returns a dict; aborts rather than degrading."""
    global _SPEC
    if not os.path.exists(path):
        raise SystemExit("ABORT [fail-closed]: --include-spec %r does not exist. The spec is "
                         "never inferred and never defaulted when asked for." % path)
    spec = {k: [] for k in INCLUDE_SPEC_KEYS}
    with io.open(path, encoding="utf-8") as fh:
        for n, raw in enumerate(fh, 1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                raise SystemExit("ABORT [fail-closed]: --include-spec %s:%d is not "
                                 "'<KEY> <value>': %r" % (path, n, raw.strip()))
            key, val = parts[0], parts[1].strip()
            if key not in spec:
                raise SystemExit("ABORT [fail-closed]: --include-spec %s:%d unknown key %r; "
                                 "known keys are %s" % (path, n, key, ", ".join(INCLUDE_SPEC_KEYS)))
            spec[key].append(val)
    if not any(spec[k] for k in INCLUDE_SPEC_KEYS):
        raise SystemExit("ABORT [fail-closed]: --include-spec %r has no include entries. An "
                         "empty allow-list would consider nothing and report a clean tree." % path)
    _SPEC = spec
    return spec


def considered(path):
    if _SPEC is None:
        # built-in CFL spec, unchanged
        if path in EXACT_INCLUDE:
            return True
        if path.startswith(PREFIX_INCLUDE):
            return True
        if path.startswith("scripts/audit/") and path.endswith(".py"):
            return True
        parts = path.split("/")
        if len(parts) == 3 and parts[0] == "skills" and parts[2] in ("SKILL.md", "PURPOSE.md"):
            return True
        return False
    if path in set(_SPEC["EXACT_INCLUDE"]):
        return True
    for pre in _SPEC["PREFIX_INCLUDE"]:
        if path.startswith(pre):
            return True
    # SUFFIX_UNDER <dir> <suffix>  -- e.g. "SUFFIX_UNDER scripts/ .py"
    for row in _SPEC["SUFFIX_UNDER"]:
        bits = row.split()
        if len(bits) == 2 and path.startswith(bits[0]) and path.endswith(bits[1]):
            return True
    # BASENAME_UNDER <dir> <depth> <name>  -- e.g. "BASENAME_UNDER skills/ 3 SKILL.md"
    for row in _SPEC["BASENAME_UNDER"]:
        bits = row.split()
        if len(bits) == 3 and path.startswith(bits[0]):
            try:
                depth = int(bits[1])
            except ValueError:
                continue
            parts = path.split("/")
            if len(parts) == depth and parts[-1] == bits[2]:
                return True
    return False


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return {}
    fm = {}
    for ln in lines[1:60]:
        if ln.strip() == "---":
            break
        m = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", ln)
        if m:
            fm[m.group(1).strip().lower()] = m.group(2).strip()
    return fm


# --- EXCLUSION CLASSES ----------------------------------------------------------------------

def path_exclusions(path, gaz):
    """(class, line, detail) from the PATH STRING ALONE. THE FILENAME IS THE DISCLOSURE."""
    out = []
    norm = path.replace("\\", "/")
    if ingest_gate.FENCE_PATH_RX.search("/" + norm):
        out.append(("PATH-FENCE-PERSONAL-HOME", 0, norm))
    comps = [p for p in norm.split("/") if p]
    for dn in sorted(DENY_DIR_NAMES):
        if dn in comps:
            out.append(("PATH-%s" % dn.upper(), 0, norm))
    if norm.startswith(DENY_PREFIX):
        out.append(("PATH-DENY-PREFIX", 0, norm))
    if norm in DENY_EXACT:
        out.append(("PATH-DENY-EXACT", 0, norm))
    for cls, _ in depii_lexicon.scan_path(norm, gaz):
        out.append(("PATH-LEXICON-" + cls, 0, norm))
    return out


def frontmatter_exclusions(path, fm):
    out = []
    if not fm:
        return out
    trunk = fm.get("trunk", "").strip().lower()
    if trunk and trunk not in TRUNK_ALLOW:
        out.append(("FM-TRUNK-NOT-FL", 0, "trunk: %s" % trunk))
    # ⛔ T5 SECOND CODE PATH, reopened by Professional as RAISER 2026-09-13 00:3x after I declared the
    # class closed. I split the verdict on HELD_VAL_RX (below) and left THIS matcher untouched -- a
    # separate `re.search(r"\bHELD\b", status)` three lines above the comment I wrote about the defect.
    # Their page was still cut, now as FM-STATUS-HELD on `status: LIVE -- positions held by this seat`.
    # ⭐ THE FINDER CLOSES THE LOOP, NOT THE AUTHOR. I fixed one path, ran MY tree where neither path
    # fires, saw no change, and called it done. They re-ran THEIR tree and the page was still gone.
    # ⚠️ And "same class, second code path" is the generalisable half: a vocabulary defect lives in
    # every matcher that shares the vocabulary, so the unit of repair is the CLASS, never the line.
    status = fm.get("status", "").strip()
    if status and re.search(r"\bHELD\b", status, re.I):
        _st = status.strip("\"'").strip()
        _stoks = _st.split()
        _declared = bool(_stoks) and (
            re.fullmatch(r"HELD", _st, re.I) is not None
            or (len(_stoks) <= 3 and re.fullmatch(r"HELD", _stoks[0].strip(":,;()"), re.I) is not None))
        if _declared:
            out.append(("FM-STATUS-HELD", 0, "status: %s" % status))
        else:
            out.append(("FM-STATUS-HELD-PROSE", 0,
                        "status: %s  [REPORT ONLY -- 'held' appears in a %d-token status whose "
                        "declared value is not HELD; nothing was cut for this]"
                        % (status, len(_stoks))))
    # ⛔ T5, raised by Professional 2026-09-13 00:1x and it is CFL's defect: HELD_VAL_RX matches
    # \bheld\b anywhere in a value's PROSE, so their LIVE page was cut for a sentence about being
    # held to a standard. FM_HELD_KEY includes `visibility` and FM_HELD_VALUE includes held /
    # personal / private -- all ordinary English -- so any narrative value under a common key trips it.
    #
    # ⭐ THE FIX IS NOT TO LOOSEN THE MATCH. On a PUBLIC surface, failing open is the dangerous
    # direction, and a real marker buried in prose must still be caught. So the VERDICT is split:
    #   FM-HELD-PERSONAL -- the value IS the marker (equality, or a marker plus a short qualifier).
    #                       Still CUTS. Fail-closed preserved.
    #   FM-HELD-PROSE    -- a marker WORD appears inside a longer value. REPORTED, never cut, and
    #                       named so a reader disposes of it instead of discovering the cut later.
    # A page is not withheld for a sentence; it is withheld for a declaration.
    for k, v in fm.items():
        if not (HELD_KEY_RX.search(k) and HELD_VAL_RX.search(v or "")):
            continue
        _val = (v or "").strip().strip("\"'").strip()
        _toks = _val.split()
        _is_marker = bool(_toks) and (
            HELD_VAL_RX.fullmatch(_val) is not None
            or (len(_toks) <= 3 and HELD_VAL_RX.fullmatch(_toks[0].strip(":,;()")) is not None))
        if _is_marker:
            out.append(("FM-HELD-PERSONAL", 0, "%s: %s" % (k, v)))
        else:
            out.append(("FM-HELD-PROSE", 0,
                        "%s: %s  [REPORT ONLY -- a held word inside a %d-token value is not a "
                        "declaration; nothing was cut for this]" % (k, v, len(_toks))))
    if path.startswith("wiki/entities/"):
        et = fm.get("entity_type", "").strip().lower()
        if et not in ENTITY_TYPE_ALLOW:
            out.append(("ENTITY-NOT-SEAT-OR-SYSTEM", 0, "entity_type: %s" % (et or "(absent)")))
    return out


def content_exclusions(text, gaz):
    """The ingest fence v2 content classes, decomposed so each hit keeps its class AND line."""
    out = []
    for cls, ln in depii_lexicon.scan_only(text, gaz):
        if cls == "CARD":
            continue          # CARD handled by the fence's false-positive-aware version below
        if cls in CONTENT_CLASSES:
            out.append(("CONTENT-" + cls, ln, ""))
    if "CARD" in CONTENT_CLASSES:
        for ln in ingest_gate.card_true_positive_hits(text):
            out.append(("CONTENT-CARD", ln, "Luhn-valid, non-excluded context"))
    if "XC-EXCHEQUER-PATH" in CONTENT_CLASSES:
        for m in sorted(set(x.group(0) for x in ingest_gate.XC_EXCHEQUER_DIR_RX.finditer(text))):
            out.append(("CONTENT-XC-EXCHEQUER-PATH", text.count("\n", 0, text.find(m)) + 1, m))
    if "FINANCIAL" in CONTENT_CLASSES:
        for detail in ingest_gate.financial_content_hits(text):
            out.append(("CONTENT-FINANCIAL", 0, detail))
    return out


# --- SOURCE READERS -------------------------------------------------------------------------

def git_paths(repo, ref):
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref],
                         cwd=repo, capture_output=True, check=True)
    return [p for p in out.stdout.decode("utf-8", "surrogateescape").split("\n") if p]


def git_read_many(repo, ref, paths):
    """Stream blobs via `git cat-file --batch` -- one subprocess for the whole set."""
    res = {}
    if not paths:
        return res
    p = subprocess.Popen(["git", "cat-file", "--batch"], cwd=repo,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    req = "".join("%s:%s\n" % (ref, x) for x in paths).encode("utf-8", "surrogateescape")
    out, _ = p.communicate(req)
    i = 0
    for path in paths:
        nl = out.find(b"\n", i)
        header = out[i:nl].decode("utf-8", "replace")
        i = nl + 1
        parts = header.split()
        if len(parts) != 3 or parts[1] != "blob":
            res[path] = None            # missing / not-a-blob -> fail closed downstream
            continue
        size = int(parts[2])
        res[path] = out[i:i + size]
        i += size + 1
    return res


def fs_paths(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            out.append(os.path.relpath(full, root).replace("\\", "/"))
    return sorted(out)


# --- REFERENCE SURVIVORS (lane PUB-2d) --------------------------------------------------------
# Professional's finding, 2026-09-02: a whole-file WITHHOLD removes a BODY from the derived tree,
# but every inbound reference to it survives BY NAME in the included files -- [[slug]] wikilinks,
# backtick paths, plain path mentions -- and a per-file exclusion list has no concept of the
# reference graph. Six such refs to that day's withheld files were found by hand.
#
# This scan DISCLOSES, it never rewrites: INCLUDE byte-identical or EXCLUDE whole-file is still the
# only rule, and a reference by name is disclosed as a name only. Five forms are matched, and each
# (included file, line, excluded file) triple is recorded once under its most specific form:
#   FULL      the repo-relative path            wiki/references/x-y.md
#   SUFFIX    parent-dir + basename             references/x-y.md
#   FILENAME  the basename                      x-y.md        -- only if UNIQUE at source
#   WIKILINK  [[stem]] / [[stem|..]] / [[stem#..]]            -- only if the stem is UNIQUE
#   STEM      the bare basename stem            x-y           -- only if UNIQUE and slug-shaped
# First real run (v4, 2026-09-02): without the uniqueness rule `SKILL.md` matched 587 lines for
# EVERY withheld skill and the word `trunks` matched 174 lines of prose. A name shared by other
# files at source, or a plain dictionary word, is not a reference to the withheld file; those
# forms are dropped for that file and the drop is disclosed in the section's `forms` column.
# --fail-on-survivors exits 4 when a PATH_EXACT row (the whole-file semantic WITHHOLD directive)
# has >= 1 survivor, so the consumer can choose to gate on it; SCAN- and PATH_PREFIX-excluded
# files are listed but never gate (their exclusion was mechanical, not a judgment about the name).

_REF_LB = r"(?<![A-Za-z0-9_\-.])"
_REF_LA = r"(?![A-Za-z0-9_\-])"
_EXCL_ORDER = {"PATH_EXACT": 0, "PATH_PREFIX": 1, "SCAN": 2}


_SLUG_RX = re.compile(r"[-_0-9]")


def _survivor_forms(excl_paths, all_paths):
    """Which forms are ARMED for each excluded path, given every path at source.
    Returns ({excluded_path: {form: key}}, {excluded_path: [dropped-form reasons]})."""
    fn_count, stem_count = {}, {}
    for q in all_paths:
        fn = q.rsplit("/", 1)[-1]
        st = fn.rsplit(".", 1)[0] if "." in fn else fn
        fn_count[fn] = fn_count.get(fn, 0) + 1
        stem_count[st] = stem_count.get(st, 0) + 1
    forms, dropped = {}, {}
    for p in excl_paths:
        fn = p.rsplit("/", 1)[-1]
        stem = fn.rsplit(".", 1)[0] if "." in fn else fn
        parts = p.split("/")
        f = {"FULL": p}
        d = []
        if len(parts) >= 2:
            f["SUFFIX"] = parts[-2] + "/" + fn
        if fn_count.get(fn, 0) == 1:
            f["FILENAME"] = fn
        else:
            d.append("FILENAME (%d files at source named %s)" % (fn_count.get(fn, 0), fn))
        if stem_count.get(stem, 0) == 1:
            f["WIKILINK"] = "[[" + stem
            if len(stem) >= 4 and _SLUG_RX.search(stem):
                f["STEM"] = stem
            else:
                d.append("STEM (%r is a plain word, not slug-shaped)" % stem)
        else:
            d.append("WIKILINK+STEM (%d paths at source share stem %s)" % (stem_count.get(stem, 0), stem))
        forms[p] = f
        dropped[p] = d
    return forms, dropped


def _survivor_regex(forms):
    """One alternation over every ARMED form of every excluded path, longest-first inside each
    form group so that at a given position FULL beats SUFFIX beats FILENAME beats STEM.
    Returns (rx, lookup) where lookup maps the matched text to [(excluded_path, form), ...]."""
    lookup = {}
    groups = {"FULL": set(), "SUFFIX": set(), "WIKILINK": set(), "FILENAME": set(), "STEM": set()}
    for p, f in forms.items():
        for form, key in f.items():
            groups[form].add(key)
            lookup.setdefault(key, []).append((p, form))
    alts = []
    for form in ("FULL", "SUFFIX", "WIKILINK", "FILENAME", "STEM"):
        for key in sorted(groups[form], key=len, reverse=True):
            if form == "WIKILINK":
                alts.append(r"\[\[" + re.escape(key[2:]) + r"(?=[\]|#])")
            elif form in ("FULL", "SUFFIX"):
                alts.append(_REF_LB + re.escape(key) + _REF_LA)
            else:
                alts.append(_REF_LB + re.escape(key) + _REF_LA + r"(?!/)")
    if not alts:
        return None, lookup
    return re.compile("|".join(alts)), lookup


def reference_survivors(excl_kind, included, out_root, all_paths):
    """Scan every INCLUDED file (as written to out_root) for references to every EXCLUDED path.
    Returns ({excluded_path: [(included_path, line, form, matched_text), ...]}, summary_line,
    {excluded_path: [dropped-form reasons]})."""
    excl_paths = sorted(excl_kind)
    survivors = {p: [] for p in excl_paths}
    forms, dropped = _survivor_forms(excl_paths, all_paths)
    rx, lookup = _survivor_regex(forms)
    if rx is not None:
        for inc_path, _ in included:
            with open(os.path.join(out_root, inc_path.replace("/", os.sep)), "rb") as f:
                data = f.read()
            text = data.decode("utf-8", "replace")
            for ln_no, line in enumerate(text.split("\n"), 1):
                seen = set()
                for m in rx.finditer(line):
                    tok = m.group(0)
                    for ex_path, form in lookup.get(tok, []):
                        if ex_path == inc_path or ex_path in seen:
                            continue
                        seen.add(ex_path)
                        survivors[ex_path].append((inc_path, ln_no, form, tok))
    with_surv = sum(1 for p in excl_paths if survivors[p])
    total_refs = sum(len(v) for v in survivors.values())
    exact = [p for p in excl_paths if excl_kind[p] == "PATH_EXACT"]
    exact_with = sum(1 for p in exact if survivors[p])
    summary = ("REFERENCE-SURVIVORS: %d of %d excluded files have >= 1 inbound reference by name "
               "in an INCLUDED file (%d refs total); PATH_EXACT rows: %d of %d have survivors"
               % (with_surv, len(excl_paths), total_refs, exact_with, len(exact)))
    return survivors, summary, dropped


def survivor_section(excl_kind, survivors, summary, dropped):
    out = ["## REFERENCE-SURVIVORS", "",
           "**" + summary + "**", "",
           "A whole-file EXCLUDE removes the body; the NAME survives wherever an INCLUDED file "
           "referred to it. Nothing below was rewritten -- a reference by name is disclosed here "
           "as a name only. Forms: FULL (repo-relative path), SUFFIX (parent-dir/basename), "
           "FILENAME, WIKILINK (`[[stem]]`), STEM (bare basename). FILENAME is armed only when no "
           "other file at source shares the basename; WIKILINK and STEM only when no other path "
           "shares the stem, and STEM additionally only for slug-shaped stems (a hyphen, underscore "
           "or digit) -- a shared name or a plain word is not a reference to THIS file, and the "
           "`forms dropped` column says so per file. One row per (referring file, line, excluded "
           "file), most specific form wins. `--fail-on-survivors` exits 4 when any PATH_EXACT row "
           "has >= 1 survivor.",
           ""]
    ordered = sorted(excl_kind, key=lambda p: (_EXCL_ORDER[excl_kind[p]], p))
    out += ["| excluded file | exclusion | inbound refs | forms dropped |", "|---|---|---|---|"]
    for p in ordered:
        out.append("| `%s` | %s | %d | %s |" % (p, excl_kind[p], len(survivors[p]),
                                               "; ".join(dropped.get(p, [])) or "none"))
    out.append("")
    for p in ordered:
        refs = survivors[p]
        if not refs:
            continue
        out.append("### `%s` (%s) -- %d inbound ref(s)" % (p, excl_kind[p], len(refs)))
        out.append("")
        for inc_path, ln_no, form, tok in sorted(refs):
            out.append("- `%s:%d` %s `%s`" % (inc_path, ln_no, form, tok.replace("`", "'")))
        out.append("")
    return out


# --- VALUE WALK (lane PUB-2d, Professional's quarantine rule) ---------------------------------

def _lit_keys():
    """Opaque per-run keys for the VALUE_WALK rows: (ordinal id, salted sha256[:8], class).
    Professional's amendment: sha256(literal) is an ORACLE for a low-entropy literal, so the
    digest is over a per-run random salt + literal, and the salt is printed nowhere."""
    salt = os.urandom(16)
    keys = []
    for i, (lit, cls) in enumerate(VALUE_WALK, 1):
        tag = hashlib.sha256(salt + lit.encode("utf-8")).hexdigest()[:8]
        keys.append(("VW-%02d" % i, tag, cls))
    return keys


def value_walk(included, out_root):
    """Fixed-string, case-sensitive walk of every VALUE_WALK literal over every INCLUDED file as
    written to out_root. Returns ({(ordinal, tag, cls): [(included_path, line), ...]},
    summary_line). Nothing here ever holds the literal in an output string."""
    keys = _lit_keys()
    hits = {k: [] for k in keys}
    if VALUE_WALK:
        for inc_path, _ in included:
            with open(os.path.join(out_root, inc_path.replace("/", os.sep)), "rb") as f:
                text = f.read().decode("utf-8", "replace")
            lines = None
            for (lit, cls), key in zip(VALUE_WALK, keys):
                if lit not in text:
                    continue
                if lines is None:
                    lines = text.split("\n")
                for ln_no, line in enumerate(lines, 1):
                    if lit in line:
                        hits[key].append((inc_path, ln_no))
    n_hits = sum(len(v) for v in hits.values())
    n_lit_hit = sum(1 for v in hits.values() if v)
    summary = ("VALUE-WALK: %d literal(s) walked over %d INCLUDED files; %d literal(s) found, "
               "%d hit(s) total" % (len(VALUE_WALK), len(included), n_lit_hit, n_hits))
    return hits, summary


def value_walk_section(hits, summary):
    out = ["## VALUE-WALK", "", "**" + summary + "**", "",
           "Each `VALUE_WALK` literal from `public_exclusions.txt` is walked fixed-string and "
           "case-sensitive over every INCLUDED file. Withholding the file that introduced an "
           "identifier does not withhold the identifier. The literal is never printed here -- a "
           "row carries an opaque ordinal id, sha256[:8] of (per-run random salt + literal) with "
           "the salt printed nowhere (an unsalted digest of a low-entropy literal is an oracle), "
           "and its class -- so this log cannot leak what it guards. Nothing was rewritten. "
           "`--fail-on-value-hits` exits 5 when any hit exists.",
           "", "| id | salted digest[:8] | class | hits |", "|---|---|---|---|"]
    for key in sorted(hits):
        oid, tag, cls = key
        out.append("| %s | `%s` | %s | %d |" % (oid, tag, cls, len(hits[key])))
    out.append("")
    for key in sorted(hits):
        oid, tag, cls = key
        rows = hits[key]
        if not rows:
            continue
        out.append("### %s (%s) -- %d hit(s)" % (oid, cls, len(rows)))
        out.append("")
        for inc_path, ln_no in sorted(rows):
            out.append("- `%s:%d`" % (inc_path, ln_no))
        out.append("")
    return out


# --- SHAPE SCAN (lane PUB-2d, Professional's amendment) --------------------------------------

_HEX_RX = re.compile(r"^[0-9a-fA-F]+$")
_DATE_RX = re.compile(r"\d{4}-\d{2}-\d{2}")


def _shape_token_ok(tok):
    """Filters a shape match down to id-shaped tokens: drop hex-only strings (sha256 prefixes,
    uuids without dashes), tokens lacking any of upper/lower/digit (mixed case plus digit is the
    shape), tokens carrying a date, and hyphenated slugs (3+ hyphen segments, every segment
    lowercase-or-digits)."""
    if _HEX_RX.match(tok):
        return False
    if not (re.search(r"[A-Z]", tok) and re.search(r"[a-z]", tok) and re.search(r"[0-9]", tok)):
        return False
    if _DATE_RX.search(tok):
        return False
    segs = tok.split("-")
    if len(segs) >= 3 and all(re.match(r"^[a-z0-9_]*$", sg) for sg in segs):
        return False
    return True


# Lane PUB-2e (2026-09-02): a SECOND COLUMN, never a filter. Professional read all four of the
# 2026-09-02 SHAPE-SCAN hits (a test-expectation key and three letter-name fragments -- all four
# false positives) and measured a discriminator over the seven tokens in hand (4 false, 3 real
# Google ids): real ids carry 0 or 1 separator (- or _) and NO all-alphabetic separator-delimited
# segment; slugs and letter names carry 4+ separators and an all-alpha segment of 7+ chars.
# Every hit stays in the log; the columns only order them and tell the human reader which rows
# look like slugs. The rule below is deliberately looser than the measured gap on both sides.
SHAPE_SLUG_RULE = ("likely_slug = separators >= 2 OR any separator-delimited segment "
                   "all-alphabetic and >= 5 chars")
SHAPE_SLUG_CAVEAT = ("Rule tuned on seven tokens, three of them real: a sample, not a validation "
                     "(Professional, 2026-09-02).")
_SEP_RX = re.compile(r"[-_]")


def _shape_slug_columns(tok):
    """Returns (likely_slug: 'yes'|'no', separators: int, longest_alpha_segment: int) for one
    shape hit. separators counts every `-` and `_`; longest_alpha_segment is the length of the
    longest separator-delimited segment made only of letters (0 if none). Never stores the
    token."""
    segs = _SEP_RX.split(tok)
    seps = len(segs) - 1
    alpha_lens = [len(sg) for sg in segs if sg and sg.isalpha()]
    longest_alpha = max(alpha_lens) if alpha_lens else 0
    likely = "yes" if (seps >= 2 or longest_alpha >= 5) else "no"
    return likely, seps, longest_alpha


def shape_scan(included, out_root):
    """Detector, not a gate: every SHAPE_SCAN regex over every INCLUDED file, filtered by
    _shape_token_ok. Returns ({name: [(included_path, line, token_len, likely_slug,
    separators, longest_alpha_segment), ...]}, summary_line). The token itself is never stored
    in the output; the three trailing fields are PUB-2e's second column (never a filter)."""
    hits = {name: [] for name, _ in SHAPE_SCAN}
    if SHAPE_SCAN:
        for inc_path, _ in included:
            with open(os.path.join(out_root, inc_path.replace("/", os.sep)), "rb") as f:
                text = f.read().decode("utf-8", "replace")
            for ln_no, line in enumerate(text.split("\n"), 1):
                for name, rx in SHAPE_SCAN:
                    for m in rx.finditer(line):
                        if _shape_token_ok(m.group(0)):
                            likely, seps, longest_alpha = _shape_slug_columns(m.group(0))
                            hits[name].append((inc_path, ln_no, len(m.group(0)),
                                               likely, seps, longest_alpha))
    n = sum(len(v) for v in hits.values())
    summary = ("SHAPE-SCAN: %d shape(s) scanned over %d INCLUDED files; %d token hit(s) "
               "(detector only, no exit code)" % (len(SHAPE_SCAN), len(included), n))
    return hits, summary


def shape_scan_section(hits, summary):
    out = ["## SHAPE-SCAN", "", "**" + summary + "**", "",
           "Each `SHAPE_SCAN <name> <regex>` row is scanned, bounded by non-token characters, over "
           "every INCLUDED file, after dropping hex-only strings, tokens lacking mixed case plus a "
           "digit, tokens carrying a date, and hyphenated slugs. A hit names the shape and the "
           "token's LENGTH only, never the token. This is a detector feeding a human decision; it "
           "sets no exit code. Nothing was rewritten.",
           "",
           "Second column (lane PUB-2e, 2026-09-02; never a filter -- no row is removed): each hit "
           "also carries `likely_slug`, `separators` (count of `-` and `_` in the token) and "
           "`longest_alpha_segment` (length of the longest separator-delimited all-letter "
           "segment, 0 if none). Rule: `" + SHAPE_SLUG_RULE + "`. " + SHAPE_SLUG_CAVEAT + " Rows "
           "are ordered likely_slug=no first, so the tokens most worth a human read come first.",
           "", "| shape | hits | likely_slug=no | likely_slug=yes |", "|---|---|---|---|"]
    for name in sorted(hits):
        n_no = sum(1 for r in hits[name] if r[3] == "no")
        out.append("| %s | %d | %d | %d |" % (name, len(hits[name]), n_no, len(hits[name]) - n_no))
    out.append("")
    for name in sorted(hits):
        rows = hits[name]
        if not rows:
            continue
        out.append("### %s -- %d hit(s)" % (name, len(rows)))
        out.append("")
        # likely_slug=no first (rows[3] == "no" sorts before "yes"), then by path and line.
        for inc_path, ln_no, tlen, likely, seps, longest_alpha in sorted(
                rows, key=lambda r: (r[3] != "no", r[0], r[1])):
            out.append("- `%s:%d` %s len=%d likely_slug=%s separators=%d longest_alpha_segment=%d"
                       % (inc_path, ln_no, name, tlen, likely, seps, longest_alpha))
        out.append("")
    return out


# --- MAIN ------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--src-mode", choices=["git", "fs"], default="git")
    ap.add_argument("--include-spec", default=None,
                    help="key-prefixed include spec (EXACT_INCLUDE / PREFIX_INCLUDE / "
                         "SUFFIX_UNDER <dir> <suffix> / BASENAME_UNDER <dir> <depth> <name>). "
                         "OPTIONAL; omitted means the built-in CFL spec, so CFL runs are "
                         "unchanged. Fail-closed when given: missing, unparseable, or empty "
                         "aborts rather than falling back, because publishing one trunk's tree "
                         "under another trunk's rules is the failure this prevents.")
    ap.add_argument("--src-root")
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-nonempty-out", action="store_true",
                    help="(unsafe) permit an existing non-empty --out; stale files from an earlier "
                         "run are NEVER removed, so a newly excluded file stays on disk")
    ap.add_argument("--scope-note",
                    help="text file inserted VERBATIM as a `## SCOPE` block at the top of "
                         "DERIVATION-LOG.md (denominator, files still UNKNOWN to semantic reading, "
                         "pending items) so a qualified grade travels with the tree; abort if empty")
    ap.add_argument("--controls-dir",
                    help="write MANIFEST.sha256 and DERIVATION-LOG.md to this sibling directory "
                         "instead of inside the tree, so the manifest covers the WHOLE tree and "
                         "the log is not a derived file describing itself; must be fresh/empty "
                         "and distinct from --out (default: unchanged, in-tree)")
    ap.add_argument("--fail-on-value-hits", action="store_true",
                    help="exit 5 when any VALUE_WALK literal from the exclusion list occurs in any "
                         "INCLUDED file (see VALUE-WALK in DERIVATION-LOG.md); takes precedence "
                         "over exit 4 because a value hit is content, not a name")
    ap.add_argument("--fail-on-survivors", action="store_true",
                    help="exit 4 when any PATH_EXACT-excluded file present at source has >= 1 "
                         "inbound reference surviving by NAME in an INCLUDED file (see "
                         "REFERENCE-SURVIVORS in DERIVATION-LOG.md); the tree and log are still "
                         "written first")
    a = ap.parse_args()
    # Wire the include spec BEFORE anything walks paths. A flag that is parsed and
    # never consumed is the defect this file exists to prevent, one layer up.
    if a.include_spec:
        _sp = load_include_spec(a.include_spec)
        print('[derive] include-spec=%s (exact=%d prefix=%d suffix=%d basename=%d)'
              % (a.include_spec, len(_sp['EXACT_INCLUDE']), len(_sp['PREFIX_INCLUDE'],)
                 , len(_sp['SUFFIX_UNDER']), len(_sp['BASENAME_UNDER'])))
    else:
        print('[derive] include-spec=BUILT-IN (CFL shape)')
    if os.path.isdir(a.out) and os.listdir(a.out) and not a.allow_nonempty_out:
        # 2026-09-02: 8 semantically WITHHELD files survived a re-derive because the
        # deriver only ever adds. A non-empty --out is UNKNOWN, never a clean tree.
        raise SystemExit('ABORT [fail-closed]: --out %r exists and is non-empty; derive into a fresh directory' % a.out)
    scope_text = None
    if a.scope_note is not None:
        if not os.path.isfile(a.scope_note):
            raise SystemExit("ABORT [fail-closed]: --scope-note %r does not exist" % a.scope_note)
        with open(a.scope_note, encoding="utf-8") as f:
            scope_text = f.read()
        if not scope_text.strip():
            raise SystemExit("ABORT [fail-closed]: --scope-note %r is empty; a scope block that "
                             "says nothing grades nothing" % a.scope_note)
    controls_root = None
    if a.controls_dir is not None:
        controls_root = a.controls_dir
        if os.path.abspath(controls_root) == os.path.abspath(a.out):
            raise SystemExit("ABORT: --controls-dir must differ from --out")
        if os.path.isdir(controls_root) and os.listdir(controls_root) and not a.allow_nonempty_out:
            raise SystemExit('ABORT [fail-closed]: --controls-dir %r exists and is non-empty' % controls_root)

    gaz = depii_lexicon.load_gazetteer()
    gaz_armed = bool(gaz)

    # PIN THE SOURCE. "HEAD" is not a source: the seat commits into this clone while lanes run,
    # and a log that records the word HEAD cannot be checked afterwards against anything. Found
    # the hard way on 2026-09-02 -- HEAD moved between this lane's dry run and its real run.
    resolved = None
    if a.src_mode == "git":
        resolved = subprocess.run(["git", "rev-parse", a.ref], cwd=a.repo,
                                  capture_output=True, check=True).stdout.decode().strip()
        all_paths = git_paths(a.repo, resolved)
    else:
        all_paths = fs_paths(a.src_root)
    src_desc = ("%s @ %s (ref %s resolved at run time)" % (a.repo or os.getcwd(), resolved, a.ref)
                if resolved else "fs %s" % a.src_root)

    cand = [p for p in all_paths if considered(p) and not p.startswith(DENY_PREFIX) and p not in DENY_EXACT]
    skipped_not_considered = len(all_paths) - len(cand)

    if a.src_mode == "git":
        blobs = git_read_many(a.repo, resolved, cand)
    else:
        blobs = {}
        for p in cand:
            with open(os.path.join(a.src_root, p.replace("/", os.sep)), "rb") as f:
                blobs[p] = f.read()

    out_root = a.out
    os.makedirs(out_root, exist_ok=True)

    included, excluded = [], []      # excluded rows: (path, class, line, detail)
    reported_rows = []               # REPORT-ONLY rows: named, logged, and NOT withheld
    for p in cand:
        data = blobs.get(p)
        if data is None:
            excluded.append((p, "SOURCE-UNREADABLE", 0, "no blob at %s" % (resolved or a.src_root)))
            continue
        if len(data) == 0:
            excluded.append((p, "EMPTY-SOURCE", 0, "0 bytes at source"))
            continue
        hits = path_exclusions(p, gaz)
        reported = []
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            hits.append(("BINARY-OR-UNDECODABLE", 0, "not valid utf-8"))
            text = None
        if text is not None:
            fm = parse_frontmatter(text) if p.endswith(".md") else {}
            for _row in frontmatter_exclusions(p, fm):
                (reported if _row[0] in REPORT_ONLY_CLASSES else hits).append(_row)
            hits += content_exclusions(text, gaz)
        for _cls, _ln, _detail in reported:
            reported_rows.append((p, _cls, _ln, _detail))
        if hits:
            for cls, ln, detail in hits:
                excluded.append((p, cls, ln, detail))
            continue
        dest = os.path.join(out_root, p.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        included.append((p, len(data)))
    # PATH_EXACT rows are pre-filtered out of `cand`, so until 2026-09-02 (Professional's v3
    # verification) they reached neither the classifier nor the log: 4 withheld files had 0 rows.
    # Log each one present at source with its class and the row's comment (the WITHHOLD basis).
    for p in all_paths:
        if p in DENY_EXACT:
            excluded.append((p, "PATH-DENY-EXACT", 0,
                             EX_COMMENTS.get(("PATH_EXACT", p), "PATH_EXACT row (no comment)")))

    # --- DERIVATION-LOG.md --------------------------------------------------------------------
    by_class = {}
    for p, cls, ln, detail in excluded:
        by_class.setdefault(cls, set()).add(p)
    excluded_paths = sorted(set(p for p, _, _, _ in excluded))

    log = []
    if scope_text is not None:
        log += ["## SCOPE", "", scope_text.rstrip("\n"), "", "---", ""]
    log += [
        "# DERIVATION-LOG -- public-safe derived tree",
        "",
        "Produced by `scripts/audit/derive_public_tree.py` (lane PUB-1).",
        "",
        "Source: %s" % src_desc,
        "",
        "**Two dispositions only: INCLUDE byte-identical, or EXCLUDE whole-file. No file's "
        "content was rewritten, and nothing in the source tree was modified.**",
        "",
        "## Exclusion set",
        "",
        "- Read from `scripts/audit/public_exclusions.txt` (sha256 `%s`), never inferred from "
        "repo prose." % _exclusions_sha(),
        "- DIR_NAME entries: %s | CONTENT_CLASS entries: %d | PATH_PREFIX entries: %d"
        % (", ".join(sorted(DENY_DIR_NAMES)), len(CONTENT_CLASSES), len(DENY_PREFIX)),
        "",
        "## Gazetteer arming",
        "",
        ("- ARMED: %d gazetteer entries loaded (entries themselves are never printed)."
         % len(gaz)) if gaz_armed else
        "- **NOT ARMED -- no gazetteer file. NAME coverage for the file-listed (family / "
        "third-party) class is UNKNOWN, not zero: the scanner looked for no names, so it found "
        "none. This is an unarmed scan, and UNKNOWN never rounds to PASS.**",
        "",
        "## Counts",
        "",
        "| quantity | n |",
        "|---|---|",
        "| paths at source | %d |" % len(all_paths),
        "| not in the include spec (never considered) | %d |" % skipped_not_considered,
        "| considered | %d |" % len(cand),
        "| INCLUDED | %d |" % len(included),
        "| EXCLUDED (distinct files) | %d |" % len(excluded_paths),
        "| exclusion hits (a file may carry several) | %d |" % len(excluded),
        "",
        "## Exclusions by class",
        "",
        "| class | files |",
        "|---|---|",
    ]
    for cls in sorted(by_class):
        log.append("| %s | %d |" % (cls, len(by_class[cls])))
    log += ["", "## Every exclusion (path, class, line, detail)", "",
            "| path | class | line | detail |", "|---|---|---|---|"]
    for p, cls, ln, detail in sorted(excluded):
        d = (detail or "").replace("|", "\\|").replace("\n", " ")
        if len(d) > 120:
            d = d[:117] + "..."
        log.append("| `%s` | %s | %s | %s |" % (p, cls, ln, d))
    log.append("")

    # --- REPORT-ONLY ROWS: named, logged, NOT withheld ----------------------------------------
    # A report nobody can read is the same defect as no report. These rows do not cut a file, so
    # they would otherwise vanish -- and the whole point of the class is that a reader disposes of
    # them instead of discovering a cut months later.
    log += ["## REPORT-ONLY (nothing was withheld for these)", "",
            "**%d row(s).** These classes are REPORTED and never cut. `FM-HELD-PROSE` exists because "
            "T5 (Professional, 2026-09-13) found `HELD_VAL_RX` matching `held` inside a value's PROSE "
            "and withholding a LIVE page for a sentence about being held to a standard. `FM_HELD_KEY` "
            "includes `visibility` and `FM_HELD_VALUE` includes `held`/`personal`/`private`, all "
            "ordinary English, so any narrative value under a common key tripped it. **A page is "
            "withheld for a DECLARATION, not for a sentence** -- and the match was not loosened, "
            "because failing open is the dangerous direction on a public surface." % len(reported_rows),
            "", "| path | class | line | detail |", "|---|---|---|---|"]
    for p_, cls, ln, detail in sorted(reported_rows):
        d = (detail or "").replace("|", chr(92) + "|").replace(chr(10), " ")
        if len(d) > 160:
            d = d[:157] + "..."
        log.append("| `%s` | %s | %s | %s |" % (p_, cls, ln, d))
    if not reported_rows:
        log.append("| *(none)* | | | |")
    log.append("")

    # --- REFERENCE-SURVIVORS (lane PUB-2d) ----------------------------------------------------
    excl_kind = {}
    for p in all_paths:
        if p in DENY_EXACT:
            excl_kind[p] = "PATH_EXACT"
        elif considered(p) and p.startswith(DENY_PREFIX):
            excl_kind[p] = "PATH_PREFIX"
    for p in excluded_paths:
        excl_kind.setdefault(p, "SCAN")
    survivors, surv_summary, surv_dropped = reference_survivors(excl_kind, included, out_root, all_paths)
    log += survivor_section(excl_kind, survivors, surv_summary, surv_dropped)
    value_hits, value_summary = value_walk(included, out_root)
    log += value_walk_section(value_hits, value_summary)
    shape_hits, shape_summary = shape_scan(included, out_root)
    log += shape_scan_section(shape_hits, shape_summary)
    ctl_root = controls_root or out_root
    os.makedirs(ctl_root, exist_ok=True)
    log_path = os.path.join(ctl_root, "DERIVATION-LOG.md")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log))

    # --- MANIFEST.sha256 (WRITTEN LAST) -------------------------------------------------------
    # Per Professional 2026-09-02: the derived tree is verified by HASH, never by file count.
    # One line per file: sha256, bytes, relative path. MANIFEST.sha256 itself is the ONLY file
    # not listed (it cannot contain its own hash); everything else, DERIVATION-LOG.md included,
    # must appear -- that is exactly what leak_control.py asserts, together with bytes > 0
    # (this morning a `cp -r` produced 1,068 zero-byte shells with correct names).
    man_lines, total_bytes = [], 0
    for rel in fs_paths(out_root):
        if rel == "MANIFEST.sha256":
            continue
        with open(os.path.join(out_root, rel.replace("/", os.sep)), "rb") as f:
            b = f.read()
        total_bytes += len(b)
        man_lines.append("%s  %d  %s" % (hashlib.sha256(b).hexdigest(), len(b), rel))
    # With --controls-dir the tree holds neither file, so the manifest covers the WHOLE tree
    # (line count == file count) and the log describes a tree it is not part of.
    man_path = os.path.join(ctl_root, "MANIFEST.sha256")
    with open(man_path, "w", encoding="utf-8") as f:
        f.write("\n".join(man_lines) + "\n")
    print("[derive] log=%s manifest=%s (%d rows)" % (log_path, man_path, len(man_lines)))

    print("[derive] considered=%d included=%d excluded_files=%d exclusion_hits=%d bytes=%d "
          "gazetteer=%s"
          % (len(cand), len(included), len(excluded_paths), len(excluded), total_bytes,
             ("ARMED(%d)" % len(gaz)) if gaz_armed else "NOT-ARMED-NAME-COVERAGE-ZERO"))
    print("[derive] " + surv_summary)
    print("[derive] " + value_summary)
    print("[derive] " + shape_summary)
    if a.fail_on_value_hits:
        n_hits = sum(len(v) for v in value_hits.values())
        if n_hits:
            print("[derive] FAIL --fail-on-value-hits: %d hit(s) of %d VALUE_WALK literal(s) in "
                  "INCLUDED files (see VALUE-WALK section; literals are never printed)"
                  % (n_hits, sum(1 for v in value_hits.values() if v)))
            return 5
    if a.fail_on_survivors:
        hit = sorted(p for p, kind in excl_kind.items() if kind == "PATH_EXACT" and survivors.get(p))
        if hit:
            print("[derive] FAIL --fail-on-survivors: %d PATH_EXACT file(s) referenced by name from "
                  "INCLUDED files: %s" % (len(hit), ", ".join(hit)))
            return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
