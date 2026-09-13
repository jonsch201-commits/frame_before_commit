#!/usr/bin/env python
# ============================================================================================
# PARKED — UNWIRED BY RULING, NOT BY OVERSIGHT.  2026-08-06
#
# Nothing invokes this file. It is not referenced from .claude/settings.json and must not be.
#
# It is a prototype content/publication screen for fable-mirror writes, built under a brief
# that said: if W-10's read-fence premise did not survive Jon's read grant, build "a stronger
# write fence instead." Mid-build Jon closed the question directly, verbatim:
#
#     "I'm not worried about anything sensitive landing in CFL. You don't need stronger
#      fences. You need to stop adding conservatism into my words."
#
# The coordinator recorded that the "build a stronger write fence" instruction was its own
# substitution, not Jon's, and closed W-10 as CLOSED-NO-BUILD. The earlier grant stands too:
#
#     "you are allowed to read anything in personal until further notice. These blockers have
#      hurt me in the past and I can't trust you to use your judgement."
#
# So BOTH sides of the membrane are unfenced by decision: reads by the grant, writes by the
# ruling above. The only mechanical fence that ships is the PATH fence in
# ../fable-mirror-write-fence.py (fable-mirror writes land under wiki/intake-triage/ only),
# which predates all of this and is unrelated.
#
# It is kept rather than deleted so that nobody rebuilds it from scratch in three weeks
# believing it was never attempted. REWIRING IT REQUIRES A NEW JON RULING — the absence of a
# fence here is the decision, not a gap.
# ============================================================================================
#
# ---- original header follows ----------------------------------------------------------------
# fable-mirror-write-fence.py — mechanical PUBLICATION fence for the fable-mirror subagent.
#
# PURPOSE
#   fable-mirror (.claude/agents/fable-mirror.md) holds the Write tool but is charter-bound
#   (prose only) to write nothing except escalation packets under wiki/intake-triage/ — the
#   single OUT-crossing of its membrane. Agent-def frontmatter cannot path-scope a granted
#   tool, so that fence is prose-only. This PreToolUse evaluator makes it MECHANICAL.
#
#   Two gates, in order, both enforced ONLY when agent_type == "fable-mirror":
#     GATE 1 (path)    — the resolved target must be inside wiki/intake-triage/.
#     GATE 2 (content) — the payload must not carry secrets, government/financial
#                        identifiers, or long verbatim personal-domain material.
#
#   GATE 2 exists because of Jon's ruling of 2026-08-06, verbatim: "you are allowed to read
#   anything in personal until further notice ... Look what gets written into CFL should not
#   be sensitive. But you shpuld read what you need to read, and find the way with
#   confidence." The read side is DELIBERATELY unfenced — see the README. The guard is on the
#   write side, because wiki/intake-triage/ is tracked, lands on main, and is republished to
#   the `canonical` branch (the claude.ai connector surface). That is the actual publication
#   path out of this repo, and it is what "written into CFL" governs.
#
# SCOPING (the crux)
#   Per CC docs, PreToolUse input carries `agent_type`, which for a custom subagent is the
#   frontmatter `name` field. This evaluator ENFORCES only when agent_type == "fable-mirror".
#   For every other caller (other agents; the main thread, where the field is absent) it
#   exits 0 and leaves normal permission flow untouched. That is the whole guarantee: the
#   fence is scoped to one agent by identity, not applied repo-wide. Note that settings.json
#   `permissions.deny` rules CANNOT do this — they are session-wide and have no agent
#   dimension — which is why the fence is a hook and not a deny rule.
#
# POSTURE
#   Fail-closed for fable-mirror: unparseable input, missing path, missing anchor, unexpected
#   tool, or any content hit => block (exit 2).
#
# Docs verified 2026-08-06 at code.claude.com/docs/en/hooks and /docs/en/permissions:
#   - PreToolUse runs on "every tool call inside the agentic loop ... except EndConversation
#     calls, which skip both". Matchers are tested with RegExp.prototype.test against
#     tool_name, so read-only tools are matchable too.
#   - PreToolUse stdin: tool_name, tool_input, tool_use_id, cwd, permission_mode, and inside a
#     subagent agent_id + agent_type (frontmatter `name` for a custom subagent).
#   - Exit 2 => blocking error; stderr is returned to the model; the tool call is blocked.
#     "Claude Code treats exit code 1 as a non-blocking error and proceeds with the action."
#   - CLAUDE_PROJECT_DIR is exported to the spawned hook process.

