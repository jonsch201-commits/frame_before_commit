#!/usr/bin/env python3
"""session_finalise.py — FINALISE every subagent extract of a session. The fixed point.

WHY THIS EXISTS — `SubagentStop` HAS NO FIXED POINT
----------------------------------------------------
`scripts/audit/agent_end_ingest.py` runs I0/I1 on `SubagentStop`. **Routing a return is itself a
return.** When an agent routes or reports its own return, `SubagentStop` fires again, the agent's
transcript is now longer, the ingest sees new bytes, and it emits a fresh extract with a higher turn
count. Measured 2026-08-06 on one agent: **101 turns at return 2, 135 at return 3.**

So the committed extract can never be the final one. HEAD carries one count, disk holds another, and
re-committing to close the gap generates the next mismatch. `exchange/ROUTING-LEDGER.md` ("The
self-routing stopping rule") held the line by DECLARATION: record once, mark terminal, do not chase.
A declaration is not a fixed point; it is an agreement to stop looking.

WHY THIS IS AN ADDITION AND NOT A MOVE
---------------------------------------
The recommendation on record was *"move the ingest to parent-session close instead of
`SubagentStop`."* That does give a real fixed point — **and it trades away the property
`SubagentStop` was chosen for: capture at agent end survives a session that never closes cleanly.**
This repo has lost records exactly that way (26 JSONLs, permanently; `cleanupPeriodDays`). Trading
one for the other is a decision, not a cleanup, and the decision here is **not to trade.**

  `SubagentStop`  -> I0/I1, `extract_status: PROVISIONAL`. Cheap, idempotent, crash-resilient.
                     Explicitly a mid-flight snapshot, and the artifact says so in a banner.
  `SessionEnd`    -> THIS SCRIPT. `extract_status: FINAL`. Every subagent of the ended session is
                     re-extracted when it is genuinely final, and stamped terminal.

WHICH HOOK, AND WHY IT IS `SessionEnd` RATHER THAN `Stop` OR `PreCompact`
-------------------------------------------------------------------------
Verified 2026-08-06 against https://code.claude.com/docs/en/hooks, not assumed:

* **`Stop` — fires once per TURN** ("when Claude finishes responding"; the cadence section lists it
  under *once per turn*). A session has many turns and an agent can be resumed by `SendMessage`
  after any of them, so a `Stop` fire proves nothing about finality. Worse, `Stop` accepts
  `hookSpecificOutput.additionalContext` **and can block** (exit 2 -> "prevents Claude from
  stopping"), so a finaliser there would inject text into the main thread on every turn. **Rejected.**
* **`PreCompact` — fires at a compact boundary**, matchers `manual|auto`, and a session may compact
  many times. After a compact the session CONTINUES and its agents can still be resumed. It is a
  checkpoint, not an end. It can also block compaction on exit 2. **Rejected as the finality
  carrier** (it stays wired for its existing job).
* **`SessionEnd` — fires "when a session terminates"**, matchers
  `clear|resume|logout|prompt_input_exit|bypass_permissions_disabled|other`. At that moment no
  subagent of the session can be resumed, so every subagent transcript is final. Two further
  properties make it the right carrier rather than merely the closest-looking one:
  **(a) it has NO decision control and its output is used for side effects only — nothing it emits
  is injected into anyone's context**, which structurally removes the hook-spam class that destroyed
  four agents' returns on 2026-08-06; and **(b) it cannot block** (exit 2 -> "shows stderr to user
  only"), so a slow or broken finaliser cannot wedge a session close.

**THE HONEST LIMIT, STATED RATHER THAN GLOSSED.** `SessionEnd` is a fixed point for a session that
*terminates through the harness*. The docs enumerate the reasons it fires; **they do not state that
it fires on a process kill, a crash, or a closed window, and I did not verify those cases —
UNKNOWN.** That residue is exactly why `SubagentStop` keeps its provisional capture and why
`--stale-sessions` exists below: a session that dies without firing `SessionEnd` still has every
agent captured provisionally, and a later run finalises it by AGE instead of by event. The chain is
belt-and-braces on purpose; neither leg is sufficient alone.

COST CONTROL — THIS IS A DRIVE-MOUNTED REPO
--------------------------------------------
"Re-extract everything at every close" would be unaffordable and would also rewrite hundreds of
tracked files for nothing. Three guards, in cost order:

 1. A **finalisation marker** keyed on `(agent_id, jsonl size, jsonl mtime)`. Same bytes as the last
    finalisation -> skipped on a `stat()`, no read, no convert, no write.
 2. If the marker is missing (it lives in gitignored state, so a fresh clone has none), the
    **tracked extract itself** is consulted: `extract_status: FINAL` plus matching `jsonl_size` /
    `jsonl_mtime` frontmatter is equally good evidence. The durable artifact is the fallback for the
    ephemeral one, never the other way round.
 3. A **time budget**. Whatever it does not reach is **reported as DEFERRED with a count**, never
    dropped silently — a partial run that looks complete is this repo's recorded failure mode.

NO DESTRUCTIVE ACTS — Jon's standing constraint, his words. This script reads `~/.claude/projects/`
and writes nothing there, ever. It deletes nothing anywhere.

Usage:
  session_finalise.py                          # hook mode: SessionEnd payload on stdin
  session_finalise.py --session <uuid|uuid6>   # foreground finalisation of one session
  session_finalise.py --session <id> --dry-run # report what would change; writes nothing
  session_finalise.py --stale-sessions [--older-than-hours N]
                                               # catch-up for sessions that never fired SessionEnd
  session_finalise.py --self-test              # negative controls
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_HERE = Path(__file__).resolve().parent
_SCRIPTS = _HERE.parent
for _p in (str(_SCRIPTS), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# REUSE, NOT REIMPLEMENTATION. Every extraction decision, path derivation and idempotence rule below
# belongs to agent_end_ingest / extract_claude_code_sessions. Two implementations of "where does this
# extract go" is the divergence defect this repo spent the week removing.
import agent_end_ingest as AEI                      # noqa: E402
import extract_claude_code_sessions as X            # noqa: E402

# NOTE 2026-09-04: REPO is bound here and USED BY NOTHING in this module -- every path this script
# writes is derived through AEI, whose root was corrected the same day to prefer CLAUDE_PROJECT_DIR
# over the G: corpus clone (agent_end_ingest.py:172; see
# wiki/references/claude-code/FINDING-chained-hooks-share-one-stdin-2026-09-04.md).
# Kept rather than deleted because a selftest case name used to cite it -- but it is INERT, and
# anything added here that WRITES A TRACKED PATH must use CLAUDE_PROJECT_DIR, never X.ROOT.
REPO = Path(X.ROOT)
PROJECTS_ROOT = X.PROJECTS_ROOT
STATE_DIR = AEI.STATE_DIR
RUN_LOG = STATE_DIR / "finalisation.log"
# CODE_ROOT follows the CHECKOUT (same split as extract_claude_code_sessions.py's ROOT/CODE_ROOT).
# It is what makes the ledger writable when the corpus ROOT is the thing that is broken.
CODE_ROOT = _SCRIPTS.parent
REFUSE_CODES = X.ROOT_REFUSE_CODES

DEFAULT_BUDGET_S = 240.0          # SessionEnd cannot block, but it should not run unbounded either
DEFAULT_STALE_HOURS = 12.0
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                     r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


# ---------------------------------------------------------------------------------------------
# Locating the session's subagents
# ---------------------------------------------------------------------------------------------
def session_dirs_for(session_id):
    """Every `<proj>/<session_id>/` directory on disk for this id. Usually one.

    Not one path guessed from `cwd`: the same session id appears under exactly one project dir, but
    deriving that dir from `cwd` would break for a worktree, and a wrong guess would silently
    finalise nothing while reporting success.
    """
    out = []
    if not session_id:
        return out
    try:
        for proj in PROJECTS_ROOT.iterdir():
            if not proj.is_dir():
                continue
            d = proj / session_id
            if d.is_dir():
                out.append(d)
    except OSError:
        pass
    return out


def resolve_session_id(payload):
    """(session_id, how). Prefers the explicit field; falls back to the transcript path stem."""
    if isinstance(payload, dict):
        for k in ("session_id", "sessionId"):
            v = payload.get(k)
            if isinstance(v, str) and v:
                return v, f"payload.{k}"
        tp = payload.get("transcript_path") or payload.get("transcriptPath")
        if isinstance(tp, str) and tp:
            stem = Path(tp).stem
            if UUID_RE.match(stem):
                return stem, "transcript_path stem"
    return None, "no session id on the payload"


def expand_session_arg(arg):
    """Accept a full uuid or a 6-char prefix. A prefix matching several sessions is an ERROR, not a
    silent pick — finalising the wrong session would stamp someone else's extracts terminal."""
    if UUID_RE.match(arg or ""):
        return arg, ""
    hits = set()
    try:
        for proj in PROJECTS_ROOT.iterdir():
            if not proj.is_dir():
                continue
            for d in proj.iterdir():
                if d.is_dir() and d.name.startswith(arg) and UUID_RE.match(d.name):
                    hits.add(d.name)
    except OSError:
        pass
    if len(hits) == 1:
        return hits.pop(), ""
    if not hits:
        return None, f"no session directory starts with {arg!r}"
    return None, f"ambiguous — {len(hits)} sessions start with {arg!r}: {sorted(hits)}"


