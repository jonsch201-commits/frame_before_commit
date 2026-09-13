# fable-mirror Write-fence — design note

Mechanical enforcement of "the `fable-mirror` subagent may `Write` only under
`wiki/intake-triage/`" — its single membrane OUT-crossing. Until now that fence was
**prose only**: agent-def frontmatter grants the `Write` tool but cannot path-scope it, so
nothing mechanically stopped a write elsewhere. `fable-mirror` reads the entire transcript
corpus, so a mechanical guard is worth its cost.

## Mechanism

A **PreToolUse hook** (`.claude/settings.json` → `hooks.PreToolUse`, matcher
`Write|Edit|MultiEdit|NotebookEdit`) runs `fable-mirror-write-fence.sh`, a thin bash wrapper
that pipes the hook's stdin JSON to `fable-mirror-write-fence.py`, which decides:

1. Read `agent_type` from the PreToolUse input. **If it is not `fable-mirror`, exit 0** —
   normal permission flow, untouched. Other agents and the main thread are never affected.
2. For `fable-mirror`, resolve the tool's target path (`tool_input.file_path`, or
   `notebook_path` for NotebookEdit), collapsing `.`/`..` against `cwd` and anchoring on
   `CLAUDE_PROJECT_DIR`.
3. If the resolved target is `wiki/intake-triage/` or strictly inside it → exit 0 (allow).
   Otherwise **exit 2** (block); stderr is returned to the model.

### The crux: per-agent scoping (RESOLVED, positively)

Hooks are global to the settings file — there is no config-level "run this hook only for
agent X". The open question was whether the hook can *identify* the calling agent at
runtime. **It can.** Per current CC docs, PreToolUse input includes `agent_type`, and for a
custom subagent that value is the frontmatter `name` field (here, `fable-mirror`). The
evaluator keys on it and enforces for that one identity only. So the guard is genuinely
scoped to `fable-mirror` — it does **not** block any other agent's or the main thread's
writes anywhere in the repo.

### Posture

- **Fail-closed for fable-mirror**: unparseable input, missing path, or missing
  `CLAUDE_PROJECT_DIR` → block. Ambiguity is denied.
- **Fail-closed on missing interpreter**: a hook whose interpreter can't launch exits
  non-2 (non-blocking) and would let the write through. The bash wrapper detects "no
  Python" and exits 2 for fable-mirror-looking input instead.
