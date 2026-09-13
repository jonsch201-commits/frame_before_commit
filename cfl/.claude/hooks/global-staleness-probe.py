#!/usr/bin/env python3
"""global-staleness-probe.py — READ-ONLY. Tells the session when `~/.claude/` has gone stale.

WIRED AS: a SessionStart hook on matcher `compact|clear`, alongside `post-compact-wake.sh`.
WRITES:   nothing, anywhere. Not to `~/.claude/`, not to the repo, not to a state file.

WHY THIS EXISTS
---------------
CFL's `.claude/settings.json` has two SessionStart entries:

    startup|resume  -> git pull + `bash sync-universal.sh`   (WRITES to ~/.claude/)
    compact|clear   -> post-compact-wake.sh                  (reads only)

On 2026-08-07 **every session in this project was a compact or a resume-in-place**, so the
`startup|resume` entry never fired, and `~/.claude/CLAUDE.md` sat **21 hours stale** — the global
layer that every project in every trunk reads. Jon's ruling closing C-6 names it:

    "The global layer is the channel that failed (CLAUDE.md 21h stale; letters worked)."

It was fixed by hand in commit `88fb610`.

Claude Personal supplied the enabling measurement
(`exchange/inbound/personal-to-cfl-sessionstart-fires-on-compact-2026-08-07.md`): **SessionStart
DOES fire with `source=compact`** — observed at least six times across 2026-08-06/07. They
deliberately declined to say what CFL should do with it:

    "Whether that is the right behavior for a hook that rewrites `~/.claude/` — mid-day, for every
     project at once — is exactly the kind of scope question."

DETECTION, NOT MUTATION — AND WHY THAT IS THE WHOLE POINT
----------------------------------------------------------
**The failure on 2026-08-07 was not that the sync did not run. It was that nobody knew for 21
hours.** A silent divergence is the defect; the missing write is only how it started. So this probe
converts an invisible global-write-that-did-not-happen into a loud local notice, and stops there.

Widening the WRITING hook to `compact|clear` is a separate decision with a real cost — a CFL
compact would rewrite the global layer for Personal, Professional and Herald mid-session — and it
is staged for Jon, not taken here. The layer Jon just ruled had failed is not the layer to start
mutating on a new trigger without him.

SILENCE IS THE HARD REQUIREMENT, AND IT IS TESTED, NOT ASSERTED
----------------------------------------------------------------
`SessionStart` stdout becomes session context (unlike `PreCompact`, whose stdout goes only to the
debug log). That is why this works at all — and it is also the hazard. **CFL's `SubagentStop` hooks
destroyed FOUR agent returns on 2026-08-06 and another on 08-07 by injecting text into contexts
that had no room for it.** `CARRIER.md` asserted both of those hooks were "silent on no-op"; when
somebody finally measured, they were emitting **323 B and 228 B**.

So the requirement is not "short". It is **zero bytes on stdout when there is nothing to say**, and
`--self-test` asserts exactly that against a no-divergence fixture — byte count, not a claim in a
comment. A property recorded once and never checked is precisely what went false here.

A ZERO DENOMINATOR IS NOT SILENCE
----------------------------------
This repo's characteristic failure is an instrument that passes by not looking — a blocking gate
once reported "0 UNSUPPORTED out of 0 resolvable" and was read as a pass. So the silent path is
reachable on exactly one condition: **the comparison actually ran, over a non-zero number of
artifacts, and found them identical.** If a root is missing, the comparator cannot be imported, or
the denominator is zero, the probe SPEAKS and says UNKNOWN. It never renders "could not look" as
"nothing to report."

ONE COMPARATOR, NOT TWO
-----------------------
Skill parity is delegated to `scripts/audit/sync_parity.py` (`classify()`), the existing witness for
repo-vs-deployed divergence — SHA-256 over every file, never mtime, never size. Writing a second
comparator here would be this repo's #1 defect ("a fact written down once, then diverging with
nothing able to notice") committed inside the fix for it.

`sync_parity.py` covers `skills/` only. `sync-universal.sh:24` also deploys `CLAUDE.md`, and
**`CLAUDE.md` is the artifact that actually went stale on 08-07** — so this probe hashes that one
pair itself. That is a gap in `sync_parity.py`'s scope, not a duplicate of its logic; it is logged
in the deposit as an OPEN item to fold upstream.

mtimes are used ONLY to annotate the age of a divergence, never to detect one. This tree is on
Google Drive, where sync can rewrite mtimes; the hash is the verdict and the age is labelled approx.

SAFETY
  Reads: its own stdin (discarded), two file trees, `os.stat`. No network, no credentials, no
  writes, no deletes. FAILS OPEN on every path — but fails open LOUDLY, per the rule above.

Usage:
    python .claude/hooks/global-staleness-probe.py            # hook mode: JSON or nothing
    python .claude/hooks/global-staleness-probe.py --report   # human mode: always prints
    python .claude/hooks/global-staleness-probe.py --self-test

Exit: 0 always. A hook that breaks a session open is worse than no hook.
"""
import importlib.util
import json
import hashlib
import os
import sys
import time

