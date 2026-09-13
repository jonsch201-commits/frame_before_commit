#!/usr/bin/env python3
"""v4.0 conformance linter + ledger generator (deterministic — no models).

Grades every source page against the presence-expressible v4.0 checks. Where the raw
is available it also runs the DETERMINISTIC anchor-range check enabled by the
turn-indexer: any turn anchor Tn with n > the raw's verified turn count is a
provably-broken citation (calibration finding F3; e.g. dba2c0b cited T570 in a
557-turn source). Correctness of IN-RANGE anchors is not decidable here — see
`scripts/lint_citation_coverage.py`, whose sampled arm found that ~40% of in-range
anchors do not actually support their claim while this file's checks read 96.7%.

WHAT CHANGED 2026-07-26, and why the old numbers were wrong
-----------------------------------------------------------
`source-page-standard-v4.md` grades a page conformant when every applicable check is
"PASS / `unrecoverable` / `N/A-by-kind` / `N/A-blocked`". **None of those three
non-FAIL grades existed in any implementation.** This file had booleans and
`conformant = all(C.values())`, so:

  1. **E7m required `reads_manifest` on EVERY page.** The standard (v4:60-61) says
     `reads_manifest` "when one exists" — conditional. Every page without a subagent
     read-manifest was scored non-conformant. This was the single largest contributor
     to near-universal non-conformance: a scoring artifact, not a wiki defect.
  2. **A `reference` page with no turn anchors graded FAIL**, where v4:41 says the
     turn-anchor is `N/A-by-kind` for that kind. Reference pages could not pass, ever.
  3. **The FORM cascade was unimplemented.** v4:36-37: a session page missing
     `## Key Claims` grades the claim-dependent checks `N/A-blocked`, NOT FAIL.
  4. **The version was thrown away.** `state.split("@")[0]` collapsed
     `verified@{v3.0,...}` and `verified@{v4.0,...}` to the same `verified`, defeating
     the G3 authority rule the field exists to serve — the one page verified at v3.0
     was indistinguishable from those at v4.0. The tool hid the exact case the rule
     was written to catch.

Also fixed: **the ledger is no longer written by default.** Running a measurement used
to mutate a tracked wiki page as a side effect, which is why it could not be run
routinely. `--write-ledger` is now opt-in; the default is stdout-only.

Run from repo root (worktree ok). Reads raws from the MAIN checkout via --main-root
(raws are gitignored, so a worktree does not have them).
"""
import hashlib, os, re, glob, argparse, sys
import turn_index  # same dir

sys.stdout.reconfigure(encoding="utf-8")  # grade glyphs are non-cp1252

WIKI = "wiki"
TRUNKS = {"wiki/sources": "fl", "wiki/personal/sources": "personal",
          "wiki/home/sources": "home", "wiki/pro/sources": "pro"}

# The standard version a page must declare to hold undemoted authority (G3).
# Bump with the standard. Kept explicit so "verified@current" is computable rather
# than assumed — the whole point of preserving the version.
CURRENT_STANDARD = "v4.0"

# Grades. Conformance accepts anything that is not FAIL.
PASS, FAIL, NA_KIND, NA_BLOCKED, UNRECOVERABLE = "PASS", "FAIL", "N/A-kind", "N/A-blocked", "unrecov"
NON_FAIL = {PASS, NA_KIND, NA_BLOCKED, UNRECOVERABLE}


def trunk_of(p):
    p = p.replace("\\", "/")
    for pre, n in TRUNKS.items():
        if p.startswith(pre): return n
    return "other"