def subagent_jsonls(session_dir):
    d = session_dir / "subagents"
    if not d.is_dir():
        return []
    return sorted(p for p in d.glob("agent-*.jsonl") if p.is_file())


# ---------------------------------------------------------------------------------------------
# The "nothing changed" test — guards 1 and 2 from the header
# ---------------------------------------------------------------------------------------------
def final_marker_path(agent_id):
    return STATE_DIR / f"{agent_id}.final.json"


def already_final(t):
    """(bool, evidence). True only when THESE EXACT BYTES were already finalised.

    Two independent sources, checked cheapest-first. The gitignored marker is fast; the TRACKED
    extract's own frontmatter is durable. A fresh clone has no markers, and re-finalising 300
    unchanged extracts because the ephemeral cache was missing would rewrite 300 tracked files for
    nothing — so the durable artifact backs up the cache.
    """
    key_raw, _ = AEI.ingest_key(t)
    try:
        rec = json.loads(final_marker_path(t["agent_id"]).read_text(encoding="utf-8"))
        if rec.get("key") == key_raw and rec.get("stage") == AEI.STAGE_FINAL:
            return True, f"marker {rec.get('finalised_utc', '?')}"
    except Exception:
        pass
    for p in X.existing_subagent_mds(t["parent_uuid"], t["agent_id"]):
        i1 = AEI.I1_ROOT / t["parent6"] / (p.name[:-3] + ".i1.md")
        if not i1.exists():
            continue
        if (AEI.read_i1_field(i1, "extract_status") == AEI.STAGE_FINAL
                and AEI.read_i1_field(i1, "jsonl_size") == str(t["size"])
                and AEI.read_i1_field(i1, "jsonl_mtime") == str(t["mtime"])):
            return True, f"extract frontmatter ({i1.name})"
    return False, ""