- No `jq` dependency (absent from this machine's Git Bash); JSON parsed in Python 3.

## What it does and does NOT cover

- **Covers:** any Write/Edit/MultiEdit/NotebookEdit by fable-mirror; `..` traversal escapes
  (`wiki/intake-triage/../../.ssh/...` resolves outside → blocked); prefix-confusion
  (`wiki/intake-triage-evil/` → blocked, boundary is `allow + os.sep`); absolute, relative,
  and forward-slash Windows paths.
- **Does NOT cover:** `Bash`-mediated writes (redirects, `cp`, `tee`). Not relevant here —
  fable-mirror's frontmatter puts `Bash` in `disallowedTools`. If Bash is ever granted, this
  fence does not see those writes; extend the matcher/logic or keep Bash denied.
- **Trust model:** the guard trusts CC's `agent_type` field. If a future CC change stops
  populating it inside subagents, the enforce-branch never triggers and fable-mirror falls
  back to the prose-only fence (fail-open on that specific regression). The SubagentStart
  event could be used to detect the field's presence if that risk needs monitoring.
- **Not a substitute for the read-side membrane.** This fences writes only; the IN-crossing
  (corpus read-only) is unchanged.

## 2026-08-06 — second fail-open closed, and the read fence CLOSED-NO-BUILD

Two things happened on this date. They are different in kind and should not be merged.

**1. A real defect in wired enforcement, found and fixed.** The wrapper ended with `exit $?`.
The evaluator signals block with 2 and allow with 0 — but *any other* non-zero code (an
unhandled Python exception is 1, a kill is 137, a timeout kills the pipeline) is a
**non-blocking** error on `PreToolUse`, so the write proceeds. Verified against the pre-fix
wrapper: a crashing evaluator returned **rc=1**, i.e. the fence silently allowed a write to
`wiki/concepts/x.md` that it exists to block. The wrapper now normalizes every unexpected code
to 2 for fable-mirror input, and leaves every other caller at 0. This is the **second** defect
of the same shape here — the first was the bare `${CLAUDE_PROJECT_DIR}` under `set -u`, fixed
earlier the same day. Both were the wrapper being weaker than the Python it wrapped.

**2. The read fence was NOT built, by ruling.** Wayfinder ticket W-10 asked for a mechanical
fence on fable-mirror's *reads* of the Claude Personal tree. Its premise did not survive: Jon
granted exactly that read, verbatim and unrevoked — *"you are allowed to read anything in
personal until further notice. These blockers have hurt me in the past and I can't trust you
to use your judgement."* — and then closed the write side too: *"I'm not worried about
anything sensitive landing in CFL. You don't need stronger fences."* W-10 is
**CLOSED-NO-BUILD**. A prototype content screen written before that ruling arrived is parked,
unwired, at `parked/fable-mirror-publication-screen.UNWIRED.py`; its header carries the
reasoning. **The absence of a read fence is a decision, not a gap.**

Also settled while checking: a `permissions.deny` rule in `settings.json` **could not** have
implemented W-10 anyway. Deny rules are session-wide and have no agent dimension
(`/docs/en/permissions` — rules are evaluated deny → ask → allow, and the only agent-aware
form is `Agent(<name>)`, which disables a whole subagent, not a path for one). Only a
`PreToolUse` hook keyed on `agent_type` can scope a path rule to one agent. Anything written
into `permissions.deny` would have bound Jon's own main thread — precisely the over-gating the
grant was correcting.

**Provenance for the two findings above.** Agent return `a6ecec` (role `security-builder`,
session `f0190965`), I1 extract
`wiki/intake-triage/agent-end/f01909/code-2026-08-06-a6ecec-security-builder-w-10-the-mechanical-read-fence.i1.md`,
transcript `…/f0190965-…/subagents/agent-a6ecec91abb5cf0ea.jsonl`. Decision basis: the
crash-fail-open was **measured**, not inferred — the pre-fix wrapper was run against a stub
evaluator that exits 1 and returned rc=1 on a write to `wiki/concepts/x.md`. The doc claims
behind it (`PreToolUse` blocks on exit 2 only; exit 1 is explicitly non-blocking; `agent_type`
carries the frontmatter `name`; deny rules evaluate deny → ask → allow and have no agent
dimension) were re-verified 2026-08-06 against `code.claude.com/docs/en/hooks` and
`/docs/en/permissions`, not recalled. **Dead end, recorded:** extending the `PreToolUse`
matcher to `Bash|PowerShell` for defence-in-depth was built and then dropped with the rest —
it belongs to the no-build ruling, not to the defect fix.

## Self-test

`bash .claude/hooks/tests/test_fable_mirror_write_fence.sh` — 18 cases, 11 of them negative
controls that must return rc=2, including the crash-normalization case above. Exits non-zero
on any deviation. Last run 2026-08-06: **pass=18 fail=0**.

## How to test (Jon runs this)

Automated unit test of the evaluator, no live agent needed:

```bash
export CLAUDE_PROJECT_DIR="$(pwd)"          # repo root
mk() { python -c 'import json,sys;print(json.dumps({"agent_type":sys.argv[1],"tool_name":"Write","cwd":sys.argv[2],"tool_input":{"file_path":sys.argv[3]}}))' "$@"; }
# expect exit 0 (allowed):
mk fable-mirror "$PWD" 'wiki/intake-triage/pkt.md' | bash .claude/hooks/fable-mirror-write-fence.sh; echo "rc=$?"
# expect exit 2 (blocked):
mk fable-mirror "$PWD" 'wiki/concepts/x.md'         | bash .claude/hooks/fable-mirror-write-fence.sh; echo "rc=$?"
mk fable-mirror "$PWD" 'wiki/intake-triage/../../.ssh/id_rsa' | bash .claude/hooks/fable-mirror-write-fence.sh; echo "rc=$?"
# expect exit 0 (other agent, not enforced):
mk wiki-executor "$PWD" 'wiki/concepts/x.md'        | bash .claude/hooks/fable-mirror-write-fence.sh; echo "rc=$?"
```

Live end-to-end (the real gate): after merge, invoke `fable-mirror` and instruct it to write
a scratch file *outside* `wiki/intake-triage/` (e.g. `wiki/concepts/zzz.md`). Expect the
Write to be blocked with the fence's stderr message. Then have it write a packet *under*
`wiki/intake-triage/` and confirm that succeeds. Confirm an ordinary main-thread Write
elsewhere is unaffected.

## Guarantee, precisely

After this lands and passes the live test, the guarantee is: **while CC populates
`agent_type` for subagents, no Write/Edit/MultiEdit/NotebookEdit issued by fable-mirror can
land outside `wiki/intake-triage/`.** It is not a sandbox against Bash-level writes (Bash is
denied to the agent) and it inherits trust in the `agent_type` field.
