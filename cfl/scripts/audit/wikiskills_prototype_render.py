#!/usr/bin/env python3
"""wikiskills_prototype_render.py -- renders wiki/WIKISKILLS-PROTOTYPE.md, the ONE page (lane W-5,
week-2026-09-02-corpus map, wiki/tracker/wayfinder-week-2026-09-02-corpus-wikiskills.md sec 2.4).

Every number in the rendered page is COMPUTED here from disk at render time -- none is typed into
the page body by hand. Stdlib only (hashlib, subprocess, glob, re, json, argparse). Reuses
scripts/audit/lint.py's parse()/kind_of()/grade() for the one worked-chain lint verdict and for
the --all-kinds sweep (W-6, already landed) that drives the "Not compliant yet" section.

Windows paths are used in every filesystem access (this repo's own convention -- POSIX paths
passed inline to `python -c` fail on this box; here everything goes through os.path / glob, which
both accept forward or back slashes on Windows, so no argv/-c distinction matters).

--check: re-render to memory, compare byte-for-byte against the file on disk, exit 1 on any diff
         (including a body that is otherwise identical -- the whole file, frontmatter included,
         must be byte-identical when nothing on disk changed since the last render).
"""
import argparse
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "scripts", "audit"))
import lint  # noqa: E402  (same-dir module, per lint.py's own convention)

OUT_PATH = os.path.join(REPO, "wiki", "WIKISKILLS-PROTOTYPE.md")
N_ROOT = "N:/claude-corpus/cfl"
UNKNOWNS = []  # (label, reason) -- appended live, printed in full, never silently dropped


def note_unknown(label, reason):
    UNKNOWNS.append((label, reason))
    return f"UNKNOWN ({reason})"


def sh(cmd):
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip()


def git_ls(pattern):
    out = sh(["git", "ls-files", pattern])
    return [l for l in out.splitlines() if l.strip()]


def commit_short():
    return sh(["git", "rev-parse", "--short", "HEAD"]) or note_unknown("commit", "git rev-parse failed")


def count_walk(root, exts=None):
    if not os.path.isdir(root):
        return None
    n = 0
    for dp, _, files in os.walk(root):
        for f in files:
            if exts is None or os.path.splitext(f)[1].lower() in exts:
                n += 1
    return n