def write_final_marker(t, detail):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    key_raw, keyhash = AEI.ingest_key(t)
    rec = {"agent_id": t["agent_id"], "key": key_raw, "keyhash": keyhash,
           "stage": AEI.STAGE_FINAL,
           "finalised_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    rec.update(detail or {})
    p = final_marker_path(t["agent_id"])
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, p)


def prior_extract_state(t):
    """(i1_path_or_None, status, turn_count_or_None) BEFORE this run touches anything.

    This is what makes "how many extracts changed provisional->final, and by how many turns" a
    measurement instead of an assertion.
    """
    for p in X.existing_subagent_mds(t["parent_uuid"], t["agent_id"]):
        i1 = AEI.I1_ROOT / t["parent6"] / (p.name[:-3] + ".i1.md")
        if i1.exists():
            tc = AEI.read_i1_field(i1, "turn_count")
            try:
                tc = int(tc)
            except (TypeError, ValueError):
                tc = None
            return i1, (AEI.read_i1_field(i1, "extract_status") or "UNSTAGED"), tc
    return None, "ABSENT", None


# ---------------------------------------------------------------------------------------------
# Finalisation
# ---------------------------------------------------------------------------------------------
def finalise_session(session_id, dry_run=False, budget_s=DEFAULT_BUDGET_S, verbose=False):
    """Returns a result dict. NEVER raises — every path is caught and reported."""
    started = time.time()
    res = {"session": session_id, "session_dirs": [], "considered": 0, "skipped_unchanged": 0,
           "finalised": 0, "new_extracts": 0, "promoted_only": 0, "content_changed": 0,
           "turn_deltas": [], "failed": [], "deferred": 0, "dry_run": dry_run, "rows": []}

    dirs = session_dirs_for(session_id)
    res["session_dirs"] = [str(d) for d in dirs]
    if not dirs:
        res["failed"].append(("-", f"no session directory found for {session_id}"))
        return res

    targets = []
    for d in dirs:
        targets.extend(subagent_jsonls(d))
    res["considered"] = len(targets)

    for jsonl in targets:
        if time.time() - started > budget_s:
            # DEFERRED IS COUNTED, NEVER DROPPED. A partial run that reports like a complete one is
            # the exact defect class this whole chain exists to catch.
            res["deferred"] += 1
            continue
        try:
            t, why = AEI.resolve_from_jsonl(jsonl)
            if t is None:
                res["failed"].append((jsonl.name, why))
                continue

            ok, evidence = already_final(t)
            if ok:
                res["skipped_unchanged"] += 1
                continue

            prior_path, prior_status, prior_turns = prior_extract_state(t)

            if dry_run:
                res["rows"].append({"id6": t["agent6"], "prior_status": prior_status,
                                    "prior_turns": prior_turns, "post_turns": None,
                                    "delta": None, "action": "would-finalise"})
                res["finalised"] += 1
                continue

            status, msg, detail = AEI.ingest(t, force=True, stage=AEI.STAGE_FINAL)
            if status != "OK":
                res["failed"].append((t["agent6"], f"{status}: {msg}"))
                continue

            post_turns = detail.get("turns")
            write_final_marker(t, {"turns": post_turns, "i1": detail.get("i1"),
                                   "prior_status": prior_status, "prior_turns": prior_turns})
            res["finalised"] += 1

            if prior_path is None:
                action = "NEW — no provisional extract existed"
                res["new_extracts"] += 1
            elif prior_turns is not None and post_turns is not None and post_turns != prior_turns:
                action = "CONTENT CHANGED"
                res["content_changed"] += 1
                res["turn_deltas"].append((t["agent6"], prior_turns, post_turns))
            elif detail.get("write") == "unchanged":
                action = "unchanged"
            else:
                action = "promoted (same turns, status flipped)"
                res["promoted_only"] += 1

            res["rows"].append({"id6": t["agent6"], "prior_status": prior_status,
                                "prior_turns": prior_turns, "post_turns": post_turns,
                                "delta": (None if prior_turns is None or post_turns is None
                                          else post_turns - prior_turns),
                                "action": action,
                                "role": (t["meta"].get("agentType") or "UNKNOWN"),
                                "desc": (t["meta"].get("description") or "UNKNOWN")})
            if verbose:
                print(f"  [{action:<34}] {t['agent6']} "
                      f"{prior_status}->{AEI.STAGE_FINAL} "
                      f"turns {prior_turns}->{post_turns}")
        except Exception as e:                                   # never let one agent kill the run
            # TOLERANCE KEPT, SILENCE REMOVED (2026-08-08). The guard stays exactly as it was —
            # one bad agent must not stop the other sixty. What changed is that the failure now
            # lands in a durable ledger row instead of living only in a dict that the HOOK path
            # never prints. Only `--session` (foreground) ever rendered `res["failed"]`.
            res["failed"].append((jsonl.name, f"{e.__class__.__name__}: {e}"))
            log_failure("extract", jsonl.name, f"{e.__class__.__name__}: {e}",
                        session_id=session_id, target=str(AEI.I1_ROOT))

    res["elapsed_s"] = round(time.time() - started, 2)
    return res


# ---------------------------------------------------------------------------------------------
# The durable record
# ---------------------------------------------------------------------------------------------
_REPORT_VOLATILE = re.compile(r"^(?:finalised_utc|report_content_sha256|elapsed_s):.*\r?\n",
                              re.MULTILINE)


def _report_hash(text):
    import hashlib
    return hashlib.sha256(_REPORT_VOLATILE.sub("", text).encode("utf-8")).hexdigest()