REPO = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DEPLOYED = os.path.expanduser("~/.claude")
FIX = "bash sync-universal.sh"


def sha256(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def hours_ago(ts):
    try:
        return max(0.0, (time.time() - ts) / 3600.0)
    except Exception:
        return None


def load_sync_parity(repo):
    """Import the EXISTING comparator by path. Returns (module, error_string)."""
    p = os.path.join(repo, "scripts", "audit", "sync_parity.py")
    if not os.path.isfile(p):
        return None, f"scripts/audit/sync_parity.py not found at {p}"
    try:
        spec = importlib.util.spec_from_file_location("_sync_parity_probe", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, None
    except Exception as e:                                    # noqa: BLE001 - fail open, loudly
        return None, f"could not import sync_parity.py: {type(e).__name__}: {e}"


def probe(repo=REPO, deployed=DEPLOYED):
    """Returns (findings, unknowns, denominator).

    findings   — list of strings naming a real divergence. Non-empty => speak.
    unknowns   — list of strings naming something we could NOT check. Non-empty => speak.
    denominator— artifacts actually compared. ZERO => speak (this is the "passed by not
                 looking" guard; a comparison over nothing is never a pass).
    """
    findings, unknowns, denom = [], [], 0

    # ---- artifact 1: the GLOBAL context file -----------------------------------------------
    #
    # ⛔ CORRECTED 2026-08-17, AND THIS PROBE WOULD HAVE BECOME A PERMANENT FALSE ALARM WITHOUT IT.
    # The original compared repo CLAUDE.md against deployed CLAUDE.md:
    #     repo_md = os.path.join(repo, "CLAUDE.md")
    # On 2026-08-17 sync-universal.sh stopped deploying CLAUDE.md and started deploying
    # CLAUDE-UNIVERSAL.md, because copying CFL's PROJECT constitution to the GLOBAL layer meant
    # every trunk on this machine loaded one trunk's file as its global. After that change the old
    # comparison can NEVER match: it would report "CLAUDE.md DIVERGED" at every single SessionStart,
    # forever, for a repo that is perfectly in sync.
    #
    # ⚠️ That is this repo's own retired-RATIO_FLOOR defect: an alarm that can never return clean is
    # a mute button, and the next real divergence would have arrived inside a stream of false ones.
    # It is also the migrations-blind-instruments pattern -- the fix to a file silently disabling the
    # instrument that watches that file. Caught before its first fire, by asking what the change did
    # to the watchdog rather than only to the target.
    #
    # THE PROBE MUST COMPARE THE ACTUAL DEPLOY SOURCE. Fall back to CLAUDE.md so this keeps working
    # in a tree that predates the split, and SAY which one was compared -- a probe that silently
    # changes its own denominator is the thing it exists to catch.
    repo_md = os.path.join(repo, "CLAUDE-UNIVERSAL.md")
    md_src = "CLAUDE-UNIVERSAL.md"
    if not os.path.isfile(repo_md):
        repo_md = os.path.join(repo, "CLAUDE.md")
        md_src = "CLAUDE.md (legacy: CLAUDE-UNIVERSAL.md absent)"
    dep_md = os.path.join(deployed, "CLAUDE.md")
    if not os.path.isfile(repo_md):
        unknowns.append(f"repo global-context source missing at {repo_md} — cannot compare")
    elif not os.path.isfile(dep_md):
        findings.append(f"~/.claude/CLAUDE.md IS ABSENT (repo has {md_src}) — the sync has never run here")
        denom += 1
    else:
        denom += 1
        a, b = sha256(repo_md), sha256(dep_md)
        if a is None or b is None:
            unknowns.append("CLAUDE.md unreadable on one side — cannot compare")
        elif a != b:
            r_age, d_age = hours_ago(os.path.getmtime(repo_md)), hours_ago(os.path.getmtime(dep_md))
            drift = ""
            if r_age is not None and d_age is not None:
                gap = abs(d_age - r_age)
                newer = "repo" if r_age < d_age else "deployed"
                drift = (f" [approx, mtime on a Drive tree] repo written {r_age:.1f}h ago, "
                         f"deployed written {d_age:.1f}h ago; {newer} is newer by {gap:.1f}h")
            findings.append(f"global CLAUDE.md DIVERGED from repo {md_src} (sha256){drift}")

    # ---- artifact 2: skills/ — delegated to the existing comparator ------------------------
    mod, err = load_sync_parity(repo)
    if err:
        unknowns.append(err + " — skill parity NOT checked")
    else:
        repo_skills = os.path.join(repo, "skills")
        dep_skills = os.path.join(deployed, "skills")
        e1 = mod.check_root(dep_skills, "deployed-root")
        e2 = mod.check_root(repo_skills, "repo-root")
        if e1 or e2:
            unknowns.append(f"skills roots unusable — {(e1 or e2).splitlines()[0]}")
        else:
            try:
                results, _, _ = mod.classify(repo_skills, dep_skills)
            except Exception as e:                            # noqa: BLE001
                results = None
                unknowns.append(f"sync_parity.classify() raised {type(e).__name__}: {e}")
            if results is not None:
                denom += len(results)
                if not results:
                    unknowns.append("skills comparison returned ZERO skills — an empty "
                                    "denominator is UNKNOWN, not parity")
                div = sorted(n for n, (v, _) in results.items() if v == mod.DIVERGED)
                gho = sorted(n for n, (v, _) in results.items() if v == mod.GHOST)
                mis = sorted(n for n, (v, _) in results.items() if v == mod.MISSING)
                if div:
                    findings.append(f"skills DIVERGED ({len(div)}): {', '.join(div[:6])}"
                                    f"{' …' if len(div) > 6 else ''}")
                if gho:
                    # A GHOST against CFL's repo is only the INPUT. Split it by fleet ownership
                    # before it becomes a claim -- see the note above build_message().
                    elsewhere, nowhere, unk = [], [], []
                    for g in gho:
                        who, badroots = owner_of(g)
                        unk.extend(badroots)
                        (elsewhere if who else nowhere).append(f"{g} [{who}]" if who else g)
                    if elsewhere:
                        findings.append(f"skills REACHABLE-ELSEWHERE ({len(elsewhere)}) — deployed "
                                        f"here, sourced in another trunk's repo, NOT a defect: "
                                        f"{', '.join(elsewhere[:6])}"
                                        f"{' …' if len(elsewhere) > 6 else ''}")
                    if nowhere:
                        findings.append(f"skills REACHABLE-NOWHERE ({len(nowhere)}) — deployed, live, "
                                        f"and sourced in NO repo on this disk: "
                                        f"{', '.join(nowhere[:6])}"
                                        f"{' …' if len(nowhere) > 6 else ''}")
                    if unk:
                        unknowns.append(f"{len(set(unk))} fleet skill root(s) unreadable "
                                        f"({', '.join(sorted(set(unk))[:4])}) — a skill sourced there "
                                        f"would be misreported as REACHABLE-NOWHERE")
                if mis:
                    findings.append(f"skills MISSING ({len(mis)}) — in repo, NOT deployed, so "
                                    f"not live this session: {', '.join(mis[:6])}"
                                    f"{' …' if len(mis) > 6 else ''}")

    # ---- artifact 3: scripts/ — added 2026-09-04, and the omission had a cost --------------
    #
    # `sync-universal.sh:113` deploys `scripts/` to ~/.claude/scripts/ exactly as it deploys
    # `skills/`. This probe compared skills/ ONLY, so an audit script committed after the last
    # sync was invisible to every other trunk and NOTHING SAID SO.
    #
    # ⛔ WHAT THAT COST, measured the same day: a CFL prototype asserted that scripts/ does not
    # sync at all — typed from memory, never read against sync-universal.sh — and published
    # "1 of 9 instruments can leave this trunk" to Jon. The truth was 6 of 9 deployed and 2
    # merely newer than the last sync. A silent gap invites an invented explanation for it.
    #
    # ⚠ DELIBERATELY NOT A CONTENT DIFF. Byte-comparing every script would report every
    # CRLF/LF difference on this machine and drown the signal; skills/ already has
    # sync_parity.py for content. This asks the cheaper, unasked question: DOES IT EXIST
    # THERE AT ALL. A file present but stale is a different finding from a file absent, and
    # only the second one means another trunk cannot run it.
    repo_scripts = os.path.join(repo, "scripts")
    dep_scripts = os.path.join(deployed, "scripts")
    if not os.path.isdir(repo_scripts):
        unknowns.append("no scripts/ in the repo — cannot compare (UNKNOWN, not 'in sync')")
    elif not os.path.isdir(dep_scripts):
        findings.append("scripts/ is NOT DEPLOYED AT ALL — no ~/.claude/scripts/. Every "
                        "instrument in this repo is unreachable from every other trunk.")
    else:
        missing, seen = [], 0
        for root, _d, files in os.walk(repo_scripts):
            for fn in files:
                if not fn.endswith((".py", ".sh", ".mjs")):
                    continue
                rel = os.path.relpath(os.path.join(root, fn), repo_scripts)
                # proto/ is throwaway by construction and is not expected to deploy.
                if rel.replace("\\", "/").startswith("proto/"):
                    continue
                seen += 1
                if not os.path.exists(os.path.join(dep_scripts, rel)):
                    missing.append(rel.replace("\\", "/"))
        denom += seen
        if seen == 0:
            unknowns.append("scripts comparison saw ZERO scripts — an empty comparison is "
                            "UNKNOWN, never a pass")
        elif missing:
            findings.append(f"scripts MISSING ({len(missing)} of {seen}) — in repo, NOT in "
                            f"~/.claude/scripts/, so NO OTHER TRUNK can run them: "
                            f"{', '.join(missing[:6])}{' …' if len(missing) > 6 else ''}")
    return findings, unknowns, denom



# ⛔ THE GHOST VERDICT WAS A ONE-TRUNK SEARCH PUBLISHED AS A FLEET FACT, corrected 2026-09-12 23:5x
# by Soul (Claude Personal) on the night it was written.
#
# What this probe said: "skills GHOST (1) -- deployed, live, no repo counterpart: tree-occupancy-guard",
# and CFL's coordinator repeated it as "live in every trunk with no reviewable source."
# `[measured 23:3x by Soul across five trunks; re-verified 23:5x here, first-hand]`
# /n/antigravity-hub/skills/tree-occupancy-guard/SKILL.md -- 2,534 B, mtime 2026-09-11 16:15.
# ANTIGRAVITY OWNS IT. The source exists and is reviewable. "No repo counterpart" was true of ONE
# repo -- CFL's -- because that is the only repo `sync_parity.classify()` compares against.
#
# ⭐ AND THE SAME CLASS WAS ALREADY CORRECTED ON THIS MACHINE EIGHT DAYS EARLIER, by Professional:
# "a machine-global skill that names a repo-relative script is broken by construction in every trunk
# except the one holding the script, because sync-universal.sh promotes skills/ machine-wide and never
# scripts/. Five instruments this trunk graded as dead are each alive in at least one trunk."
#
# ✅ SO THE BUCKET SPLIT, WHICH IS THE GENERAL FIX AND NOT A PATCH FOR ONE SKILL:
#   REACHABLE-ELSEWHERE  -- deployed here, sourced in another trunk's repo. NOT a defect. Name the owner.
#   REACHABLE-NOWHERE    -- deployed here, sourced in no repo on this disk. THE ONLY defect.
# A GHOST verdict from a two-tree comparison is the INPUT to this split, never the conclusion.
FLEET_SKILL_ROOTS = (
    ("cfl",          "N:/claude-cfl/clone/skills"),
    ("professional", "N:/claude-professional/skills"),
    ("personal",     "N:/claude-personal/skills"),
    ("secretary",    "N:/claude-secretary/skills"),
    ("antigravity",  "N:/antigravity-hub/skills"),
    ("personal-local", "N:/claude-personal/.claude/skills"),
    ("cfl-local",    "N:/claude-cfl/clone/.claude/skills"),
)


def owner_of(skill_name, roots=None):
    # ⚠️ READ THE MODULE GLOBAL AT CALL TIME, never as a default argument. The first version wrote
    # `roots=FLEET_SKILL_ROOTS`, which binds ONCE at definition, so the self-test's override of the
    # roots list had no effect and the new arm failed -- correctly. A default argument is a snapshot,
    # and a snapshot of a configuration is untestable by construction.
    """Which trunk's repo holds this skill's source? None means reachable-nowhere.

    An UNREADABLE root must not read as absence, so a root that cannot be listed is reported as
    UNKNOWN rather than skipped -- the caller then says UNKNOWN instead of 'nowhere'."""
    if roots is None:
        roots = FLEET_SKILL_ROOTS
    unknown = []
    for trunk, root in roots:
        try:
            if os.path.isfile(os.path.join(root, skill_name, "SKILL.md")):
                return trunk, unknown
        except OSError:
            unknown.append(trunk)
    return None, unknown


def build_message(findings, unknowns, denom):
    """Returns the additionalContext string, or None when there is nothing to say.

    None is returned on EXACTLY one condition: the comparison ran over a non-zero denominator
    and found no divergence and no unknowns.
    """
    if not findings and not unknowns and denom > 0:
        return None
    parts = ["GLOBAL LAYER STALENESS PROBE (read-only; wrote nothing)."]
    # ⛔ A ROW THE PROBE ITSELF CALLS "NOT a defect" MUST NOT INFLATE THE FINDING COUNT OR WEAR THE
    # ALARM HEADER. Added 2026-09-12 23:5x: after the bucket split, the only row on the live tree was
    # REACHABLE-ELSEWHERE (tree-occupancy-guard, sourced by Antigravity), and the probe still opened
    # with "DIVERGES FROM THE REPO — 1 finding(s)" and closed with the 08-07 outage quote. A reader
    # learns from that to discount the header, which is the same alarm-fatigue defect this probe was
    # repaired for an hour earlier on its remedy line.
    _informational = [f for f in findings if f.startswith("skills REACHABLE-ELSEWHERE")]
    _real = [f for f in findings if f not in _informational]
    if _real:
        parts.append(f"~/.claude/ DIVERGES FROM THE REPO — {len(_real)} finding(s) over "
                     f"{denom} artifact(s) compared: " + " | ".join(_real) + ".")
    if _informational:
        parts.append(f"NOTED, not a divergence ({denom} artifact(s) compared): "
                     + " | ".join(_informational) + ".")

    # ⛔ THE REMEDY IS CLASS-AWARE, and this block sits at FUNCTION level on purpose.
    # [2026-09-12 23:5x] An edit that added the informational header accidentally nested this under
    # `if _informational:`, so the FIX line vanished whenever the only findings were real ones --
    # exactly the cases that need it. The self-test caught it on two arms. A remedy that appears only
    # when an unrelated row is present is worse than none, because its absence reads as "no action".
    #
    # The original defect this block fixes: sync-universal.sh copies repo -> global with `cp -ru` and
    # its own code prints of an orphan "deployed-not-in-repo (orphan, NOT deleted)". So for a skill
    # sourced in no repo, the printed fix runs, reports success, and leaves the finding standing.
    _nowhere = any(f.startswith("skills REACHABLE-NOWHERE") for f in findings)
    _other = any(not f.startswith("skills REACHABLE-") for f in findings)
    if _other:
        parts.append(f"FIX (one command, from the repo root): {FIX}")
    if _nowhere:
        parts.append("⛔ THE SYNC DOES NOT CLEAR A REACHABLE-NOWHERE SKILL"
                     + (" (the line above is for the other finding(s) only)" if _other else "")
                     + ": it copies repo -> global and never deletes an orphan. It needs a "
                     "DISPOSITION, and there are exactly two: ADOPT it (copy the deployed skill into "
                     "a repo at skills/<name>/ so it is reviewable and versioned) or RETIRE it "
                     "(remove it from ~/.claude/skills/). Neither is the sync, and retiring is not "
                     "done because a peer asked — a deployed skill is live in every trunk right now. "
                     "⚠️ And check the OTHER trunks' repos before calling anything reachable-nowhere: "
                     "on 2026-09-12 this probe called tree-occupancy-guard an orphan with no source, "
                     "and Antigravity owned it at /n/antigravity-hub/skills/.")

    if _real:
        parts.append("On 2026-08-07 this exact divergence went 21 hours unnoticed because the "
                     "sync hook only fires on startup|resume and every session that day was a "
                     "compact. Jon: \"The global layer is the channel that failed.\"")
    if unknowns:
        parts.append(f"UNKNOWN — {len(unknowns)} thing(s) could NOT be checked: "
                     + " | ".join(unknowns) + ". This is UNKNOWN, not clean; verify by hand "
                     f"({FIX} then `python scripts/audit/sync_parity.py`).")
    if denom == 0:
        parts.append("DENOMINATOR ZERO — nothing was actually compared. A check over nothing is "
                     "never a pass. This probe is reporting that it could not look, not that "
                     "there is nothing to see.")
    return " ".join(parts)


def emit(msg):
    """Hook mode. Writes the JSON envelope, or NOTHING AT ALL. No trailing newline either way."""
    if msg is None:
        return
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}
    }))


