#!/usr/bin/env python3
"""nightly_corpus_delta.py — Stage 1 pilot lane runner (PROPOSAL; not scheduled by this repo).

Full spec + doc citations: exchange/lanes/lane-nightly-corpus-delta.md. Leg 1 (pure Python, ZERO
tokens): --list -> {uuid6: msg-count}, diff vs prev snapshot. Leg 2 (headless, tokens ONLY on a
delta): claude -p converts the delta + opens ONE draft PR. Runner does NO git ops, NEVER calls
schtasks; reads CLAUDE_CODE_OAUTH_TOKEN only to gate (never stores/logs/emits; redacts it); no-ops
(exit 0) when token absent or KILL set. Normal mode NOT --bare (bare ignores the token); refuses if
ANTHROPIC_API_KEY set (would bill pay-per-token).

WATERMARK CONTRACT (the thing this lane must never get wrong): the snapshot advances ONLY over
sessions whose conversion the extractor itself confirms, PLUS the lane's own self-caused session
identified by exact session_id. It never advances on "the subprocess exited 0". Anything the lane
did not verify stays below the watermark and re-triggers. Absence of a ledger row means the lane
did not run, and nothing else.
"""
import json, os, re, subprocess, sys
from datetime import datetime, date
from pathlib import Path

REPO = Path(r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer")
EXTRACT = REPO / "scripts" / "extract_claude_code_sessions.py"
LEDGER = REPO / "exchange" / "lanes" / "ledger" / "nightly-corpus-delta.tsv"
# STATE_DIR off Drive (MEMORY: Drive-lag). Caps below in lane-spec units; all env-overridable.
STATE_DIR = Path(os.environ.get("CFL_LANE_STATE_DIR",
    Path(os.environ.get("LOCALAPPDATA", Path.home())) / "cfl-lanes" / "nightly-corpus-delta"))
SNAPSHOT, KILL = STATE_DIR / "snapshot.json", STATE_DIR / "KILL"
LANE_MODEL = os.environ.get("CFL_LANE_MODEL", "sonnet")
MAX_TURNS = int(os.environ.get("CFL_LANE_MAX_TURNS", "30"))
REPORT_BYTES = int(os.environ.get("CFL_LANE_REPORT_BYTES", "8192"))
MAX_SESSIONS = int(os.environ.get("CFL_LANE_MAX_SESSIONS", "25"))
WALL_SECONDS = int(os.environ.get("CFL_LANE_WALL_SECONDS", "1200"))
LINE_RE = re.compile(r"^\s+([0-9a-fA-F]{6})\s+(\d+)\s+msgs\b")
# `--update --dry-run` prints "  [EXTRACT] uuid6  (reason) ..." / "  [REFRESH] uuid6 ...".
DRYRUN_RE = re.compile(r"^\s+\[(?:EXTRACT|REFRESH)\]\s+([0-9a-fA-F]{6})\b")

# Leg 2 runs `dontAsk` (doc, permission-modes: "auto-denies every tool call that would otherwise
# prompt you ... the session never waits for input. Use this mode for CI pipelines"). Under it
# Claude runs ONLY these rules + read-only Bash, so the leg can no longer silently stall on a
# permission prompt that no human is there to answer.
ALLOWED_TOOLS = ",".join([
    "Read", "Glob", "Grep", "Write", "Edit",
    "Bash(python scripts/extract_claude_code_sessions.py *)",
    "Bash(git status *)", "Bash(git rev-parse *)", "Bash(git fetch *)", "Bash(git worktree *)",
    "Bash(git checkout *)", "Bash(git switch *)", "Bash(git add *)", "Bash(git commit *)",
    "Bash(git push *)", "Bash(git diff *)", "Bash(git log *)",
    "Bash(gh pr create *)", "Bash(gh pr view *)",
])
# Deny beats allow in every mode (doc, permissions § Manage permissions: "Rules are evaluated in
# order: deny, then ask, then allow ... rule specificity doesn't change the order"). `raw/` is
# gitignored precisely because it is Jon's full history and is NEVER pushed to GitHub (CLAUDE.md);
# a plain `git add` on it is a silent no-op, so the ONLY way it reaches a PR is a force-add. These
# rules make that mechanically impossible rather than merely un-instructed.
DENIED_TOOLS = ",".join([
    "Bash(git add -f *)", "Bash(git add --force *)", "Bash(git add *raw/*)",
    "Bash(git push * main)",
])


def _tok():
    return os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") or ""


def redact(text):
    t = _tok()
    return text.replace(t, "***REDACTED-OAUTH-TOKEN***") if (t and text) else text


def log(msg):  # stdout only; the scheduled task redirects stdout to a logfile (see PR-body command)
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {redact(msg)}", flush=True)


def leg1_manifest():
    if not EXTRACT.exists():
        return None, f"extract script not found: {EXTRACT}"
    try:
        r = subprocess.run([sys.executable, str(EXTRACT), "--list"],
                           cwd=str(REPO), capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"--list failed: {e}"
    if r.returncode != 0:
        return None, f"--list exit {r.returncode}: {redact((r.stderr or '')[:200])}"
    manifest = {m.group(1).lower(): int(m.group(2))
                for m in (LINE_RE.match(ln) for ln in r.stdout.splitlines()) if m}
    if not manifest:
        return None, "parsed 0 sessions from --list (format drift?) — failing safe, no tokens"
    return manifest, f"parsed {len(manifest)} sessions"


def leg1_pending():
    """uuid6s the extractor ITSELF still says need extraction, via its own `--update --dry-run`
    (writes nothing: the dry-run branch prints and `continue`s before any unlink/convert).

    Verification deliberately reuses the extractor's own predicate instead of re-deriving one here.
    MEMORY (detection-proxies-lie): `md✓/md✗` glyphs and --update mtime/size are NOT reliable
    signals on their own, and a second hand-rolled copy of that logic would drift from the tool it
    is supposed to be checking. "Verified" therefore means exactly: the extractor no longer asks to
    convert this session.
    """
    try:
        r = subprocess.run([sys.executable, str(EXTRACT), "--update", "--dry-run"],
                           cwd=str(REPO), capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"--update --dry-run failed: {e}"
    if r.returncode != 0:
        return None, f"--update --dry-run exit {r.returncode}: {redact((r.stderr or '')[:200])}"
    pending = {m.group(1).lower()
               for m in (DRYRUN_RE.match(ln) for ln in r.stdout.splitlines()) if m}
    return pending, f"{len(pending)} session(s) still pending conversion"


def load_snapshot():
    """(manifest, status) where status is 'absent' | 'ok' | 'corrupt: <why>'.

    A corrupt snapshot is NEVER treated as a first run. Baselining on unreadable state would write
    the whole current corpus in as "already handled" and exit 0 — silently absorbing the entire
    accumulated backlog while reporting success. The sibling lane already fails the correct way
    (transcript_corpus_diff.py load_prev_manifest: "manifest unreadable; treating all conversations
    as new"), i.e. toward reprocessing. These two now agree.
    """
    if not SNAPSHOT.exists():
        return None, "absent"
    try:
        data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, f"corrupt: {type(e).__name__}: {str(e)[:120]}"
    if not isinstance(data, dict):
        return None, "corrupt: top-level JSON is not an object"
    return data, "ok"


def write_snapshot(manifest):
    """Atomic: a kill mid-write (sleep, power loss, Task Scheduler ExecutionTimeLimit) must not be
    able to leave a truncated snapshot behind. os.replace is atomic on Windows and POSIX."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = SNAPSHOT.with_name(SNAPSHOT.name + ".tmp")
    tmp.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    os.replace(tmp, SNAPSHOT)


def compute_delta(prev, cur):
    new = sorted(u for u in cur if u not in prev)
    grown = sorted(u for u in cur if u in prev and cur[u] > prev[u])
    return new, grown


def advance_snapshot(prev, post, delta, pending, own6):
    """Build the next snapshot. Pure function — unit-testable, no I/O.

    Resolves the two requirements that used to be in tension:
      (a) advance ONLY over delta sessions the extractor confirms are converted, and
      (b) still absorb the lane's OWN self-caused session, or a quiet corpus fires the lane
          nightly forever (the real problem the old post-run rescan was solving).
    They are not actually in conflict once provenance is tracked instead of guessed: (a) is keyed
    on the extractor's pending set, (b) on the exact session_id Leg 2 reports. The old blanket
    post-run rescan conflated the two and swept in a third, unwanted class — sessions nobody
    converted, including everything past the per-night cap and any genuine concurrent Jon session
    that happened to start during the run.

    Returns (next_snapshot, verified, deferred, absorbed).
    """
    nxt = dict(prev)
    verified, deferred = [], []
    for u in delta:
        if u in post and u not in pending:
            nxt[u] = post[u]
            verified.append(u)
        else:
            deferred.append(u)          # stays at its prev value (or absent) -> re-triggers
    absorbed = []
    if own6 and own6 in post and own6 not in prev:
        # Self-caused only: it must have appeared DURING this run. Never absorb a uuid we already
        # knew about, and never absorb an arbitrary "appeared during the run" session — only the
        # one whose session_id Leg 2 itself returned.
        nxt[own6] = post[own6]
        absorbed.append(own6)
    return nxt, verified, deferred, absorbed


def build_report(new, grown, cur, prev):
    lines = [f"Corpus delta {date.today():%Y-%m-%d}: {len(new)} new, {len(grown)} grown session(s)."]
    lines += [f"  NEW   {u}  {cur[u]} msgs" for u in new[:MAX_SESSIONS]]
    lines += [f"  GROWN {u}  {prev[u]} -> {cur[u]} msgs" for u in grown[:MAX_SESSIONS]]
    report, truncated = "\n".join(lines), False
    if len(report.encode("utf-8")) > REPORT_BYTES:
        report = report.encode("utf-8")[:REPORT_BYTES].decode("utf-8", "ignore")
        report += "\n  ...(truncated at cap; omitted sessions are NOT advanced past — they stay "
        report += "below the watermark and re-trigger)"
        truncated = True
    return report, truncated


SYS_PROMPT = (  # belt-and-suspenders; non-bare leg also inherits repo .claude/agents + CLAUDE.md
    "Nightly corpus-delta executor (mechanical-extractor + intake conventions). FENCES: draft PRs "
    "ONLY, never commit/push main; worktree off Drive (Temp/claude/wt-*, core.longpaths=true, empty "
    "porcelain first); 0 deletions; credential paths read-forbidden; never echo/log any token. "
    "NEVER stage, add, or force-add anything under raw/ — it is gitignored because it is Jon's full "
    "personal history and is never pushed to GitHub; if a git add appears to do nothing on a raw/ "
    "path that is CORRECT, do not reach for -f. Do NOT ingest to wiki/ (Jon-gated) — only a "
    "ONE-LINE note in wiki/intake-triage/. Open exactly ONE draft PR (base main); print its URL "
    "last. Stop at completion; surplus is a breach."
)


def build_prompt(report):
    return ("The nightly pure-Python scan found this corpus delta:\n\n" + report + "\n\n"
            "Run `python scripts/extract_claude_code_sessions.py --update` to convert the sessions "
            "above and verify the written counts. The converted markdown lands under raw/, which is "
            "gitignored and MUST NOT be staged or pushed — leave it on disk. Then open ONE draft PR "
            f"(base main, new branch lane/nightly-{date.today():%Y%m%d}) containing ONLY a one-line "
            "intake note in wiki/intake-triage/ recording which sessions were converted. Output "
            "only the PR URL on the final line.")


def leg2_headless(report):
    from shutil import which
    claude = which("claude") or which("claude.cmd")
    if not claude:
        return {"is_error": True, "_err": "claude CLI not found on PATH"}
    # Prompt goes over STDIN, NOT argv. On Windows `claude` resolves to claude.CMD; executing a .CMD
    # routes argv through cmd.exe, which truncates a newline-containing arg at the first line and
    # mangles trailing flags (verified 2026-07-19: killed the multi-line prompt AND ate
    # --output-format json -> text output -> parse failure). Headless doc: "Non-interactive mode
    # reads stdin" and shows `gh pr diff | claude -p --append-system-prompt ...` with no positional
    # prompt (prompt supplied via stdin). Requires claude >= v2.1.211 (Windows stdin fix). Only flags
    # stay on argv here; SYS_PROMPT MUST remain single-line (no newlines) since it rides argv.
    cmd = [claude, "-p", "--output-format", "json",
           "--model", LANE_MODEL, "--max-turns", str(MAX_TURNS),
           "--permission-mode", "dontAsk",
           "--allowedTools", ALLOWED_TOOLS,
           "--disallowedTools", DENIED_TOOLS,
           "--append-system-prompt", SYS_PROMPT]
    log(f"Leg 2: claude -p (model={LANE_MODEL}, max-turns={MAX_TURNS}, wall={WALL_SECONDS}s, "
        "permission-mode=dontAsk)")
    try:
        r = subprocess.run(cmd, cwd=str(REPO), input=build_prompt(report),
                           capture_output=True, text=True, timeout=WALL_SECONDS)
    except subprocess.TimeoutExpired:
        return {"is_error": True, "_err": f"wall-clock cap {WALL_SECONDS}s exceeded (SIGTERM)"}
    except OSError as e:
        return {"is_error": True, "_err": f"spawn failed: {e}"}
    if r.returncode != 0:  # 1 = max-turns/task error, 143 = SIGTERM; stderr redacted before storage
        return {"is_error": True, "_err": f"exit {r.returncode}: {redact((r.stderr or '')[:300])}"}
    try:
        return json.loads(r.stdout)
    except ValueError:  # log redacted stdout head so the next parse failure is diagnosable
        head = redact((r.stdout or "")[:300]).replace("\n", "\\n")
        log(f"Leg 2: JSON parse failed (rc=0). stdout[:300]={head!r}")
        return {"is_error": True, "_err": "could not parse --output-format json"}


LEDGER_HEADER = ("date\tn_new\tn_grown\tn_verified\tn_deferred\tnum_turns\ttotal_cost_usd\t"
                 "outcome\tpr_url\tdetail\n")


def append_ledger(outcome, n_new=0, n_grown=0, n_verified="", n_deferred="",
                  result=None, pr="", detail=""):
    """Append EXACTLY ONE row per invocation, on every exit path including no-op nights.

    This is what makes Jon's 7-night report possible at all. Previously a row was written only on a
    delta night, so a silent night, a no-token night, a missing-G:-drive night and a night the task
    never fired were indistinguishable — all four left zero trace. The ledger is an attendance
    register now: absence of a row means the lane did not run, and nothing else.
    """
    result = result or {}
    turns, cost = result.get("num_turns", ""), result.get("total_cost_usd", "")
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    if not LEDGER.exists():  # self-seed the tracked ledger header on first run
        LEDGER.write_text("# append-only TSV; runner appends, never commits\n" + LEDGER_HEADER,
                          encoding="utf-8")
    row = "\t".join(str(x) for x in
                    [f"{date.today():%Y-%m-%d}", n_new, n_grown, n_verified, n_deferred,
                     turns, cost, outcome, redact(str(pr))[:200], redact(str(detail))[:160]])
    try:
        with LEDGER.open("a", encoding="utf-8") as f:
            f.write(row + "\n")
        log(f"Ledger row appended (uncommitted): {outcome}")
    except OSError as e:  # G: unavailable / Drive lag — say so, never fail silently
        log(f"WARN: could not append ledger row ({e}); outcome was {outcome}")


HEARTBEAT = REPO / "exchange" / "lanes" / "HEARTBEAT.md"

HEARTBEAT_HEADER = """\
# Nightly lane heartbeat

**One dated line per run, every run, whatever the outcome.** Append-only.

**Why this file exists** (Jon, turn-8 §4b, 2026-07-26): the lane's other run evidence —
stdout logs and the state snapshot — lives on `C:`/`D:` paths *the claude.ai layer
structurally cannot see*. From the wayfinder's seat that makes **"didn't run" and "ran
invisibly" indistinguishable**, and a missed night has to be loud from both venues. This
file sits under `exchange/`, which is published to the `canonical` branch, so the triage
layer can read it directly.

**How to read it — the miss is DERIVED, never recorded.** Nothing here announces a failure.
Compare the newest timestamp below against now: **older than ~24h means a night was
missed**, regardless of what any other document claims. An absent newest line means the
lane has never run at all. Do not trust a status written elsewhere over this arithmetic.

| when (local) | outcome | detail |
|---|---|---|
"""


def heartbeat(outcome, msg):
    """Append one dated line. Never raises — a heartbeat failure must not kill the run,
    but it IS logged loudly, because a silent heartbeat failure recreates the exact
    blindness this file exists to remove."""
    try:
        HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
        if not HEARTBEAT.exists():
            HEARTBEAT.write_text(HEARTBEAT_HEADER, encoding="utf-8")
        detail = redact(str(msg)).replace("|", "\\|").replace("\n", " ")[:220]
        with HEARTBEAT.open("a", encoding="utf-8") as f:
            f.write(f"| {datetime.now():%Y-%m-%d %H:%M:%S} | {outcome} | {detail} |\n")
    except Exception as e:
        log(f"HEARTBEAT-WRITE-FAILED ({type(e).__name__}: {e}) — this run is invisible to "
            f"the claude.ai layer; treat a gap at this timestamp as a real miss")


def finish(outcome, msg, code=0, **kw):
    """Single exit point: log, write the attendance row, beat, exit."""
    log(f"{outcome}: {msg}")
    append_ledger(outcome, detail=msg, **kw)
    heartbeat(outcome, msg)
    sys.exit(code)


def main():
    if KILL.exists():
        finish("SKIP-KILL", f"KILL switch present at {KILL}")
    if os.environ.get("ANTHROPIC_API_KEY"):
        finish("SKIP-APIKEY", "ANTHROPIC_API_KEY set — refusing so billing can't move to "
               "pay-per-token (iam auth-precedence: API key outranks subscription OAuth in -p)")
    if not _tok():
        finish("SKIP-NOTOKEN", "CLAUDE_CODE_OAUTH_TOKEN absent — no subscription auth")

    manifest, why = leg1_manifest()
    if manifest is None:
        # Includes the "G: not mounted" case: Google Drive mounts per-logon, so an unattended run
        # without the Drive present must be a LOUD skip, not an exit-0 that Task Scheduler records
        # as success.
        finish("SKIP-NOREPO", f"Leg 1 could not build a manifest ({why})", code=1)
    log(f"Leg 1: {why}")

    prev, status = load_snapshot()
    if status == "absent":
        write_snapshot(manifest)
        finish("BASELINE", f"first run — snapshot baselined at {len(manifest)} sessions, "
               "no delta processing")
    if prev is None:
        finish("HALT-SNAPSHOT", f"snapshot unreadable ({status}) — refusing to re-baseline, which "
               f"would silently absorb the entire backlog. Inspect/remove {SNAPSHOT} to re-baseline "
               "deliberately.", code=1)

    new, grown = compute_delta(prev, manifest)
    if not new and not grown:
        finish("SILENT", "no new or grown sessions; zero tokens, no PR")

    log(f"DELTA: {len(new)} new, {len(grown)} grown")
    report, truncated = build_report(new, grown, manifest, prev)
    if truncated:
        log(f"delta report truncated at {REPORT_BYTES} bytes")

    result = leg2_headless(report)
    if result.get("is_error"):
        err = redact(str(result.get("_err", "unknown")))
        log(f"Leg 2 error: {err} — snapshot NOT advanced")
        append_ledger("ERROR", len(new), len(grown), 0, len(new) + len(grown),
                      result=result, detail=err)
        heartbeat("ERROR", err)   # bypasses finish(); beat explicitly or the night looks unrun
        sys.exit(1)

    pr = ""
    res_text = str(result.get("result", "")).strip()
    if res_text:
        pr = res_text.splitlines()[-1][:200]

    # Verify BEFORE advancing. If verification itself cannot run, advance nothing: re-running a
    # already-converted delta tomorrow is a cheap no-op for the extractor, whereas advancing over
    # unverified work is unrecoverable.
    post, why2 = leg1_manifest()
    pending, why3 = leg1_pending()
    delta = new + grown
    if post is None or pending is None:
        log(f"Leg 2 ok but verification unavailable (post-scan: {why2}; pending-scan: {why3}) — "
            "snapshot NOT advanced; the delta re-triggers next run")
        append_ledger("UNVERIFIED", len(new), len(grown), 0, len(delta), result=result, pr=pr,
                      detail=f"verification unavailable: {why2 if post is None else why3}")
        heartbeat("UNVERIFIED", why2 if post is None else why3)  # bypasses finish() — beat here
        sys.exit(1)

    own6 = str(result.get("session_id", ""))[:6].lower() or None
    nxt, verified, deferred, absorbed = advance_snapshot(prev, post, delta, pending, own6)
    write_snapshot(nxt)

    log(f"Verified converted: {len(verified)}; deferred (re-trigger next run): {len(deferred)}"
        + (f" -> {deferred[:10]}" if deferred else "")
        + (f"; absorbed own session {absorbed[0]}" if absorbed else "; own session NOT identified"))
    append_ledger("ok" if not deferred else "ok-partial",
                  len(new), len(grown), len(verified), len(deferred),
                  result=result, pr=pr,
                  detail=("all delta sessions verified" if not deferred
                          else f"{len(deferred)} session(s) unverified, left below watermark"))


if __name__ == "__main__":
    # An unhandled crash must still leave a beat. Without this, the one failure mode with
    # no diagnosis at all — the script dying before any ledger row — is also the one that
    # looks identical to "the scheduled task never fired." Those need different fixes.
    try:
        main()
    except SystemExit:
        raise
    except BaseException as e:
        heartbeat("CRASH", f"{type(e).__name__}: {e}")
        raise