def write_report(res):
    """One TRACKED page per session listing which extracts are terminal. Rewritten in place.

    Content-stable for the same reason `build_i1` is: this path is tracked, `SessionStart` runs
    `git pull --ff-only`, and a file that changes on every run shows permanently `M` and aborts the
    pull. Identical content -> no write at all.
    """
    parent6 = res["session"][:6]
    out_dir = AEI.I1_ROOT / parent6
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = sorted(res["rows"], key=lambda r: r["id6"])

    b = []
    a = b.append
    a("---\n")
    a(f"title: \"Finalisation record — session {parent6}\"\n")
    a("source_kind: tracker\n")
    a(f"retrieval_key: agent-end-finalisation-{parent6}\n")
    a("tags: agent-end, I1, finalisation, subagent, record-architecture\n")
    a("coverage_class: untraced-by-design\n")
    a("coverage_class_reason: mechanical finalisation record written automatically at SessionEnd; "
      "it makes no citable claim of its own\n")
    a(f"parent_session: {res['session']}\n")
    a(f"subagents_considered: {res['considered']}\n")
    a(f"finalised_this_run: {res['finalised']}\n")
    a(f"skipped_already_final: {res['skipped_unchanged']}\n")
    a(f"deferred_budget: {res['deferred']}\n")
    a(f"failed: {len(res['failed'])}\n")
    a(f"finalised_utc: {now}\n")
    a("produced_by: scripts/audit/session_finalise.py (SessionEnd, automatic)\n")
    a("---\n\n")
    a(f"# Finalisation record — session `{res['session']}`\n\n")
    a("**Every extract listed here is `extract_status: FINAL`.** It was rebuilt after the parent "
      "session terminated, when no subagent of it could be resumed, so the transcripts behind these "
      "extracts cannot grow further. **This is the fixed point that `SubagentStop` does not have** "
      "— routing a return is itself a return, so a `SubagentStop` extract is always a mid-flight "
      "snapshot (measured 2026-08-06 on one agent: 101 turns at return 2, 135 at return 3). See "
      "`exchange/ROUTING-LEDGER.md`.\n\n")
    a(f"- subagent transcripts considered: **{res['considered']}**\n")
    a(f"- finalised on this run: **{res['finalised']}**"
      f" (new extracts that never existed provisionally: **{res['new_extracts']}**;"
      f" content changed since the provisional: **{res['content_changed']}**;"
      f" promoted with identical turn count: **{res['promoted_only']}**)\n")
    a(f"- skipped, already final at these exact bytes: **{res['skipped_unchanged']}**\n")
    a(f"- **DEFERRED (time budget): {res['deferred']}** — these are still PROVISIONAL. A deferral "
      f"is counted here rather than dropped; re-run `session_finalise.py --session {parent6}` to "
      f"clear it.\n")
    a(f"- failures: **{len(res['failed'])}**\n\n")

    if res["turn_deltas"]:
        a("## Extracts whose content changed between PROVISIONAL and FINAL\n\n")
        a("These are the ones a reader citing the provisional version would have got wrong.\n\n")
        a("| id6 | provisional turns | final turns | delta |\n|---|---|---|---|\n")
        for id6, before, after in sorted(res["turn_deltas"]):
            a(f"| {id6} | {before} | {after} | +{after - before} |\n")
        a("\n")
    else:
        a("## Extracts whose content changed between PROVISIONAL and FINAL\n\n")
        a("**None on this run.** Stated rather than omitted: where finalisation changed nothing, it "
          "bought certainty rather than content, and the cost/benefit of that is a real question "
          "for whoever reads this.\n\n")

    a("## Every subagent finalised on this run\n\n")
    if not rows:
        a("_None._\n\n")
    else:
        a("| id6 | role | description | prior status | prior turns | final turns | action |\n")
        a("|---|---|---|---|---|---|---|\n")
        for r in rows:
            a(f"| {r['id6']} | {r.get('role', '-')} | "
              f"{str(r.get('desc', '-')).replace('|', '/')[:60]} | {r['prior_status']} | "
              f"{r['prior_turns'] if r['prior_turns'] is not None else '-'} | "
              f"{r['post_turns'] if r['post_turns'] is not None else '-'} | {r['action']} |\n")
        a("\n")

    if res["failed"]:
        a("## Failures — recorded, not swallowed\n\n")
        for who, why in res["failed"]:
            a(f"- `{who}` — {why}\n")
        a("\n")

    a("## What this record does NOT claim\n\n")
    a("- That the extracts were read, ranked, or accepted. They are I1. INGEST/SKIP is I2/I3 and "
      "belongs to wiki-master in an interactive session.\n")
    a("- That `SessionEnd` always fires. The docs enumerate the reasons it fires; they do not state "
      "that it fires on a process kill or crash, and that was **not verified — UNKNOWN**. A session "
      "that dies without firing it keeps its PROVISIONAL extracts, which is why "
      "`--stale-sessions` exists as the age-based catch-up.\n")

    doc = "".join(b)
    sha = _report_hash(doc)
    doc = doc.replace(f"finalised_utc: {now}\n",
                      f"finalised_utc: {now}\nreport_content_sha256: {sha}\n", 1)
    out_path = out_dir / "_FINALISATION.md"
    try:
        if out_path.exists():
            m = re.search(r"^report_content_sha256:\s*([0-9a-f]{64})\s*$",
                          out_path.read_text(encoding="utf-8", errors="replace"), re.MULTILINE)
            if m and m.group(1) == sha:
                return out_path, "unchanged"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(doc, encoding="utf-8")
        return out_path, "written"
    except OSError as e:
        return None, f"{e.__class__.__name__}: {e}"