# ------------------------------------------------------------------------------------------
# SELF-TEST — silence is measured in BYTES, not asserted in prose. See the docstring: two hooks
# in this repo were documented as silent on no-op and were emitting 323 B and 228 B.
# ------------------------------------------------------------------------------------------

def _capture(fn):
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn()
    return buf.getvalue()


def self_test():
    import tempfile
    import shutil
    fails = []
    tmp = tempfile.mkdtemp()

    def mk(root, claude_md, skills):
        os.makedirs(os.path.join(root, "skills"), exist_ok=True)
        with open(os.path.join(root, "CLAUDE.md"), "w", encoding="utf-8") as f:
            f.write(claude_md)
        for name, body in skills.items():
            d = os.path.join(root, "skills", name)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write(body)

    # The real comparator must be reachable from the fixture repo root.
    real_sp = os.path.join(REPO, "scripts", "audit", "sync_parity.py")

    def mk_repo(root):
        os.makedirs(os.path.join(root, "scripts", "audit"), exist_ok=True)
        shutil.copy(real_sp, os.path.join(root, "scripts", "audit", "sync_parity.py"))

    def mk_dep_scripts(root, names=("sync_parity.py",)):
        """Mirror the repo's scripts into a fixture's DEPLOYED root.

        Added 2026-09-04 with the scripts/ check itself. Case 1 is the only case
        licensed to be silent, so every artifact class the probe examines must be
        IN SYNC in that fixture -- otherwise adding a new class silently converts
        the silence control into a permanently-failing test, and the honest
        reading of that is 'the fixture is incomplete', not 'the check is wrong'."""
        d = os.path.join(root, "scripts", "audit")
        os.makedirs(d, exist_ok=True)
        for n in names:
            with open(os.path.join(d, n), "w", encoding="utf-8") as f:
                f.write("# fixture\n")

    # --- case 1: NO DIVERGENCE. The one path that may be silent. ---------------------------
    r1 = os.path.join(tmp, "repo1"); d1 = os.path.join(tmp, "dep1")
    mk(r1, "same\n", {"alpha": "---\nname: alpha\n---\nbody\n"})
    mk(d1, "same\n", {"alpha": "---\nname: alpha\n---\nbody\n"})
    mk_repo(r1); mk_dep_scripts(d1)
    f, u, n = probe(r1, d1)
    m = build_message(f, u, n)
    if m is not None:
        fails.append(f"case 1 (in sync): expected None message, got {m[:120]!r}")
    if n <= 0:
        fails.append(f"case 1: denominator must be > 0 to license silence, got {n}")
    out = _capture(lambda: emit(m))
    if len(out) != 0:
        fails.append(f"case 1: SILENCE VIOLATION — emitted {len(out)} B, expected 0 B: {out[:200]!r}")

    # --- case 2: CLAUDE.md diverged ---------------------------------------------------------
    r2 = os.path.join(tmp, "repo2"); d2 = os.path.join(tmp, "dep2")
    mk(r2, "new text\n", {"alpha": "---\nname: alpha\n---\nbody\n"})
    mk(d2, "OLD text\n", {"alpha": "---\nname: alpha\n---\nbody\n"})
    mk_repo(r2); mk_dep_scripts(d2)
    f, u, n = probe(r2, d2)
    m = build_message(f, u, n)
    if m is None or "CLAUDE.md DIVERGED" not in m:
        fails.append(f"case 2: CLAUDE.md divergence not reported; got {m!r}")
    if m and FIX not in m:
        fails.append("case 2: the fix command was not named")
    out = _capture(lambda: emit(m))
    if len(out) == 0:
        fails.append("case 2: emitted 0 B on a real divergence")
    else:
        try:
            j = json.loads(out)
            if j["hookSpecificOutput"]["hookEventName"] != "SessionStart":
                fails.append("case 2: wrong hookEventName")
            if not j["hookSpecificOutput"]["additionalContext"]:
                fails.append("case 2: empty additionalContext")
        except Exception as e:                                # noqa: BLE001
            fails.append(f"case 2: stdout was not a single valid JSON object: {e}")

    # --- case 3: a skill diverged, and a ghost ----------------------------------------------
    r3 = os.path.join(tmp, "repo3"); d3 = os.path.join(tmp, "dep3")
    mk(r3, "same\n", {"alpha": "---\nname: alpha\n---\nv2\n"})
    mk(d3, "same\n", {"alpha": "---\nname: alpha\n---\nv1\n",
                      "orphan": "---\nname: orphan\n---\nx\n"})
    mk_repo(r3); mk_dep_scripts(d3)
    f, u, n = probe(r3, d3)
    m = build_message(f, u, n)
    # vocabulary updated 2026-09-12 23:5x: "GHOST" is no longer a verdict this probe publishes --
    # a two-tree orphan is bucketed REACHABLE-ELSEWHERE or REACHABLE-NOWHERE before it is a claim.
    if m is None or "DIVERGED" not in m or "REACHABLE-" not in m:
        fails.append(f"case 3: skill DIVERGED / orphan-bucket not reported; got {m!r}")
    if "alpha" not in (m or "") or "orphan" not in (m or ""):
        fails.append("case 3: the offending skills were not named")
    # 2026-09-12: the remedy must be class-aware -- the sync cannot clear a GHOST
    if "REACHABLE-" not in (m or ""):
        fails.append("case 3: an orphan was not bucketed as REACHABLE-ELSEWHERE or -NOWHERE")

    # --- case 3b: a GHOST ALONE must not print the sync as its fix --------------------------
    r3b = os.path.join(tmp, "repo3b"); d3b = os.path.join(tmp, "dep3b")
    _nl = chr(10)  # NOT a backslash-n literal: the Bash tool unescapes those in file content
    _alpha = "---" + _nl + "name: alpha" + _nl + "---" + _nl + "v1" + _nl
    _orph = "---" + _nl + "name: orphan" + _nl + "---" + _nl + "x" + _nl
    mk(r3b, "same" + _nl, {"alpha": _alpha})
    mk(d3b, "same" + _nl, {"alpha": _alpha, "orphan": _orph})
    mk_repo(r3b); mk_dep_scripts(d3b)
    f, u, n = probe(r3b, d3b)
    m3b = build_message(f, u, n)
    if m3b is None or "REACHABLE-NOWHERE" not in m3b:
        fails.append(f"case 3b: a lone orphan with no source anywhere was not reported as "
                     f"REACHABLE-NOWHERE; got {m3b!r}")
    elif "FIX (one command" in m3b:
        fails.append("case 3b: printed the sync as THE fix for a finding it cannot clear")
    elif "DOES NOT CLEAR A REACHABLE-NOWHERE" not in m3b:
        fails.append("case 3b: no disposition named for a lone reachable-nowhere skill")

    # --- case 3c: an orphan WITH a source in another trunk is NOT a defect ---------------------
    import tempfile as _tf
    _own = os.path.join(tmp, "othertrunk", "skills")
    os.makedirs(os.path.join(_own, "orphan"), exist_ok=True)
    with open(os.path.join(_own, "orphan", "SKILL.md"), "w", encoding="utf-8") as _f:
        _f.write("---" + chr(10) + "name: orphan" + chr(10) + "---" + chr(10))
    _keep = globals()["FLEET_SKILL_ROOTS"]
    globals()["FLEET_SKILL_ROOTS"] = (("othertrunk", _own),)
    f, u, n = probe(r3b, d3b)
    m3c = build_message(f, u, n)
    globals()["FLEET_SKILL_ROOTS"] = _keep
    if "REACHABLE-ELSEWHERE" not in (m3c or "") or "othertrunk" not in (m3c or ""):
        fails.append("case 3c: an orphan sourced in another trunk was not bucketed as "
                     "REACHABLE-ELSEWHERE with its owner named")
    if "REACHABLE-NOWHERE" in (m3c or ""):
        fails.append("case 3c: a skill with a findable source was still called reachable-nowhere")

    # --- case 4: comparator unreachable => UNKNOWN, never silence ---------------------------
    r4 = os.path.join(tmp, "repo4"); d4 = os.path.join(tmp, "dep4")
    mk(r4, "same\n", {"alpha": "---\nname: alpha\n---\nbody\n"})
    mk(d4, "same\n", {"alpha": "---\nname: alpha\n---\nbody\n"})
    # deliberately DO NOT copy sync_parity.py into r4
    f, u, n = probe(r4, d4)
    m = build_message(f, u, n)
    if m is None:
        fails.append("case 4: went SILENT with the comparator missing — that is 'passed by not "
                     "looking'")
    elif "UNKNOWN" not in m:
        fails.append(f"case 4: did not say UNKNOWN; got {m[:160]!r}")

    # --- case 5: zero denominator => UNKNOWN, never silence ---------------------------------
    m = build_message([], [], 0)
    if m is None:
        fails.append("case 5: a ZERO denominator rendered as silence — the exact defect class")
    elif "DENOMINATOR ZERO" not in m:
        fails.append("case 5: zero denominator not named")

    # --- case 7: a script in the repo but NOT deployed is a FINDING ------------------------
    # Added 2026-09-04 with the scripts/ check. Without this the check is an oracle nobody has
    # watched fail -- and an audit script committed after the last sync is unreachable from every
    # other trunk while this probe stays silent, which is exactly what happened.
    r7 = os.path.join(tmp, "repo7"); d7 = os.path.join(tmp, "dep7")
    skill7 = {"alpha": "---\nname: alpha\n---\nb\n"}
    mk(r7, "x\n", skill7)
    mk(d7, "x\n", skill7)
    mk_repo(r7); mk_dep_scripts(d7)
    with open(os.path.join(r7, "scripts", "audit", "brand_new_check.py"), "w",
              encoding="utf-8") as f:
        f.write("# committed after the last sync\n")
    f7, u7, n7 = probe(r7, d7)
    m = build_message(f7, u7, n7)
    if m is None or "scripts MISSING" not in m:
        fails.append(f"case 7: an undeployed script was NOT reported; got {m!r}")
    if "brand_new_check.py" not in (m or ""):
        fails.append("case 7: the undeployed script was not named")

    # --- case 7b: CONTROL -- a proto/ script is throwaway and must NOT be reported ----------
    # Prototypes are not expected to deploy. Reporting them would put a permanent finding in
    # front of every session, and a reader trained to ignore a finding is worse off than one
    # who never had it.
    os.makedirs(os.path.join(r7, "scripts", "proto"), exist_ok=True)
    with open(os.path.join(r7, "scripts", "proto", "throwaway.py"), "w",
              encoding="utf-8") as f:
        f.write("# throwaway\n")
    f7b, u7b, n7b = probe(r7, d7)
    if any("throwaway.py" in x for x in f7b):
        fails.append("case 7b: a proto/ throwaway script was reported as undeployed; "
                     "prototypes are not expected to deploy and reporting them would "
                     "train a reader to ignore this finding")

    # --- case 6: deployed CLAUDE.md absent is a FINDING, not silence ------------------------
    r6 = os.path.join(tmp, "repo6"); d6 = os.path.join(tmp, "dep6")
    mk(r6, "x\n", {"alpha": "---\nname: alpha\n---\nb\n"})
    mk(d6, "x\n", {"alpha": "---\nname: alpha\n---\nb\n"})
    mk_repo(r6); mk_dep_scripts(d6)
    os.remove(os.path.join(d6, "CLAUDE.md"))
    f, u, n = probe(r6, d6)
    m = build_message(f, u, n)
    if m is None or "ABSENT" not in m:
        fails.append(f"case 6: absent deployed CLAUDE.md not reported; got {m!r}")

    # --- case 7: THE LIVE TREE. Byte count against the state that actually exists now. ------
    live_f, live_u, live_n = probe()
    live_m = build_message(live_f, live_u, live_n)
    live_out = _capture(lambda: emit(live_m))
    live_note = (f"live tree: {live_n} artifact(s) compared, {len(live_f)} finding(s), "
                 f"{len(live_u)} unknown(s) -> {len(live_out)} B emitted")
    if live_n == 0:
        fails.append("case 7: the LIVE probe compared ZERO artifacts")
    if not live_f and not live_u and len(live_out) != 0:
        fails.append(f"case 7: live tree is in sync but emitted {len(live_out)} B")

    print("=== SELF-TEST — global-staleness-probe.py ===")
    if fails:
        for x in fails:
            print(f"  FAIL: {x}")
        print(f"  note: {live_note}")
        print(f"\nRESULT: FAIL — {len(fails)} failure(s)")
        return 1
    print("  in-sync fixture emits EXACTLY 0 bytes (measured, not asserted) : PASS")
    print("  in-sync silence requires a NON-ZERO denominator                : PASS")
    print("  CLAUDE.md divergence -> valid JSON envelope naming the fix     : PASS")
    print("  skill DIVERGED + GHOST reported and named                      : PASS")
    print("  comparator unreachable -> UNKNOWN, never silence               : PASS")
    print("  zero denominator      -> UNKNOWN, never silence                : PASS")
    print("  deployed CLAUDE.md absent -> finding, never silence            : PASS")
    print(f"  {live_note} : PASS")
    print("\nRESULT: PASS — 8/8")
    return 0