import sys, os, re, json

GUARDED_AGENT = "fable-mirror"
ALLOWED_SUBDIR = os.path.join("wiki", "intake-triage")

# Tools fable-mirror is chartered to use for its OUT-crossing. Anything else that reaches this
# fence from fable-mirror (Bash, PowerShell, a future tool) is blocked rather than reasoned
# about: a shell redirect is a write channel this evaluator cannot path-check.
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# Longest verbatim run permitted in a packet that also references personal-domain material.
# The standing fence says: show "path, line, count, and at most a 40-char fingerprint".
# 400 is deliberately looser than 40 so ordinary FL quoting is unaffected; it only bites when
# the packet ALSO points at personal-domain sources. Override with FM_FENCE_QUOTE_CAP.
QUOTE_CAP = int(os.environ.get("FM_FENCE_QUOTE_CAP", "400"))

SECRET_PATTERNS = [
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}")),
    ("github fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}")),
    ("anthropic api key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{16,}")),
    ("openai-style api key", re.compile(r"\bsk-[A-Za-z0-9]{32,}")),
    ("aws access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google api key", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}")),
    ("slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.=]{24,}")),
]

# key=value / key: value with a real-looking value. Redaction placeholders are exempt so the
# fence does not block a packet that is correctly REPORTING a leak.
ASSIGN_RE = re.compile(
    r"(?i)\b(password|passwd|secret|api[_\-]?key|access[_\-]?token|auth[_\-]?token|"
    r"client[_\-]?secret|private[_\-]?key)\b\s*[:=]\s*[\"']?([^\s\"'`,;]{8,})"
)
REDACTED_RE = re.compile(
    r"(?i)^(x{3,}|\*{3,}|\.{3,}|<[^>]*>|\[[^\]]*\]|\{[^}]*\}|redacted|removed|elided|"
    r"placeholder|none|null|todo|example|changeme|your[_\-]?\w+)$"
)

SSN_RE = re.compile(r"\b(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b")
PAN_CANDIDATE_RE = re.compile(r"(?<![\d\-])(?:\d[ \-]?){12,18}\d(?![\d\-])")

# A packet that points at personal-domain material. Deliberately narrow: these are paths and
# tree names, not topic words. Blocking on words like "health" or a family member's name would
# be exactly the over-gating Jon's ruling was correcting.
PERSONAL_REF_RE = re.compile(
    r"(?i)(claude[ _\-]personal|wiki/personal/|/personal/|\\personal\\|"
    r"raw/transcripts/[a-z\-]+/personal)"
)

FENCED_RE = re.compile(r"```[^\n]*\n(.*?)(?:```|\Z)", re.S)
BLOCKQUOTE_RE = re.compile(r"(?m)^(?:[ \t]*>.*\n?)+")


def block(detail, guidance=None):
    sys.stderr.write("fable-mirror write-fence: BLOCKED. " + detail + "\n")
    sys.stderr.write(
        guidance
        or "fable-mirror may Write only under wiki/intake-triage/ "
           "(its single membrane OUT-crossing). Re-target the escalation packet there.\n"
    )
    sys.exit(2)


def luhn_ok(digits):
    total, alt = 0, False
    for ch in reversed(digits):
        d = ord(ch) - 48
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


def collect_strings(node, out):
    """Recursively gather every string in tool_input.

    Deliberately schema-agnostic: Write uses `content`, Edit uses `new_string`, MultiEdit
    uses `edits[].new_string`, NotebookEdit uses `new_source`, and a future tool will use
    something else. Walking the whole object means an unrecognized field cannot become a
    silent bypass — the failure mode this fence exists to avoid.
    """
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, dict):
        for v in node.values():
            collect_strings(v, out)
    elif isinstance(node, (list, tuple)):
        for v in node:
            collect_strings(v, out)


def longest_verbatim_run(text):
    longest = 0
    for m in FENCED_RE.finditer(text):
        longest = max(longest, len(m.group(1).strip()))
    for m in BLOCKQUOTE_RE.finditer(text):
        longest = max(longest, len(m.group(0).strip()))
    return longest