def _ledger_targets():
    """Ledger locations, in preference order. NEVER a path under an unusable corpus root.

    THE EXISTING CONVENTION IS REUSED, NOT REPLACED — same file name (`finalisation.log`), same
    append-a-line format, same directory when the root is healthy. Inventing a second failure
    venue is this repo's #1 defect ("a fact written down once, then diverging with nothing able to
    notice"), so there is still exactly one ledger name.

    What is new is the fallback. `STATE_DIR` is derived from the hardcoded corpus `ROOT`, so when
    the ROOT is itself the broken thing, the ledger that should record the breakage is unwritable
    too — and the old `except OSError: pass` below then swallowed the record of the swallow. Worse
    on POSIX: `STATE_DIR.mkdir(parents=True)` would have SUCCEEDED into a junk relative directory,
    writing the evidence into the same disappearing place as the transcripts. So when the
    precondition fails, the root-derived candidate is dropped entirely rather than merely
    reordered.
    """
    ok, _code, _detail = X.corpus_root_status()
    cands = ([RUN_LOG] if ok else []) + [CODE_ROOT / "raw" / "extracts" / "_state" /
                                         "finalisation.log"]
    seen, uniq = set(), []
    for p in cands:
        if str(p) not in seen:
            seen.add(str(p))
            uniq.append(p)
    return uniq


def log_run(line):
    """Append one row to the durable run/failure ledger. Returns the path written, or None.

    DURABLE FILE ONLY — never stdout, never `hookSpecificOutput.additionalContext`. Hook output
    injected into a receiving context destroyed four agent returns on 2026-08-06 and a fifth on
    08-07. The ledger row is the payload; the console is not a delivery mechanism.
    """
    row = line.rstrip("\n") + "\n"
    for p in _ledger_targets():
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "a", encoding="utf-8") as fh:
                fh.write(row)
            return p
        except OSError:
            continue
    return None


def log_failure(kind, who, detail, session_id=None, target=None):
    """One structured row per caught-and-tolerated failure. Tolerance kept, silence removed."""
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return log_run(f"{stamp} FAILURE kind={kind} session={session_id or '-'} who={who} "
                   f"target={target or '-'} detail={str(detail)[:400]!r}")


def corpus_preflight(context):
    """(may_proceed, code). Checks the corpus root BEFORE anything tries to write to it.

    This is the half of the fix that the exception handlers cannot cover: on POSIX the bad-root
    write does not throw, so there is no exception to make louder. The check has to run first.

    REFUSAL IS NARROW AND IS NOT "KILLING THE RUN". It fires only for roots that cannot possibly
    be the corpus (relative, absent, or not a directory). On Windows with a mounted G: none of
    those hold, so host behaviour is unchanged — asserted by the self-test, not by this comment.
    """
    ok, code, detail = X.corpus_root_status()
    if ok:
        return True, code
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    refuse = code in REFUSE_CODES
    p = log_run(f"{stamp} CORPUS-ROOT-UNUSABLE code={code} context={context} root={X.ROOT!s} "
                f"action={'REFUSED' if refuse else 'PROCEEDED-WITH-WARNING'} detail={detail!r}")
    # STDERR, never stdout. `SessionEnd` stdout goes to the transcript; stderr is shown to the user
    # only and is injected into no context (docs, verified 2026-08-06 — see this module's header).
    try:
        print(f"[session-finalise] CORPUS ROOT UNUSABLE ({code}). "
              f"{'REFUSED to write.' if refuse else 'Proceeding with warning.'} {detail} "
              f"Ledger: {p if p else 'UNWRITABLE — this run left no durable record'}",
              file=sys.stderr)
    except Exception:
        pass
    return (not refuse), code


# ---------------------------------------------------------------------------------------------
# Stale-session catch-up — the answer to "SessionEnd may not have fired"
# ---------------------------------------------------------------------------------------------
def stale_sessions(older_than_hours=DEFAULT_STALE_HOURS, exclude=()):
    """Sessions whose own transcript has not been touched for N hours.

    A session that crashed never fired `SessionEnd`, so its extracts stay PROVISIONAL forever. Age
    is a WEAKER signal than the event — it can be wrong about a long-idle live session — so this is
    a separate opt-in mode with a stated threshold, not something folded into the hook path.
    """
    cutoff = time.time() - older_than_hours * 3600.0
    out = []
    try:
        for proj in PROJECTS_ROOT.iterdir():
            if not proj.is_dir():
                continue
            for d in proj.iterdir():
                if not (d.is_dir() and UUID_RE.match(d.name)) or d.name in exclude:
                    continue
                if not subagent_jsonls(d):
                    continue
                conv = proj / f"{d.name}.jsonl"
                mt = conv.stat().st_mtime if conv.is_file() else max(
                    (p.stat().st_mtime for p in subagent_jsonls(d)), default=0)
                if mt < cutoff:
                    out.append((d.name, mt))
    except OSError:
        pass
    return sorted(out, key=lambda r: r[1])


# ---------------------------------------------------------------------------------------------
def summarise(res):
    return (f"{res['finalised']} finalised "
            f"({res['new_extracts']} new, {res['content_changed']} content-changed, "
            f"{res['promoted_only']} promoted), {res['skipped_unchanged']} already final, "
            f"{res['deferred']} deferred, {len(res['failed'])} failed, "
            f"{res.get('elapsed_s', 0)}s")