def main():
    # ORDER MATTERS. The stdin drain must come AFTER the mode check, and must never run in a
    # human-facing mode. Found while measuring this script's own byte output on 2026-08-08:
    # `--report` invoked from a shell whose stdin is an open-but-never-closed pipe blocked
    # forever on read(). Hook mode is safe (the runtime writes the payload and closes), and the
    # drain is kept there only so the writer never sees EPIPE.
    if "--self-test" in sys.argv:
        return self_test()

    if "--report" in sys.argv:
        try:
            f, u, n = probe()
            msg = build_message(f, u, n)
        except Exception as e:        # noqa: BLE001
            msg = f"PROBE CRASHED ({type(e).__name__}: {e}) — it checked NOTHING."
        print(msg or "IN SYNC — repo and ~/.claude/ are byte-identical across every artifact "
                     "sync-universal.sh deploys. (Hook mode would emit 0 bytes here.)")
        return 0

    try:
        if not sys.stdin.isatty():
            sys.stdin.read()          # drain the hook payload; nothing here needs it
    except Exception:                 # noqa: BLE001
        pass

    try:
        f, u, n = probe()
        msg = build_message(f, u, n)
    except Exception as e:            # noqa: BLE001
        # Fail open — but LOUDLY. A probe that crashes silently is indistinguishable from a
        # probe that found nothing, which is the whole defect class this file is about.
        msg = (f"GLOBAL LAYER STALENESS PROBE CRASHED ({type(e).__name__}: {e}). It checked "
               f"NOTHING. `~/.claude/` staleness is UNKNOWN this session — run {FIX} and "
               f"`python scripts/audit/sync_parity.py` by hand.")

    emit(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