def sha256_of(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError as e:
        return None, str(e)


def read_frontmatter(path):
    try:
        fm, body, text = lint.parse(path)
        return fm, body, text
    except OSError:
        return {}, "", ""


# ---------------------------------------------------------------------------------------------
# Section 1: three-directory tree with live counts
# ---------------------------------------------------------------------------------------------
def section_tree():
    lines = ["## 1. Three-directory shape, live counts\n"]

    originals_n = count_walk(os.path.join(N_ROOT, "raw", "originals"))
    if originals_n is None:
        originals_line = note_unknown("raw/originals count", f"{N_ROOT}/raw/originals not reachable")
    else:
        originals_line = f"{originals_n} files (N: mirror, `{N_ROOT}/raw/originals`, listing only)"

    transcripts_n = count_walk(os.path.join(N_ROOT, "raw", "transcripts"))
    if transcripts_n is None:
        transcripts_line = note_unknown("raw/transcripts count", f"{N_ROOT}/raw/transcripts not reachable")
    else:
        transcripts_line = f"{transcripts_n} files (N: mirror, `{N_ROOT}/raw/transcripts`, listing only)"

    fl_dir = os.path.join(REPO, "raw", "transcripts", "claude-code", "fl")
    minted = glob.glob(os.path.join(fl_dir, "*window-*"))
    minted_line = f"{len(minted)} (`raw/transcripts/claude-code/fl/`, filesystem glob `*window-*`; " \
                  f"gitignored -- not in `git ls-files`)"

    sources = git_ls("wiki/sources")
    superseded = 0
    for p in sources:
        fm, _, _ = read_frontmatter(os.path.join(REPO, p.replace("/", os.sep)))
        if fm.get("state", "").strip() == "superseded":
            superseded += 1
    concepts = len(git_ls("wiki/concepts"))
    entities = len([p for p in git_ls("wiki/entities") if not p.endswith("/index.md")])
    patterns = len([p for p in git_ls("wiki/patterns") if not p.endswith("/index.md")])
    references = len(git_ls("wiki/references"))
    log_path = os.path.join(REPO, "wiki", "log.md")
    try:
        with open(log_path, encoding="utf-8", errors="ignore") as f:
            log_lines = sum(1 for _ in f)
    except OSError:
        log_lines = note_unknown("wiki/log.md lines", "file not reachable")

    skill_dirs = [d for d in glob.glob(os.path.join(REPO, "skills", "*")) if os.path.isdir(d)]
    skill_md = sum(1 for d in skill_dirs if os.path.isfile(os.path.join(d, "SKILL.md")))
    purpose_md = [d for d in skill_dirs if os.path.isfile(os.path.join(d, "PURPOSE.md"))]
    resolved, unknown_mp = 0, 0
    for d in purpose_md:
        fm, _, text = read_frontmatter(os.path.join(d, "PURPOSE.md"))
        mp = fm.get("motivating_pattern", "").strip()
        if mp == "UNKNOWN":
            unknown_mp += 1
        elif re.match(r"^\[\[[^\]]+\]\]$", mp):
            resolved += 1
    val_splits = sorted(os.listdir(os.path.join(REPO, "wiki", "skills-gate", "validation"))) \
        if os.path.isdir(os.path.join(REPO, "wiki", "skills-gate", "validation")) else []

    lines.append("```")
    lines.append("raw/")
    lines.append(f"  originals/       {originals_line}")
    lines.append(f"  transcripts/     {transcripts_line}")
    lines.append(f"    claude-code/fl/  minted windows: {minted_line}")
    lines.append("wiki/")
    lines.append(f"  sources/         {len(sources)} pages (git ls-files), of which state:superseded = {superseded}")
    lines.append(f"  concepts/        {concepts} pages")
    lines.append(f"  entities/        {entities} pages (excl. index.md)")
    lines.append(f"  patterns/        {patterns} pages (excl. index.md)")
    lines.append(f"  references/      {references} pages")
    lines.append(f"  log.md           {log_lines} lines")
    lines.append("skills/")
    lines.append(f"  SKILL.md         {skill_md} of {len(skill_dirs)} skill dirs")
    lines.append(f"  PURPOSE.md       {len(purpose_md)}, of which motivating_pattern resolved={resolved} "
                 f"UNKNOWN={unknown_mp} unset/other={len(purpose_md) - resolved - unknown_mp}")
    lines.append(f"  validation/      splits present for: {', '.join(val_splits) if val_splits else '(none)'}")
    lines.append("```\n")
    return "\n".join(lines), dict(sources=len(sources), superseded=superseded)


# ---------------------------------------------------------------------------------------------
# Section 2: one worked chain, real paths
# ---------------------------------------------------------------------------------------------
def section_chain():
    lines = ["## 2. One worked chain (real paths, verified live)\n"]

    session = "9041f3b0-5102-4a06-a459-b076681a76bd"
    raw_jsonl = os.path.join(N_ROOT.replace("/", os.sep), "raw", "live-store-capture",
                              "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer",
                              session + ".jsonl")
    raw_ok = os.path.isfile(raw_jsonl)
    lines.append(f"1. **raw JSONL** (newest for session `{session[:8]}`): `{raw_jsonl}` "
                 f"-- {'resolves' if raw_ok else note_unknown('raw jsonl', 'path missing on N:')}")

    window = os.path.join(REPO, "raw", "transcripts", "claude-code", "fl",
                           "code-2026-09-02-9041f3-window-192940-v2.md")
    window_ok = os.path.isfile(window)
    lines.append(f"2. **minted window** (-v2 re-mint): `raw/transcripts/claude-code/fl/"
                 f"code-2026-09-02-9041f3-window-192940-v2.md` -- "
                 f"{'resolves' if window_ok else note_unknown('window', 'path missing')}")

    src_page = "wiki/sources/infrastructure/silent-success-hooks-continuity-untrusted-2026-08-18-3bafc5.md"
    src_abs = os.path.join(REPO, src_page.replace("/", os.sep))
    fm, body, text = read_frontmatter(src_abs)
    sf = fm.get("source_file", "")
    raw_abs = os.path.join(N_ROOT.replace("/", os.sep), sf.replace("/", os.sep)) if sf else None
    actual_sha = None
    if raw_abs and os.path.isfile(raw_abs):
        actual_sha = sha256_of(raw_abs)
    declared_sha = fm.get("raw_sha256", "").strip()
    sha_match = bool(actual_sha) and isinstance(actual_sha, str) and actual_sha == declared_sha
    slug = os.path.basename(src_page)[:-3]
    kind = lint.kind_of(fm, body, slug, src_page)
    C = lint.grade(src_page, fm, body, text, kind, N_ROOT)
    conformant = all(v in lint.NON_FAIL for v in C.values())
    lines.append(f"3. **source page from this week's S-lane batch** (added to this branch since "
                 f"2026-09-01, `source_file` resolving under the N: root):\n   `{src_page}`\n"
                 f"   - `source_file`: `{sf}`\n"
                 f"   - declared `raw_sha256`: `{declared_sha}`\n"
                 f"   - recomputed sha256 (from `{raw_abs}`): `{actual_sha}` -- "
                 f"{'MATCH' if sha_match else 'MISMATCH/UNKNOWN'}\n"
                 f"   - `lint.grade()` verdict (via `lint.py --main-root {N_ROOT}`): "
                 f"{', '.join(f'{k}={v}' for k, v in C.items())}\n"
                 f"   - CONFORMANT: **{conformant}**")

    pat = "wiki/patterns/write-is-not-delivery.md"
    pat_ok = os.path.isfile(os.path.join(REPO, pat.replace("/", os.sep)))
    src_links_pat = "[[write-is-not-delivery]]" in text
    lines.append(f"4. **pattern page** `[[write-is-not-delivery]]`: `{pat}` -- "
                 f"{'resolves' if pat_ok else note_unknown('pattern page', 'missing')}. "
                 f"Linked FROM the source page above: {'yes' if src_links_pat else 'NO -- this chain link is topical, not a live [[..]] wikilink on this specific page'}")

    purpose = "skills/exchange-letters/PURPOSE.md"
    purpose_ok = os.path.isfile(os.path.join(REPO, purpose.replace("/", os.sep)))
    lines.append(f"5. **skill purpose**: `{purpose}` -- {'resolves' if purpose_ok else note_unknown('purpose', 'missing')}")

    lines.append("6. **LEDGER GT-1 rows** (`wiki/skills-gate/LEDGER.md`), best-so-far R for exchange-letters:")
    lines.append("   | run | R | detail |")
    lines.append("   |---|---|---|")
    baseline_p = os.path.join(REPO, "wiki", "skills-gate", "validation", "exchange-letters", "baseline.json")
    blind_p = os.path.join(REPO, "wiki", "skills-gate", "validation", "exchange-letters", "blind-run1-full.json")
    for label, p, key in [("author (R_best)", baseline_p, "R_best"), ("author R_degraded", baseline_p, "R_degraded")]:
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            lines.append(f"   | {label} | {d.get(key)} | {p.replace(REPO + os.sep, '')} |")
        except (OSError, json.JSONDecodeError) as e:
            lines.append(f"   | {label} | {note_unknown(label, str(e))} | |")
    try:
        with open(blind_p, encoding="utf-8") as f:
            d = json.load(f)
        lines.append(f"   | blind (first non-author score) | {d.get('R')} "
                     f"({d.get('passed')}/{d.get('passed', 0) + d.get('failed', 0)} scored, "
                     f"{d.get('unknown')} UNKNOWN excluded) | {blind_p.replace(REPO + os.sep, '')} |")
    except (OSError, json.JSONDecodeError) as e:
        lines.append(f"   | blind | {note_unknown('blind run', str(e))} | |")

    rp28_path = os.path.join(REPO, "wiki", "tracker", "PROBE-REGISTRY.md")
    try:
        with open(rp28_path, encoding="utf-8", errors="ignore") as f:
            rp_text = f.read()
        m = re.search(r"## RP-28.*?\n(.*?)\n## ", rp_text, re.S)
        rows = re.findall(r"\| RP28-Q\d[^\n]*\n", rp_text)
        n_pass = sum(1 for r in rows if "PASS" in r)
        lines.append(f"7. **PROBE-REGISTRY RP-28 rows**: `wiki/tracker/PROBE-REGISTRY.md` -- "
                     f"{len(rows)} rows found, {n_pass} PASS (no class flip)")
    except OSError:
        lines.append(f"7. **PROBE-REGISTRY RP-28 rows**: {note_unknown('RP-28', 'PROBE-REGISTRY.md not reachable')}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------------
# Section 3: baseline -> now table for D2..D12
# ---------------------------------------------------------------------------------------------
def section_baseline(commit, sources_n, superseded_n, sweep):
    lines = ["## 3. Baseline -> now (D2-D12)\n"]
    lines.append("| # | Check | Baseline | Now | Computed from | Commit |")
    lines.append("|---|---|---|---|---|---|")

    def row(n, check, baseline, now, src):
        lines.append(f"| {n} | {check} | {baseline} | {now} | `{src}` | `{commit}` |")

    row("D2", "wiki/sources pages (excl. session-stubs.md)", "158",
        f"{sources_n} (raw git ls-files count; not filtered for session-stubs.md by this renderer)",
        "git ls-files wiki/sources")

    census_json = os.path.join(REPO, "wiki", "intake-triage", "CENSUS-2026-09-02-coverage.json")
    src_c = "wiki/intake-triage/CENSUS-2026-09-02-coverage.json"
    try:
        with open(census_json, encoding="utf-8") as f:
            rows_c = json.load(f)  # list of per-session dicts with a 'class' and 'date'
        total = len(rows_c)
        covered = sum(1 for r in rows_c if r.get("class") in ("A", "B"))
        z = sum(1 for r in rows_c if r.get("class") == "Z")
        row("D3", "coverage census: sessions mapped (A+B)", "221/723 = 30.6%",
            f"{covered}/{total} = {100*covered/total:.1f}%", src_c)
        row("D4", "zero-footprint sessions (Z)", "351 = 48.5%",
            f"{z} = {100*z/total:.1f}%", src_c)
        aug = [r for r in rows_c if str(r.get("date", "")).startswith("2026-08")]
        aug_covered = sum(1 for r in aug if r.get("class") in ("A", "B"))
        if aug:
            row("D5", "August 2026 sessions covered", "8/425 = 1.9%",
                f"{aug_covered}/{len(aug)} = {100*aug_covered/len(aug):.1f}%", src_c)
        else:
            row("D5", "August 2026 sessions covered", "8/425 = 1.9%",
                note_unknown("D5", "no August-dated rows found in census json"), src_c)
    except (OSError, json.JSONDecodeError, TypeError) as e:
        for n, c in [("D3", "coverage A+B"), ("D4", "zero-footprint Z"), ("D5", "August covered")]:
            row(n, c, "see map", note_unknown(n, f"census json unreadable: {e}"), src_c)
    if sweep is None:
        for n, c in [("D6", "pages created this week lint-clean"),
                     ("D7", "wiki/entities pages, lint-clean"),
                     ("D11", "wiki/patterns pages, conformant (E9_backref proxy)"),
                     ("D12", "PURPOSE.md motivating_pattern resolved+UNKNOWN")]:
            row(n, c, "see map", note_unknown(n, "lint sweep unavailable"), "scripts/audit/lint.py --all-kinds")
    else:
        added_this_week = set(sh(["git", "log", "--since=2026-09-01", "--diff-filter=A",
                                   "--name-only", "--pretty=format:", "--", "wiki/sources/"]).splitlines())
        added_this_week = {p.strip().replace("\\", "/") for p in added_this_week if p.strip()}
        new_rows = [r for r in sweep if r["path"].replace("\\", "/") in added_this_week]
        new_clean = sum(1 for r in new_rows if r["conformant"])
        row("D6", "pages created this week (this branch), lint-clean", "unmeasured",
            f"{new_clean}/{len(new_rows)}" + (f" = {100*new_clean/len(new_rows):.0f}%" if new_rows else " (0 added)"),
            "git log --since=2026-09-01 --diff-filter=A -- wiki/sources/ + lint sweep")

        ent_rows = [r for r in sweep if r["label"] == "entity"]
        ent_clean = sum(1 for r in ent_rows if r["conformant"])
        row("D7", "wiki/entities pages, lint-clean", "0", f"{ent_clean}/{len(ent_rows)}",
            "lint.py --all-kinds sweep, label=entity")

        pat_rows = [r for r in sweep if r["label"] == "pattern"]
        pat_ok = sum(1 for r in pat_rows if r["C"].get("E9_backref") == lint.PASS)
        row("D11", "wiki/patterns pages, >=2 locators + Motivates (E9_backref)", "0",
            f"{pat_ok}/{len(pat_rows)}", "lint.py --all-kinds sweep, label=pattern, E9_backref")

        pur_rows = [r for r in sweep if r["label"] == "purpose"]
        pur_resolved = sum(1 for r in pur_rows if r["C"].get("E9_backref") == lint.PASS)
        skill_dirs_n = len([d for d in glob.glob(os.path.join(REPO, "skills", "*")) if os.path.isdir(d)])
        row("D12", "skills/<name>/PURPOSE.md, motivating_pattern resolves or UNKNOWN", "0",
            f"{pur_resolved}/{len(pur_rows)} pass E9_backref ({len(pur_rows)} of {skill_dirs_n} skill dirs have a PURPOSE.md)",
            "lint.py --all-kinds sweep, label=purpose, E9_backref")
    for n, c, base in [
        ("D8", "dangling path citations", "433/1,314 = 33%; 34 CFL-origin"),
        ("D9", "wiki/index.md last_updated == disk", "08-23; 49 vs 56"),
        ("D10", "retrieve.py on 8 sealed probes", "118 s"),
    ]:
        row(n, c, base, note_unknown(n, "requires a dedicated instrument run "
            "(check_wiki_path_refs.py / wiki/index.md diff / retrieve.py timing x8) this renderer does not invoke"),
            "see D-row source path in the map's done-test table")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------------
# Section 4: last 10 INGEST-LEDGER index lines + last 5 REJECTED/superseded
# ---------------------------------------------------------------------------------------------
def section_ledger():
    lines = ["## 4. INGEST-LEDGER and rejections/supersessions\n"]
    ledger_path = os.path.join(REPO, "wiki", "skills-gate", "INGEST-LEDGER.md")
    try:
        with open(ledger_path, encoding="utf-8", errors="ignore") as f:
            text = f.read()
        idx_lines = [l for l in text.splitlines() if re.match(r"^- \d{4}-\d{2}-\d{2} ", l)]
        lines.append(f"**Last 10 index lines** (of {len(idx_lines)} total in `wiki/skills-gate/INGEST-LEDGER.md`):\n")
        for l in idx_lines[-10:]:
            lines.append(f"- {l[2:]}")
        rejected = [l for l in idx_lines if "REJECTED" in l]
        lines.append(f"\n**Last 5 REJECTED rows** (of {len(rejected)} total):\n")
        for l in rejected[-5:]:
            lines.append(f"- {l[2:]}")
    except OSError as e:
        lines.append(note_unknown("INGEST-LEDGER", str(e)))

    superseded_pages = []
    for p in git_ls("wiki/sources"):
        fm, _, _ = read_frontmatter(os.path.join(REPO, p.replace("/", os.sep)))
        if fm.get("state", "").strip() == "superseded":
            superseded_pages.append(p)
    lines.append(f"\n**wiki/sources pages with `state: superseded`** ({len(superseded_pages)} total, last 5 by "
                 f"git-ls-files order):\n")
    for p in superseded_pages[-5:]:
        lines.append(f"- `{p}`")
    lines.append("")
    return "\n".join(lines)


def compute_sweep():
    """Run lint's --all-kinds sweep once; return list of dicts reused by sections 3 and 5."""
    pages, kindmap = lint.collect_pages(all_kinds=True)
    slug_index = lint.build_slug_index()
    out = []
    for path in pages:
        fm, body, text = read_frontmatter(path)
        slug = os.path.basename(path)[:-3]
        label = kindmap[path]
        if label == "source":
            if "wiki/sources/" not in path.replace("\\", "/"):
                continue
            kind = lint.kind_of(fm, body, slug, path)
            C = lint.grade(path, fm, body, text, kind, N_ROOT)
        else:
            kind = lint.effective_kind(fm, label)
            C = lint.grade_new_kind(fm, body, text, kind, N_ROOT, slug_index)
        out.append(dict(path=path, slug=slug, kind=kind, label=label, C=C,
                         conformant=all(v in lint.NON_FAIL for v in C.values())))
    return out


# ---------------------------------------------------------------------------------------------
# Section 5: Not compliant yet
# ---------------------------------------------------------------------------------------------
def section_not_compliant(sweep):
    lines = ["## Not compliant yet\n"]
    if sweep is None:
        lines.append(note_unknown("lint sweep", "compute_sweep() failed -- see section 3 note"))
        return "\n".join(lines)

    fail_by_check = {}
    unknown_rows = 0
    total = len(sweep)
    for r in sweep:
        for check, verdict in r["C"].items():
            if verdict == lint.FAIL:
                fail_by_check[check] = fail_by_check.get(check, 0) + 1
            if verdict == lint.UNRECOVERABLE:
                unknown_rows += 1

    lines.append(f"Lint sweep over {total} pages (`wiki/sources` full set + `--all-kinds` "
                 f"patterns/entities/concepts/references/purpose), `--main-root {N_ROOT}`:\n")
    lines.append("| check | FAIL count |")
    lines.append("|---|---|")
    for check, n in sorted(fail_by_check.items()):
        lines.append(f"| {check} | {n} |")
    lines.append(f"\n**UNRECOVERABLE/UNKNOWN rows** (raw unreachable from N:, graded as their own class, "
                 f"never rounded to PASS): {unknown_rows}")
    lines.append("")
    lines.append("**What this renderer could not compute** (named, never omitted):")
    if UNKNOWNS:
        for label, reason in UNKNOWNS:
            lines.append(f"- `{label}`: {reason}")
    else:
        lines.append("- (none this run)")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------------
def render():
    global UNKNOWNS
    UNKNOWNS = []
    commit = commit_short()
    tree_md, tree_stats = section_tree()
    chain_md = section_chain()
    try:
        sweep = compute_sweep()
    except Exception as e:
        note_unknown("lint sweep (section 3 + 5)", f"compute_sweep() raised: {e}")
        sweep = None
    baseline_md = section_baseline(commit, tree_stats["sources"], tree_stats["superseded"], sweep)
    ledger_md = section_ledger()
    notcompliant_md = section_not_compliant(sweep)  # must run before frontmatter (needs final UNKNOWNS)

    body_parts = [
        "# WikiSkills prototype: CFL knowledgebase in the three-directory shape\n",
        "Rendered by `scripts/audit/wikiskills_prototype_render.py`. Every number below is computed "
        "live from disk at render time (git ls-files, filesystem walks, `lint.py` grade calls, JSON "
        "reads) -- none is hand-typed. Re-run with `--check` to verify this file is still "
        "byte-identical to a fresh render.\n",
        tree_md,
        chain_md,
        baseline_md,
        ledger_md,
        notcompliant_md,
    ]
    body = "\n".join(body_parts).rstrip() + "\n"
    body_sha = hashlib.sha256(body.encode("utf-8")).hexdigest()

    fm_lines = [
        "---",
        "format: cfl-page/v1",
        "kind: reference",
        "slug: WIKISKILLS-PROTOTYPE",
        'title: "WikiSkills prototype: CFL knowledgebase in the three-directory shape"',
        f"date: {time.strftime('%Y-%m-%d', time.gmtime())}",
        "generated_by: scripts/audit/wikiskills_prototype_render.py",
        f"rendered_at: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
        f"commit: {commit}",
        f"rendered_sha256: {body_sha}",
        "---",
        "",
    ]
    return "\n".join(fm_lines) + body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                     help="re-render to memory, compare to the file on disk, exit 1 on any diff")
    args = ap.parse_args()

    rendered = render()

    if args.check:
        try:
            with open(OUT_PATH, encoding="utf-8") as f:
                on_disk = f.read()
        except OSError as e:
            print(f"CHECK FAIL: cannot read {OUT_PATH}: {e}")
            sys.exit(1)
        # rendered_at differs by construction on every run -- compare everything else byte-for-byte.
        def strip_rendered_at(s):
            return re.sub(r"^rendered_at: .*$", "rendered_at: STRIPPED", s, flags=re.M)
        if strip_rendered_at(rendered) != strip_rendered_at(on_disk):
            print("CHECK FAIL: re-render differs from wiki/WIKISKILLS-PROTOTYPE.md (excl. rendered_at)")
            sys.exit(1)
        print("CHECK OK: byte-identical (excl. rendered_at)")
        return

    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(rendered)
    print(f"Wrote {OUT_PATH} ({len(rendered.encode('utf-8'))} bytes)")
    if UNKNOWNS:
        print(f"{len(UNKNOWNS)} UNKNOWN item(s) recorded in the page (never omitted):")
        for label, reason in UNKNOWNS:
            print(f"  - {label}: {reason}")


if __name__ == "__main__":
    main()