def hook_mode():
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception:
        pass
    try:
        payload = json.loads(raw) if raw.strip() else None
    except Exception:
        payload = None

    event = "SessionEnd"
    if isinstance(payload, dict) and isinstance(payload.get("hook_event_name"), str):
        event = payload["hook_event_name"] or event
    reason = (payload or {}).get("reason", "UNKNOWN") if isinstance(payload, dict) else "UNKNOWN"

    # BEFORE anything derives a write path from the corpus root. On POSIX the bad-root write does
    # not raise, so this check — not the `except` clauses — is what stands between a container
    # session and a transcript history that silently goes to zero.
    if not corpus_preflight(f"hook:{event}:{reason}")[0]:
        return 0

    session_id, how = resolve_session_id(payload)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not session_id:
        log_run(f"{stamp} event={event} reason={reason} NOT-RUN {how}")
        return 0

    res = finalise_session(session_id)
    ok, note = write_report(res)
    log_run(f"{stamp} event={event} reason={reason} session={session_id} "
            f"{summarise(res)} report={note}")

    # SILENCE ON NO-OP. `SessionEnd` output is documented as side-effect-only, so nothing here is
    # injected anywhere — but the discipline is kept regardless, because this script may later be
    # wired to an event whose output IS injected, and because a hook that narrates its own no-ops is
    # how four agents' returns were destroyed on 2026-08-06.
    if res["finalised"] == 0 and not res["failed"]:
        return 0
    # SCHEMA, measured by Claude Personal on our own forks 2026-08-07 and fixed here:
    #   "Hook JSON output validation failed -- (root): Invalid input"
    # The harness enumerates `additionalContext` under UserPromptSubmit / PostToolUse /
    # SessionStart ONLY. Emitting it under SessionEnd fails validation on EVERY close. It failed
    # silently -- the finalisation still happened, so nothing looked broken, which is why it took
    # another project running forks against our tree to see it.
    #
    # So: structured output only for events that accept it; plain stdout otherwise. SessionEnd
    # output is side-effect-only and goes to the transcript, which is the right place for it.
    msg = (f"[session-finalise] {summarise(res)}. Extracts for session {session_id[:6]} are now "
           f"extract_status: FINAL.")
    ACCEPTS_ADDITIONAL_CONTEXT = ("UserPromptSubmit", "PostToolUse", "SessionStart")
    try:
        if event in ACCEPTS_ADDITIONAL_CONTEXT:
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": event, "additionalContext": msg}}))
        else:
            print(msg)
    except Exception:
        pass
    return 0