def parse(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    fm, body = {}, text
    if text.startswith("---"):
        e = text.find("\n---", 3)
        if e != -1:
            for line in text[3:e].splitlines():
                m = re.match(r"^([a-z_0-9]+):\s*(.*)$", line.strip())
                if m: fm[m.group(1)] = m.group(2).strip()
            body = text[e+4:]
    return fm, body, text


def kind_of(fm, body, slug, path):
    if fm.get("source_kind"): return fm["source_kind"]
    if "concepts/" in path or "analyses/" in path or not re.search(r"\d{4}-\d{2}-\d{2}-[a-f0-9]{6}", slug):
        return "candidate-analysis"
    if "## Key Claims" in body and "## Summary" in body: return "session"
    if re.search(r"^##\s*(Product|Warranty|Ticket|Spec|Model|Intake|Photos|Action Items)", body, re.M):
        return "reference"
    return "session?"


def audit_state_of(fm):
    """Return (stage, version, display). The VERSION IS PRESERVED — that is the point.

    `audit_state: verified@{v4.0, 2026-07-13, sha256:...}` -> ("verified", "v4.0", ...)
    A page verified at a superseded standard is `verified@stale`, which under G3 has
    demoted authority exactly like an unverified page. Collapsing it to "verified"
    (the prior behaviour) reported it as current.
    """
    raw = fm.get("audit_state", "unaudited").strip()
    stage = raw.split("@")[0].split("{")[0].strip() or "unaudited"
    m = re.search(r"v\d+\.\d+", raw)
    version = m.group(0) if m else ""
    if stage != "verified":
        return stage, version, stage
    if not version:
        return stage, "", "verified@unversioned"
    return stage, version, ("verified@current" if version == CURRENT_STANDARD
                            else f"verified@stale({version})")


def grade(path, fm, body, text, kind, main_root):
    """Grade one page. Every check returns a grade, never a bare boolean."""
    is_session = "session" in kind
    is_reference = "reference" in kind
    is_analysis = "analysis" in kind

    # --- FORM, and the cascade it triggers (v4:36-37) ---
    if is_session:
        e1 = PASS if all(f"## {s}" in body for s in ("Summary", "Key Claims", "Conflicts")) else FAIL
    else:
        # reference: identity heading + domain sections. analysis: thesis + claims + links.
        # Previously `("reference" in kind or "analysis" in kind)` — a tautology that
        # graded every non-session page PASS without inspecting it.
        if is_reference:
            e1 = PASS if re.search(r"^##\s+\S", body, re.M) else FAIL
        else:
            e1 = PASS if (re.search(r"^##\s+\S", body, re.M) and re.search(r"\[\[[^\]]+\]\]", text)) else FAIL
    # A session page with no ## Key Claims cannot be graded on its claims.
    claims_blocked = is_session and "## Key Claims" not in body

    def claim_check(fn):
        return NA_BLOCKED if claims_blocked else (PASS if fn() else FAIL)

    has_turn_anchor = bool(re.search(r":T\d+", text))
    has_wikilink = bool(re.search(r"\[\[[^\]]+\]\]", text))
    has_src_cite = bool(re.search(r"`[^`]+\.(?:md|py|sh|json|ya?ml)[^`]*`|https?://", text))

    # --- E2 anchor, parameterized per kind (v4:40-45) ---
    if is_session:
        e2 = claim_check(lambda: has_turn_anchor)
    elif is_reference:
        # v4:41 — "reference: source-citation; turn-anchor N/A-by-kind"
        e2 = PASS if has_src_cite else NA_KIND
    else:
        e2 = PASS if (has_wikilink or "[inferred]" in text) else FAIL

    e3 = claim_check(lambda: bool(re.search(
        r"\[(verbatim|paraphrase|reconstructed|contextual|inferred|uncaptured)\]", text)))
    e5 = claim_check(lambda: has_wikilink)

    # --- E8 fixity: only meaningful when the page HAS a raw ---
    sf = fm.get("source_file", "")
    has_raw = bool(sf) and sf.lower() not in ("none", "n/a", "")
    if not has_raw:
        e8 = NA_KIND                      # analysis kind expects `source_file: none`
    elif "unrecoverable" in text.lower():
        e8 = UNRECOVERABLE                # documented loss is a first-class grade, not a FAIL
    else:
        # E8 USED TO CHECK THAT A HASH WAS WRITTEN DOWN. It now checks that the hash is TRUE.
        #
        # Found 2026-07-27: this module contained no `hashlib` at all. E8 asserted the *string*
        # `raw_sha256:` appeared in the page, so a stale hash, a wrong hash, or an invented hash
        # passed exactly like a correct one. That is the record-a-derivable-fact defect this repo
        # has fixed four times elsewhere — the skills digest, the index headers, the intake
        # backlog, the coverage registers — and never here, in the check whose entire job is
        # fixity.
        #
        # A declared hash nobody recomputes is not fixity. It is a comment shaped like a hash.
        declared = fm.get("raw_sha256", "")
        if not (declared and "raw_length:" in text):
            e8 = FAIL
        else:
            raw_path = os.path.join(main_root, sf) if main_root else sf
            try:
                actual = hashlib.sha256(open(raw_path, "rb").read()).hexdigest()
                # Mismatch is a distinct outcome from absence: the page names a source it no
                # longer matches, which is worse than naming none, because it reads as verified.
                e8 = PASS if actual == declared.strip() else FAIL
            except OSError:
                # Raw not reachable from here (gitignored corpus absent, or path moved). NOT a
                # page defect and NOT a pass — an unverifiable claim, graded as its own thing so
                # a missing corpus can never be mistaken for a clean bill of health.
                e8 = UNRECOVERABLE

    # --- E7m reads-manifest: CONDITIONAL (v4:60-61 "when one exists") ---
    # Required only where a subagent contributed; otherwise there is no manifest to
    # declare. Requiring it universally was the largest false-nonconformance source.
    if "extraction_by:" in text:
        e7m = PASS if "reads_manifest:" in text else FAIL
    else:
        e7m = NA_KIND

    return {
        "E1k_kind":    PASS if fm.get("source_kind") else FAIL,
        "E1_form":     e1,
        "E2_anchor":   e2,
        "E3_fidelity": e3,
        "E4_uncap":    PASS if "uncaptured_assessed:" in text else (NA_KIND if not has_raw else FAIL),
        "E5_link":     e5,
        "E6_find":     PASS if ("retrieval_key:" in text and text.count("aliases:") >= 1) else FAIL,
        "E7_prov":     PASS if "generated_by:" in text else FAIL,
        "E7m_reads":   e7m,
        "E8_fixity":   e8,
    }


CHECKS = ["E1k_kind", "E1_form", "E2_anchor", "E3_fidelity", "E4_uncap",
          "E5_link", "E6_find", "E7_prov", "E7m_reads", "E8_fixity"]
GLYPH = {PASS: "✓", FAIL: "·", NA_KIND: "—", NA_BLOCKED: "▨", UNRECOVERABLE: "!"}


# ============================================================================================
# W-6 (2026-09-02): kind-aware extension — patterns/entities/concepts/references/purpose.
#
# Everything above this line (kind_of, grade, the default page-collection glob, CHECKS, GLYPH)
# is UNTOUCHED. That is deliberate: /sources/ pages must keep their exact prior verdicts, and the
# safest way to guarantee that is to never edit the code path that produces them. --all-kinds
# routes /sources/ pages through the SAME kind_of()/grade() calls as before and routes every other
# collected page through the NEW functions below. scripts/audit/selftest_lint_kinds.py's
# regression fixture proves the untouched claim empirically (0 diffs vs `git show HEAD:...`).
# ============================================================================================

ALL_KIND_ROOTS = [("wiki/concepts", "concept"), ("wiki/entities", "entity"),
                   ("wiki/patterns", "pattern"), ("wiki/references", "reference")]

CHECKS_NEW = ["E1k_kind", "E1_form", "E2_anchor", "E3_fidelity", "E4_uncap",
              "E5_link", "E6_find", "E7_prov", "E8_fixity", "E9_backref", "E10_probe"]

# E3's fidelity-tag regex, widened here only: a qualifier after a comma — `[verbatim, cropped]` —
# does not match the ORIGINAL regex in grade() above (W-1 finding, on a patterns page). Scoping
# the widened regex to the new-kind path keeps grade() above byte-for-byte the same, so this
# cannot move any /sources/ verdict.
FIDELITY_RE_V2 = re.compile(
    r"\[(verbatim|paraphrase|reconstructed|contextual|inferred|uncaptured)"
    r"(?:\s*,\s*[a-zA-Z0-9_\- ]+)*\]")


def build_slug_index():
    """slug -> path for every wiki/**/*.md page. Used to resolve [[slug]] links for E9_backref
    (entity: >=2 resolving links; purpose: motivating_pattern resolves to a real pattern page)."""
    idx = {}
    for p in glob.glob(f"{WIKI}/**/*.md", recursive=True):
        p = p.replace("\\", "/")
        idx.setdefault(os.path.basename(p)[:-3], p)
    return idx


def collect_pages(all_kinds):
    """Return (sorted page list, {path: kind_bucket}).

    kind_bucket 'source' pages are always the same set the ORIGINAL glob would have found
    ("/sources/" in path) and are always graded by the untouched kind_of()/grade() pair above,
    with or without --all-kinds. --all-kinds only ADDS pages under concepts/entities/patterns/
    references and skills/*/PURPOSE.md — it never changes which pages are treated as 'source'.
    """
    src = sorted(p.replace("\\", "/") for p in glob.glob(f"{WIKI}/**/*.md", recursive=True)
                 if "/sources/" in p.replace("\\", "/"))
    kindmap = {p: "source" for p in src}
    if not all_kinds:
        return src, kindmap
    extra = []
    for root, label in ALL_KIND_ROOTS:
        for p in glob.glob(f"{root}/**/*.md", recursive=True):
            p = p.replace("\\", "/")
            if p in kindmap:
                continue
            kindmap[p] = label
            extra.append(p)
    for p in glob.glob("skills/*/PURPOSE.md"):
        p = p.replace("\\", "/")
        if p in kindmap:
            continue
        kindmap[p] = "purpose"
        extra.append(p)
    pages = sorted(set(src) | set(extra))
    return pages, kindmap


def effective_kind(fm, default_label):
    """Frontmatter `kind:` wins when present (e.g. `pattern-index` is exempt from the pattern
    contract's E9_backref even though it lives under wiki/patterns/); else the directory label."""
    k = fm.get("kind", "").strip()
    return k if k else default_label


def _section(text, heading):
    m = re.search(re.escape(heading) + r"\n(.*?)(\n## |\Z)", text, re.S)
    return m.group(1) if m else ""


def _struggle_locators(text):
    """Count '## Struggle' bullets carrying a backtick `path:line` locator whose path resolves
    on disk (repo-relative, checked from cwd — this lane runs from repo root, per its brief)."""
    sec = _section(text, "## Struggle")
    n = 0
    for line in sec.splitlines():
        if not line.startswith("- "):
            continue
        m = re.search(r"`([^`\s]+):(\d+)", line)
        if m and os.path.isfile(m.group(1)):
            n += 1
    return n


def _motivates_ok(text):
    sec = _section(text, "## Motivates")
    if "none yet" in sec.lower():
        return True
    m = re.search(r"\[SKILL:\s*([A-Za-z0-9_\-]+)\]", sec)
    return bool(m) and os.path.isfile(f"skills/{m.group(1)}/SKILL.md")


def _entity_link_count(text, slug_index):
    return sum(1 for m in re.finditer(r"\[\[([^\]|]+)\]\]", text)
               if m.group(1).strip() in slug_index)


def _purpose_backref_ok(fm, slug_index):
    mp = fm.get("motivating_pattern", "").strip()
    if mp == "UNKNOWN":
        return True
    m = re.match(r"^\[\[([^\]]+)\]\]$", mp)
    if not m:
        return False
    slug = m.group(1).strip()
    return slug_index.get(slug, "").replace("\\", "/").startswith("wiki/patterns/")


def grade_e9(kind_label, fm, text, slug_index):
    """E9_backref: kind-specific structural back-reference check (new 2026-09-02).

    pattern: >=2 resolving evidence locators in ## Struggle, AND ## Motivates names an existing
             `[SKILL: name]` or reads the literal 'none yet'.
    purpose: `motivating_pattern:` is `[[slug]]` resolving to wiki/patterns/<slug>.md, or exactly
             the literal UNKNOWN.
    entity:  >=2 `[[slug]]` links anywhere on the page that resolve to a real wiki page.
    anything else (concept, reference, pattern-index, ...): not applicable.
    """
    if kind_label == "pattern":
        return PASS if (_struggle_locators(text) >= 2 and _motivates_ok(text)) else FAIL
    if kind_label == "purpose":
        return PASS if _purpose_backref_ok(fm, slug_index) else FAIL
    if kind_label == "entity":
        return PASS if _entity_link_count(text, slug_index) >= 2 else FAIL
    return NA_KIND


def grade_e10(fm, text):
    """E10_probe: any page created 2026-09-02 or later must carry `probe_sealed:` in the sealed
    "<question> => <class>" form (a quoted string containing '=>'), not a bare boolean or absent
    field. Pages with no parseable `date:`, or dated before 2026-09-02, are N/A (can't be graded
    on a cutoff we can't place them against — NOT rounded to PASS)."""
    date_s = fm.get("date", "").strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_s) or date_s < "2026-09-02":
        return NA_KIND
    m = re.search(r'probe_sealed:\s*"([^"]*)"', text)
    return PASS if (m and "=>" in m.group(1)) else FAIL


