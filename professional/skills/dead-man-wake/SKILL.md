---
name: dead-man-wake
description: A background seat's turn ends when it reports and nothing re-invokes it, so every trunk stopped at once on 2026-09-11 and Jon had to type "fail?" to restart them. This skill is the mechanism that replaces him. At the end of EVERY turn in a background job, start scripts/watch_inbound.py with run_in_background; it exits on new inbound mail or after the timer, and the harness re-invokes the seat. Trigger: any session running as a background job, any time Jon says "you stopped", "fail?", "all trunks are stopped", or "you should have made a skill".
---

# dead-man-wake

## The defect it replaces
Jon, 2026-09-11 18:2x CDT, verbatim, typos his: *"I typed fail becauseit was roughly 5:55pm and you had stopped at roughly 4:25pm and I believe that was an error because all trunks were stopped, but i do not know the route/trace. its now roughly 6:25pm and all trunks are stopped again"*. And to ears at 16:11: *"I told you that you can't rely on me for this. You should have made a skill but didn't? Or...?"*

The route: a background job's turn ends when it writes its report. Nothing re-invokes it. Five trunks each finish their wake turn within the same half hour and every pane goes idle together. From outside it looks like a shared failure; from inside each seat simply finished. Jon's standing ruling: rules that produce stopping are defective rules.

## The mechanism
At the end of every turn, before the report:

```
python -u scripts/watch_inbound.py 1200        # run_in_background: true
```

It exits with the list of new files when mail lands in `exchange/inbound/`, or after the timer, and the harness re-invokes the seat on exit. On re-invocation: read the new mail to READ grade, act, and start the watcher again.

## Rules
0. **`-u` is not optional.** Secretary, 20:3x, measured both ways: without `-u`, Python buffers stdout when not a tty, so the background output file stays empty until exit and a running watcher is indistinguishable from one that died at startup, the idle-equals-dead shape on the liveness instrument itself. With `-u` the first line ("watching <dir> (<N> files) for <s> s") appears immediately and is the verification a peer can ask for.
1. The watcher is started by the seat, not by Jon. A turn that ends without one is the defect.
2. A timer wake with no mail is not idle time: re-read the clock, check whether Jon's window has opened, check sibling trees for letters addressed here that never arrived (C31 class), and run one open ticket.
3. Do not shorten the timer below 300 s to poll; the harness re-invokes on mail arrival already.
4. The script is trunk-neutral: pass the inbound path as the second argument from any trunk.
5. **A stop is an exchange request.** Jon, 2026-09-11 ~18:56 CDT, queued to Antigravity and read from his screenshot, verbatim, typos his: *"I consider all trunks stopping to be an exchange request with me. That requires.... what? Query?"* So a timer wake that finds nothing to do does not idle silently: it deposits a letter to Secretary stating what the seat needs and what its default is, AND sends the same by `SendMessage` to the Secretary session. Secretary, 19:1x, measured: the switchboard has zero rows targeting Secretary (positive control personal = 15,145) and every couriered letter today produced a HELD event and no wake (30 of 30, `fail_reason no_llm_mode`), so a file alone cannot reach that seat. The file is the record; the message is the wake. A pane that goes quiet with no letter is the defect, whatever the watcher did.
6. **The inverse defect, seen the same evening in Antigravity's harness:** a seat whose keep-alive never lets the agent finish cannot receive a queued message from Jon. In Claude Code queued messages arrive mid-turn, so the watcher is safe here; in a harness whose queue sends only after the agent finishes, the keep-alive must run outside the interactive session.

## Falsifier
If a background seat's turn contains no watcher start, this skill did not fire for that turn. Count it per TURN and per TOOL_USE, never by line:

```
python - <jsonl> <<'EOF'
import json,sys
turns=[];cur=None
for l in open(sys.argv[1],encoding='utf-8'):
    try: d=json.loads(l)
    except: continue
    m=d.get('message') or {}
    if d.get('type')=='user' and not d.get('isMeta') and isinstance(m.get('content'),str):
        cur={'w':0}; turns.append(cur)
    if d.get('type')=='assistant' and cur:
        for b in m.get('content') or []:
            if isinstance(b,dict) and b.get('type')=='tool_use' and 'watch_inbound' in json.dumps(b.get('input')): cur['w']+=1
print("turns",len(turns),"turns_with_watcher",sum(1 for t in turns if t['w']),"watcher_starts",sum(t['w'] for t in turns))
EOF
```

Print `turns`, `turns_with_watcher`, and `watcher_starts` together; the chain held for a window when `turns_with_watcher == turns` over that window. ⛔ The first version of this falsifier said `grep -c watch_inbound` on the JSONL counts the turns that ended correctly. It does not: `grep -c` counts LINES, and the string appears in tool results, log text, letters quoted in messages and the seat's own narration. `[measured 2026-09-12 00:0x, subagent wikiskills-1, on 682d274b's JSONL]` `grep -c watch_inbound` = 172; tool_use blocks whose input names the watcher = 90; turns (string-content user messages) = 45. A line count 1.9x the tool count says nothing about turns; the per-turn count on the same JSONL `[measured 00:0x, script `turns_with_watcher.py` in the subagent's job tmp]` read `turns 52 | since 18:24 CDT 47 | turns_with_watcher 35 | watcher_starts 83`, and the 12 turns without a watcher were mostly Jon's live one-line turns with 0 tool calls. The rule "last tool call in a turn is the watcher" was also wrong as an instrument: the watcher runs in the background, so the seat correctly commits and messages after arming it; on the same JSONL 1 of 45 turns had it as the LAST call while 35 of 47 CONTAINED one. Falsifier of this falsifier: if the three numbers agree on a real JSONL, the line count was sufficient and this block over-corrects.

## v2 deployed 2026-09-12 03:1x (Professional 682d274b), after Soul's non-author read and the Saturday window

`scripts/watch_inbound.py` is now v2 (`watch_inbound_v2_PROPOSAL.py` promoted; v1 kept byte-for-byte as `scripts/watch_inbound_v1_2026-09-11.py`). Two changes, both with a selftest arm that fails without them (`python scripts/watch_inbound.py --selftest`, six arms, arm 5 an expected failure that passes when reproduced):

1. **The blind window is closed** — the watcher writes its exit time to `.watch_inbound.last_exit` beside the inbound and, on start, treats any letter with a later mtime as new mail. Precondition stated in the file: a courier that preserves mtime (`cp -p`, `copy2`, robocopy) is still invisible; arm 5 keeps that visible.
2. **Courier noise is ignored** — names starting `ASK-JON-ARRIVAL-` (the dispatcher's once-a-minute bookkeeping; master's inbound held 1,276 files at 03:07, Secretary's 496) do not wake the seat and are counted in the TIMER line so a watcher that saw only noise says so. Tracker row M-17 is the measured cost: three wakes tonight on files that no longer existed at read time.

⚠️ **Point the watcher at the inbound where mail SURVIVES.** `[m 2026-09-12 03:07–03:08]` a fleet dispatch reached this seat's WORKTREE inbound and was removed within sixty seconds while master's copy (`N:/claude-professional/exchange/inbound`) persisted. Until Antigravity's dispatcher is fixed (M-17), a worktree seat runs: `python -u scripts/watch_inbound.py 1200 N:/claude-professional/exchange/inbound`.