# ---------------------------------------------------------------------------------------------
def self_test():
    cases = []

    # --- Resolution refuses to guess ----------------------------------------------------------
    sid, how = resolve_session_id(None)
    cases.append(("no payload -> no session id, with a reason", sid is None and "no session" in how))
    sid, how = resolve_session_id({"hook_event_name": "SessionEnd"})
    cases.append(("NEGATIVE CONTROL: payload with no id is NOT guessed from cwd",
                  sid is None))
    sid, how = resolve_session_id({"session_id": "abc"})
    cases.append(("explicit session_id is used", sid == "abc" and how == "payload.session_id"))
    sid, how = resolve_session_id(
        {"transcript_path": "/x/y/f0190965-96ce-4e41-996f-c2b8585272b2.jsonl"})
    cases.append(("transcript stem is accepted ONLY when it is a uuid",
                  sid == "f0190965-96ce-4e41-996f-c2b8585272b2"))
    sid, _ = resolve_session_id({"transcript_path": "/x/y/not-a-uuid.jsonl"})
    cases.append(("NEGATIVE CONTROL: a non-uuid transcript stem is refused", sid is None))

    # An unknown session must report failure, not report success over zero work. This is the
    # "0 UNSUPPORTED out of 0 resolvable" defect class, checked directly.
    r = finalise_session("00000000-0000-0000-0000-000000000000", dry_run=True)
    cases.append(("NEGATIVE CONTROL: unknown session FAILS rather than reporting a clean 0/0",
                  r["finalised"] == 0 and len(r["failed"]) == 1))

    # --- The provisional/final distinction is a FACT, not a label -----------------------------
    # Re-asserted here against agent_end_ingest's real hashing, because this script's whole value
    # depends on it: if promoting an extract did not change its bytes, finalisation would be a
    # no-op wearing a status field.
    prov = "---\nextract_status: PROVISIONAL\nfinalised_utc: -\n---\nbody\n"
    fin = "---\nextract_status: FINAL\nfinalised_utc: 2026-01-01T00:00:00Z\n---\nbody\n"
    cases.append(("NEGATIVE CONTROL: PROVISIONAL and FINAL of identical body hash DIFFERENTLY",
                  AEI.stable_hash(prov) != AEI.stable_hash(fin)))
    cases.append(("two finalisations of identical content hash the SAME (no tracked churn)",
                  AEI.stable_hash(fin) == AEI.stable_hash(
                      "---\nextract_status: FINAL\nfinalised_utc: 2026-12-31T23:59:59Z\n---\nbody\n")))

    # --- The report is content-stable ---------------------------------------------------------
    ra = "finalised_utc: 2026-01-01T00:00:00Z\nelapsed_s: 1\nrows\n"
    rb = "finalised_utc: 2026-09-09T09:09:09Z\nelapsed_s: 99\nrows\n"
    rc = "finalised_utc: 2026-01-01T00:00:00Z\nelapsed_s: 1\nrows CHANGED\n"
    cases.append(("report hash ignores its own timestamp and elapsed time",
                  _report_hash(ra) == _report_hash(rb)))
    cases.append(("NEGATIVE CONTROL: report hash still changes on real content change",
                  _report_hash(ra) != _report_hash(rc)))

    # --- Idempotence: the skip test is keyed on BYTES, not on status ---------------------------
    fake = {"agent_id": "z" * 17, "agent6": "zzzzzz", "size": 1, "mtime": 2,
            "parent_uuid": "0" * 36, "parent6": "000000"}
    ok, ev = already_final(fake)
    cases.append(("NEGATIVE CONTROL: an agent with no marker and no extract is NOT 'already final'",
                  ok is False))
    k1, _ = AEI.ingest_key(fake)
    k2, _ = AEI.ingest_key({**fake, "size": 2})
    cases.append(("finalisation key changes when the transcript grows", k1 != k2))

    # --- Ambiguity is an error, never a silent pick --------------------------------------------
    sid, why = expand_session_arg("zzzzzz")
    cases.append(("NEGATIVE CONTROL: an unmatched session prefix errors rather than picking one",
                  sid is None and "no session directory" in why))

    # --- NO DESTRUCTIVE ACTS ------------------------------------------------------------------
    # Checked against this module's own source: nothing here may delete, move, or write under
    # ~/.claude/projects/. A behavioural test cannot prove absence, so the check is textual and
    # says so.
    src = Path(__file__).read_text(encoding="utf-8", errors="replace")
    body = src.split("def self_test", 1)[0]
    cases.append(("no unlink/rmtree/rename/move anywhere in the operative body (textual check)",
                  not re.search(r"\b(unlink|rmtree|shutil\.move|os\.remove)\b", body)))
    # ⚠️ LABEL CORRECTED 2026-09-04. This case read "the only writes are under REPO, never
    # under ~/.claude/projects" -- and it never checked the REPO half at all. What it actually
    # asserts is the second clause only: that no write is opened against a session jsonl or
    # project path. The REPO clause was unverifiable here anyway (REPO is bound at :109 and used
    # by nothing), so the NAME promised a guarantee the CHECK could not deliver. That is the same
    # family found tonight in postcompact step 7, which printed PASS while its only input was a
    # fallback default. The assertion is unchanged; only its name now matches it.
    cases.append(("no write is ever opened against ~/.claude/projects (session jsonl / project dir)",
                  "PROJECTS_ROOT" in body and not re.search(
                      r"open\(\s*(?:str\()?\s*(?:proj|session_dir|jsonl)\b[^)]*['\"][aw]", body)))

    # --- Reuse, not reimplementation ----------------------------------------------------------
    cases.append(("finalisation delegates extraction to agent_end_ingest",
                  AEI.ingest.__module__ == "agent_end_ingest"))
    cases.append(("path derivation delegates to the canonical extractor",
                  X.CONVERTER.name == "convert-claude-code.py"))
    cases.append(("FINAL stage constant comes from agent_end_ingest, not restated here",
                  AEI.STAGE_FINAL == "FINAL"))

    # --- CORPUS ROOT PRECONDITION — the container silent-loss detector ------------------------
    from pathlib import PurePosixPath
    _ok, _code, _ = X.corpus_root_status()
    cases.append(("corpus root on THIS host passes the precondition (host behaviour unchanged)",
                  _ok and _code == X.ROOT_OK))
    _pp = PurePosixPath(str(X.ROOT))
    cases.append(("THE CONTAINER CASE: the hardcoded Windows root parses as a RELATIVE, "
                  "one-component POSIX path", (not _pp.is_absolute()) and len(_pp.parts) == 1))
    _o2, _c2, _ = X.corpus_root_status(Path(__file__).resolve().parent / "___no_such_dir___")
    cases.append(("NEGATIVE CONTROL: a missing absolute root reports MISSING, not OK",
                  (not _o2) and _c2 == X.ROOT_MISSING))
    _o3, _c3, _ = X.corpus_root_status(Path(__file__).resolve())
    cases.append(("NEGATIVE CONTROL: a FILE given as the root reports NOT_A_DIR, not OK",
                  (not _o3) and _c3 == X.ROOT_NOT_A_DIR))
    cases.append(("refusal is NARROW: only relative / missing / not-a-directory roots refuse",
                  set(REFUSE_CODES) == {X.ROOT_NOT_ABSOLUTE, X.ROOT_MISSING, X.ROOT_NOT_A_DIR}))

    # The ledger must survive the failure it exists to record.
    _saved_root = X.ROOT
    try:
        X.ROOT = Path("Z:/definitely/not/here" if os.name == "nt" else "/definitely/not/here")
        _tg = _ledger_targets()
        cases.append(("BAD ROOT: ledger drops the corpus-root copy and keeps a checkout-relative "
                      "one that is still writable",
                      len(_tg) == 1 and str(CODE_ROOT) in str(_tg[0])))
        cases.append(("BAD ROOT: preflight refuses rather than writing to nowhere",
                      X.corpus_root_status()[1] in REFUSE_CODES))
    finally:
        X.ROOT = _saved_root
    cases.append(("HEALTHY ROOT: the ledger is the EXISTING finalisation.log, not a new venue",
                  _ledger_targets()[0] == RUN_LOG and RUN_LOG.name == "finalisation.log"))

    # --- SILENCE ON NO-OP, MEASURED IN BYTES rather than asserted in a comment ----------------
    # CARRIER.md asserted two SubagentStop hooks were "silent on no-op"; when measured they
    # emitted 323 B and 228 B, and that injection destroyed four agent returns. A claim in a
    # comment is not a control. This measures stdout and carries a POSITIVE control so it cannot
    # pass by simply being broken.
    import contextlib
    import io as _io

    def _emitted(payload, res_stub):
        _stdin, _fin, _rep, _log = sys.stdin, finalise_session, write_report, log_run
        g = globals()
        g["finalise_session"] = lambda *a, **k: res_stub
        g["write_report"] = lambda res: (None, "unchanged")
        g["log_run"] = lambda line: None          # ledger writes are not what this test measures
        buf = _io.StringIO()
        try:
            sys.stdin = _io.StringIO(json.dumps(payload))
            with contextlib.redirect_stdout(buf):
                hook_mode()
        finally:
            sys.stdin = _stdin
            g["finalise_session"], g["write_report"], g["log_run"] = _fin, _rep, _log
        return buf.getvalue()

    _clean = {"session": "a" * 36, "finalised": 0, "new_extracts": 0, "content_changed": 0,
              "promoted_only": 0, "skipped_unchanged": 12, "deferred": 0, "failed": [],
              "elapsed_s": 0.1}
    _pl = {"hook_event_name": "SessionEnd", "reason": "other", "session_id": "a" * 36}
    n_noop = len(_emitted(_pl, _clean))
    n_noid = len(_emitted({"hook_event_name": "SessionEnd", "reason": "other"}, _clean))
    _work_out = _emitted(_pl, {**_clean, "finalised": 3})
    n_work = len(_work_out)
    n_fail = len(_emitted(_pl, {**_clean, "failed": [("agent-x", "OSError: nope")]}))

    cases.append((f"SILENCE MEASURED: no-op close emits {n_noop} bytes of stdout", n_noop == 0))
    cases.append((f"SILENCE MEASURED: unresolvable session emits {n_noid} bytes of stdout",
                  n_noid == 0))
    cases.append((f"POSITIVE CONTROL: real work DOES emit ({n_work} B) — the two silence "
                  "measurements above are not vacuous", n_work > 0))
    cases.append((f"a tolerated FAILURE breaks silence ({n_fail} B) rather than passing as a "
                  "clean no-op", n_fail > 0))
    cases.append(("NEGATIVE CONTROL: nothing emitted under SessionEnd is `additionalContext`",
                  "additionalContext" not in _work_out))

    print("=== SELF-TEST (negative controls included) ===")
    bad = 0
    for name, ok in cases:
        bad += 0 if ok else 1
        print(f"  {name:<78} : {'PASS' if ok else 'FAIL'}")
    print(f"\nRESULT: {'PASS' if not bad else 'FAIL'} — {len(cases) - bad}/{len(cases)}")
    return 0 if not bad else 1