def grade_new_kind(fm, body, text, kind_label, main_root, slug_index):
    """Grade one non-'source' page. Contract (W-6 brief): E1k/E1/E5/E6/E7 apply to EVERY kind;
    E2/E3/E4/E8 apply only when `source_file` is set and not none/n/a (else N/A-kind — identical
    has_raw gating to the session-kind path above); plus the two new checks."""
    has_wikilink = bool(re.search(r"\[\[[^\]]+\]\]", text))
    sf = fm.get("source_file", "")
    has_raw = bool(sf) and sf.lower() not in ("none", "n/a", "")

    e1 = PASS if re.search(r"^##\s+\S", body, re.M) else FAIL

    if not has_raw:
        e2 = e3 = e4 = e8 = NA_KIND
    else:
        e2 = PASS if bool(re.search(r":T\d+", text)) else FAIL
        e3 = PASS if FIDELITY_RE_V2.search(text) else FAIL
        e4 = PASS if "uncaptured_assessed:" in text else FAIL
        declared = fm.get("raw_sha256", "")
        if not (declared and "raw_length:" in text):
            e8 = FAIL
        else:
            raw_path = os.path.join(main_root, sf) if main_root else sf
            try:
                actual = hashlib.sha256(open(raw_path, "rb").read()).hexdigest()
                e8 = PASS if actual == declared.strip() else FAIL
            except OSError:
                e8 = UNRECOVERABLE

    return {
        "E1k_kind":   PASS if fm.get("source_kind") else FAIL,
        "E1_form":    e1,
        "E2_anchor":  e2,
        "E3_fidelity": e3,
        "E4_uncap":   e4,
        "E5_link":    PASS if has_wikilink else FAIL,
        "E6_find":    PASS if ("retrieval_key:" in text and text.count("aliases:") >= 1) else FAIL,
        "E7_prov":    PASS if "generated_by:" in text else FAIL,
        "E8_fixity":  e8,
        "E9_backref": grade_e9(kind_label, fm, text, slug_index),
        "E10_probe":  grade_e10(fm, text),
    }