def screen_content(text):
    """Return (category, detail) on a hit, or None. Order: secrets, IDs, verbatim."""
    for label, rx in SECRET_PATTERNS:
        m = rx.search(text)
        if m:
            return ("SECRET", "payload contains a %s (matched %d chars at offset %d)"
                    % (label, len(m.group(0)), m.start()))

    m = ASSIGN_RE.search(text)
    if m and not REDACTED_RE.match(m.group(2)):
        return ("SECRET", "payload assigns a live-looking value to '%s'" % m.group(1))

    m = SSN_RE.search(text)
    if m:
        return ("GOVID", "payload contains a US SSN-shaped identifier at offset %d" % m.start())

    for m in PAN_CANDIDATE_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 19 and luhn_ok(digits):
            return ("FINANCIAL",
                    "payload contains a %d-digit Luhn-valid card-shaped number at offset %d"
                    % (len(digits), m.start()))

    if PERSONAL_REF_RE.search(text):
        run = longest_verbatim_run(text)
        if run > QUOTE_CAP:
            return ("PERSONAL_VERBATIM",
                    "packet references personal-domain sources and carries a %d-char verbatim "
                    "block (cap %d)" % (run, QUOTE_CAP))
    return None


def main():
    raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except Exception:
        # Cannot parse. Only fail closed if it looks like a fable-mirror call; otherwise
        # never interfere with other callers.
        if '"fable-mirror"' in raw and "agent_type" in raw:
            block("unparseable PreToolUse input for a fable-mirror call")
        sys.exit(0)

    if data.get("agent_type") != GUARDED_AGENT:
        sys.exit(0)  # not fable-mirror -> defer to normal permission flow

    tool = data.get("tool_name", "")
    tinput = data.get("tool_input") or {}

    # ---- GATE 0: tool class -------------------------------------------------------------
    # The settings.json matcher also routes Bash/PowerShell here so that widening
    # fable-mirror's frontmatter `tools:` can never open an unfenced write channel via a
    # shell redirect. Such a call is blocked outright rather than path-parsed.
    if tool not in WRITE_TOOLS:
        block(
            "tool '%s' is outside fable-mirror's charter" % (tool or "<unnamed>"),
            "fable-mirror is a records-reader: Read/Grep/Glob in, and Write to "
            "wiki/intake-triage/ out. Shell and other tools are not a membrane crossing.\n",
        )

    # ---- GATE 1: path -------------------------------------------------------------------
    path = tinput.get("file_path") or tinput.get("notebook_path") or ""
    cwd = data.get("cwd") or ""
    proj = os.environ.get("CLAUDE_PROJECT_DIR", "")

    if not path:
        block("no target path in tool_input for %s" % (tool or "write"))
    if not proj:
        block("CLAUDE_PROJECT_DIR unset; cannot anchor the allow-root")

    # Resolve relative paths against the tool call's cwd (falling back to project root).
    if not os.path.isabs(path):
        path = os.path.join(cwd or proj, path)

    # normpath collapses '.' and '..' without touching the filesystem (Write creates the
    # file, so it may not exist yet). normcase makes the compare case-insensitive and
    # separator-insensitive, matching the Windows filesystem.
    target = os.path.normcase(os.path.normpath(os.path.abspath(path)))
    allow = os.path.normcase(
        os.path.normpath(os.path.abspath(os.path.join(proj, ALLOWED_SUBDIR)))
    )

    if not (target == allow or target.startswith(allow + os.sep)):
        block("%s -> %s resolves outside wiki/intake-triage/" % (tool or "write", target))

    # ---- GATE 2: content ----------------------------------------------------------------
    parts = []
    collect_strings(tinput, parts)
    payload = "\n".join(parts)

    hit = screen_content(payload)
    if hit:
        cat, detail = hit
        block(
            "[%s] %s" % (cat, detail),
            "Jon's ruling of 2026-08-06 leaves your READS unfenced and guards the WRITE side: "
            "'what gets written into CFL should not be sensitive.' wiki/intake-triage/ is "
            "tracked, lands on main, and is republished to the `canonical` branch. Report the "
            "finding by PATH, LINE, COUNT and at most a 40-char fingerprint instead of "
            "reproducing the material.\n",
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