def _argval(argv, flag, default=None):
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
    return default


def main():
    argv = sys.argv[1:]
    if "--self-test" in argv:
        return self_test()

    dry = "--dry-run" in argv
    budget = float(_argval(argv, "--budget-seconds", DEFAULT_BUDGET_S))

    may, root_code = corpus_preflight("foreground")
    if not may:
        print(f"NOT RUN — corpus root unusable ({root_code}). Row written to finalisation.log.",
              file=sys.stderr)
        return 0

    if "--stale-sessions" in argv:
        hours = float(_argval(argv, "--older-than-hours", DEFAULT_STALE_HOURS))
        rows = stale_sessions(hours)
        print(f"=== STALE SESSIONS (no activity for {hours}h, have subagents) — "
              f"{'DRY RUN' if dry else 'APPLY'} ===")
        print(f"DENOMINATOR: {len(rows)} session(s)")
        for sid, mt in rows:
            age_h = (time.time() - mt) / 3600.0
            res = finalise_session(sid, dry_run=dry, budget_s=budget)
            print(f"  {sid[:8]}  idle {age_h:6.1f}h  {summarise(res)}")
            if not dry:
                write_report(res)
        return 0

    if "--session" in argv:
        arg = _argval(argv, "--session", "")
        sid, why = expand_session_arg(arg)
        if sid is None:
            print(f"NOT RUN — {why}")
            return 0
        print(f"=== FINALISE session {sid} — {'DRY RUN' if dry else 'APPLY'} ===")
        res = finalise_session(sid, dry_run=dry, budget_s=budget, verbose=True)
        print("\n--- SUMMARY ---")
        print(f"  subagent transcripts considered : {res['considered']}")
        print(f"  skipped, already final          : {res['skipped_unchanged']}")
        print(f"  finalised this run              : {res['finalised']}")
        print(f"    of which NEW (no provisional) : {res['new_extracts']}")
        print(f"    of which CONTENT CHANGED      : {res['content_changed']}")
        print(f"    of which promoted, same turns : {res['promoted_only']}")
        print(f"  DEFERRED (budget)               : {res['deferred']}")
        print(f"  failed                          : {len(res['failed'])}")
        for who, why2 in res["failed"]:
            print(f"      {who}: {why2}")
        if res["turn_deltas"]:
            print("\n--- TURN DELTAS, provisional -> final ---")
            for id6, before, after in sorted(res["turn_deltas"]):
                print(f"  {id6}: {before} -> {after}  (+{after - before})")
        else:
            print("\n--- TURN DELTAS: NONE. Finalisation bought certainty, not content, "
                  "for the extracts that already existed. ---")
        if not dry:
            p, note = write_report(res)
            print(f"\nreport: {p} [{note}]")
            log_run(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") +
                    f" event=FOREGROUND session={sid} {summarise(res)} report={note}")
        return 0

    return hook_mode()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:                    # never block a session close, on any path
        try:
            log_run(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") +
                    f" CRASHED {e.__class__.__name__}: {e}")
        except Exception:
            pass
        sys.exit(0)