def display_status(C):
    """3-way per-page status for the --all-kinds report only (does not touch `conformant`, which
    keeps its existing non-FAIL-is-conformant meaning for --write-ledger etc.). UNRECOVERABLE
    never rounds to PASS/CONFORMANT here — it gets its own NA bucket, distinguishable from a page
    that is genuinely clean."""
    vals = list(C.values())
    if FAIL in vals:
        return "FAIL"
    if UNRECOVERABLE in vals:
        return "NA"
    return "CONFORMANT"


def main():
    ap = argparse.ArgumentParser()
    # ⛔ WAS a hardcoded G: tree path — R4b / the G30 shape, a stale tree as a DEFAULT. Same line as
    # census.py:68, and both were flagged the same afternoon by two independent instruments.
    # ⭐ DERIVED from this file's own location; cannot name a tree the caller is not in.
    ap.add_argument("--main-root",
                    default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    ap.add_argument("--write-ledger", action="store_true",
                    help="regenerate wiki/references/audit-conformance-ledger.md. OFF by default: "
                         "measuring must not mutate what it measures.")
    ap.add_argument("--explain", metavar="SLUG", help="show every grade for one page, with reasons")
    ap.add_argument("--all-kinds", action="store_true",
                    help="also grade wiki/concepts, wiki/entities, wiki/patterns, wiki/references, "
                         "and skills/*/PURPOSE.md, under the kind-aware contract (W-6, 2026-09-02). "
                         "OFF by default so every prior caller's page set is unchanged.")
    args = ap.parse_args()

    pages, kindmap = collect_pages(args.all_kinds)
    slug_index = build_slug_index() if args.all_kinds else {}
    rows, broken_anchor_pages = [], []
    for path in pages:
        fm, body, text = parse(path)
        # skills/<name>/PURPOSE.md all share the literal basename "PURPOSE" — use the skill
        # directory name as the slug instead, or --explain/--all-kinds output could never tell
        # 42 different purpose pages apart.
        slug = (os.path.basename(os.path.dirname(path)) if kindmap[path] == "purpose"
                else os.path.basename(path)[:-3])

        if kindmap[path] == "source":
            # UNTOUCHED path: identical to the pre-W-6 behavior, whether or not --all-kinds is set.
            kind = kind_of(fm, body, slug, path)
            C = grade(path, fm, body, text, kind, args.main_root)

            sf = fm.get("source_file", ""); anchor_range = NA_KIND; oor = []
            raw_abs = os.path.join(args.main_root, sf) if sf and sf.lower() != "none" else None
            anchors = sorted(set(int(n) for n in re.findall(r":T(\d+)", text)))
            if anchors and raw_abs and os.path.isfile(raw_abs):
                try:
                    count = turn_index.index(raw_abs)["turn_count"]
                    oor = [n for n in anchors if n > count]
                    anchor_range = FAIL if oor else PASS
                    if oor: broken_anchor_pages.append((slug, count, oor))
                except Exception:
                    anchor_range = "ERR"
            stage, version, state_display = audit_state_of(fm)
            conformant = all(v in NON_FAIL for v in C.values()) and anchor_range in NON_FAIL
            rows.append(dict(slug=slug, path=path, kind_bucket="source", trunk=trunk_of(path),
                             kind=kind, stage=stage, version=version, state=state_display,
                             anchor_range=anchor_range, oor=oor, conformant=conformant, C=C))
        else:
            kind_label = effective_kind(fm, kindmap[path])
            C = grade_new_kind(fm, body, text, kind_label, args.main_root, slug_index)
            stage, version, state_display = audit_state_of(fm)
            conformant = all(v in NON_FAIL for v in C.values())
            rows.append(dict(slug=slug, path=path, kind_bucket=kindmap[path], trunk=trunk_of(path),
                             kind=kind_label, stage=stage, version=version, state=state_display,
                             anchor_range=NA_KIND, oor=[], conformant=conformant, C=C))

    if args.explain:
        matched = [r for r in rows if args.explain in r["slug"]]
        if matched:
            for r in matched:
                checks = CHECKS if r["kind_bucket"] == "source" else CHECKS_NEW
                print(f"\n{r['slug']}\n  kind={r['kind']}  trunk={r['trunk']}  audit_state={r['state']}")
                for c in checks:
                    print(f"    {c:14} {r['C'][c]}")
                if r["kind_bucket"] == "source":
                    print(f"    {'anchor_range':14} {r['anchor_range']}"
                          + (f"  out-of-range={r['oor']}" if r["oor"] else ""))
                print(f"  CONFORMANT: {r['conformant']}")
            return
        # Nothing in the collected set matched — the old behavior here was SILENCE (W-1's finding:
        # `--explain <slug>` for a patterns page printed nothing, not even N/A). Look wider than
        # the collected set so a real page always gets a verdict line, never silence.
        candidates = []
        for root, label in [("wiki/sources", "source")] + ALL_KIND_ROOTS:
            for p in glob.glob(f"{root}/**/*.md", recursive=True):
                p = p.replace("\\", "/")
                if args.explain in os.path.basename(p)[:-3]:
                    candidates.append((p, label))
        for p in glob.glob("skills/*/PURPOSE.md"):
            p = p.replace("\\", "/")
            if args.explain in os.path.basename(p)[:-3] or args.explain in os.path.dirname(p):
                candidates.append((p, "purpose"))
        if not candidates:
            print(f"OUT-OF-SCOPE: no page found matching '{args.explain}' under wiki/ or skills/*/PURPOSE.md")
            return
        for p, label in candidates:
            if not args.all_kinds and label != "source":
                print(f"OUT-OF-SCOPE: {p} — kind={label}, structurally skipped without --all-kinds "
                      f"(pass --all-kinds to grade patterns/entities/concepts/references/purpose pages)")
            else:
                print(f"OUT-OF-SCOPE: {p} — kind={label}, not selected by --explain's substring match "
                      f"against its own slug (this should not happen; report as a bug)")
        return

    src_rows = [r for r in rows if r["kind_bucket"] == "source"]
    n = len(src_rows)
    print(f"=== v4.0 CONFORMANCE — {n} /sources/ pages "
          f"({'ledger written' if args.write_ledger else 'stdout only, ledger NOT touched'}) ===")
    print(f"  grades: {GLYPH[PASS]}=PASS  {GLYPH[FAIL]}=FAIL  {GLYPH[NA_KIND]}=N/A-by-kind  "
          f"{GLYPH[NA_BLOCKED]}=N/A-blocked  {GLYPH[UNRECOVERABLE]}=unrecoverable")
    for c in CHECKS:
        d = {}
        for r in src_rows: d[r["C"][c]] = d.get(r["C"][c], 0) + 1
        p = d.get(PASS, 0); f_ = d.get(FAIL, 0)
        na = n - p - f_
        print(f"  {c:14} PASS {p:>4} ({100*p//n:>3}%)   FAIL {f_:>4}   non-applicable {na:>4}")
    print(f"  conformant(v4.0): {sum(1 for r in src_rows if r['conformant'])}/{n}")
    all_rows = rows          # keep the full (source + new-kind) set for the --all-kinds sweep below
    rows = src_rows          # everything below this line (unchanged from pre-W-6) operates on /sources/ only

    from collections import Counter
    print(f"  audit_state: {dict(Counter(r['state'] for r in rows))}")
    stale = [r["slug"] for r in rows if r["state"].startswith("verified@stale")]
    if stale:
        print(f"  !! verified at a SUPERSEDED standard (G3: demoted authority): {stale}")

    print(f"\n=== DETERMINISTIC BROKEN ANCHORS (Tn > verified turn count) — {len(broken_anchor_pages)} pages ===")
    for slug, count, oor in broken_anchor_pages:
        print(f"  {slug}: count={count}, out-of-range={oor}")
    print("\nNOTE: in-range anchors are NOT verified here. scripts/lint_citation_coverage.py's\n"
          "sampled arm put genuine in-range support at ~40% against this file's 96.7%.")

    if args.all_kinds:
        new_rows = [r for r in all_rows if r["kind_bucket"] != "source"]
        print(f"\n=== KIND-AWARE SWEEP (--all-kinds), {len(new_rows)} non-source pages "
              f"(patterns/entities/concepts/references/purpose) ===")
        print(f"  grades: {GLYPH[PASS]}=PASS  {GLYPH[FAIL]}=FAIL  {GLYPH[NA_KIND]}=N/A-by-kind  "
              f"{GLYPH[UNRECOVERABLE]}=unrecoverable  (UNKNOWN/unrecoverable is reported as its "
              f"own NA bucket below, never folded into CONFORMANT)")
        from collections import Counter, defaultdict
        by_kind = defaultdict(list)
        for r in new_rows:
            by_kind[r["kind"]].append(r)
        print(f"\n  {'kind':16} {'pages':>6} {'CONFORMANT':>11} {'FAIL':>6} {'NA':>6}")
        for kind_label in sorted(by_kind):
            grp = by_kind[kind_label]
            statuses = [display_status(r["C"]) for r in grp]
            print(f"  {kind_label:16} {len(grp):>6} {statuses.count('CONFORMANT'):>11} "
                  f"{statuses.count('FAIL'):>6} {statuses.count('NA'):>6}")
        all_statuses = [display_status(r["C"]) for r in new_rows]
        print(f"  {'TOTAL':16} {len(new_rows):>6} {all_statuses.count('CONFORMANT'):>11} "
              f"{all_statuses.count('FAIL'):>6} {all_statuses.count('NA'):>6}")

        failing = [(r, display_status(r["C"])) for r in new_rows if display_status(r["C"]) != "CONFORMANT"]
        print(f"\n  --- failing/NA pages ({len(failing)}) and their non-PASS checks ---")
        for r, status in sorted(failing, key=lambda t: (t[0]["kind"], t[0]["slug"])):
            bad = [f"{c}={r['C'][c]}" for c in CHECKS_NEW if r["C"][c] not in (PASS, NA_KIND)]
            print(f"  [{status:10}] {r['kind']:10} {r['slug']}: {', '.join(bad) if bad else '(see NA check above)'}")

    if args.write_ledger:
        out = f"{WIKI}/references/audit-conformance-ledger.md"
        with open(out, "w", encoding="utf-8") as f:
            f.write("---\ntitle: v4.0 Conformance Ledger\n"
                    "status: generated by scripts/audit/lint.py --write-ledger (deterministic)\n---\n\n")
            f.write(f"# v4.0 Conformance Ledger — {n} pages\n\n")
            f.write(f"Grades: `{GLYPH[PASS]}` PASS · `{GLYPH[FAIL]}` FAIL · `{GLYPH[NA_KIND]}` N/A-by-kind · "
                    f"`{GLYPH[NA_BLOCKED]}` N/A-blocked · `{GLYPH[UNRECOVERABLE]}` unrecoverable. "
                    f"Conformant = no FAIL. audit_state authority per G3; the standard version is "
                    f"PRESERVED, so `verified@stale` is distinguishable from `verified@current` "
                    f"(current = {CURRENT_STANDARD}).\n\n")
            f.write("| slug | trunk | kind | audit_state | " +
                    " | ".join(c.replace('_', '·') for c in CHECKS) + " | anchor_range | v4.0 |\n")
            f.write("|" + "---|" * (len(CHECKS) + 6) + "\n")
            for r in sorted(rows, key=lambda r: (r["trunk"], r["slug"])):
                cells = "".join(GLYPH.get(r["C"][c], "?") + " | " for c in CHECKS)
                f.write(f"| {r['slug']} | {r['trunk']} | {r['kind']} | {r['state']} | "
                        f"{cells}{r['anchor_range']} | {'YES' if r['conformant'] else '·'} |\n")
        print(f"\nledger -> {out}")


if __name__ == "__main__":
    main()
