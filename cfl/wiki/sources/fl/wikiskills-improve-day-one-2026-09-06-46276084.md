---
kind: source
trunk: fl
session: "46276084-5985-4514-9ad1-0d77cf7a0ceb"
model: "claude-opus-5 -> claude-fable-5-1 (switched 2026-09-05 ~21:15)"
date: 2026-09-06
window: "2026-09-05 15:25 -> 2026-09-06 15:0x CDT; one auto compact 2026-09-05 22:34; Jon's compact pending at write time"
author: cfl 46276084
status: "I0/I1 record written at the compact boundary; not synthesized (wiki-master's)"
handoff: handoff-wikiskills-improve-day-one-2026-09-06.md
labels: [verbatim, measured, interpretation]
---

# wikiskills-improve, day one — what was established and how to check it

**How to read this page.** Every claim carries one of three labels. `[verbatim]` is Jon's words with a
primary. `[measured]` names the command or the seat that ran it. `[interpretation]` is a reading a
successor may strike. Nothing untagged is a claim.

## 1. The skill exists, is deployed machine-global, and fires on a fresh JSON

- `[measured — sync-universal.sh receipt, 14:56]` `~/.claude/skills/wikiskills-improve/SKILL.md` sha256 `8f4816511aeb…`,
  byte-identical to `N:\claude-cfl\clone\skills\wikiskills-improve\SKILL.md`. Check: `cmp` the two paths.
- `[measured — four seats, 09:0x–09:2x, each from its own tree]` Professional, Secretary, Soul, Herald read the same hash,
  found their elder JSONL on disk, and ran their §3 line. Nine defects were found in the process; all fixed the same
  hour by the seat that found them (list in §3 below).
- `[measured — Secretary, JSONLs 9fdea274/c75b0402/10f5443d/0e4d7f9c under N--claude-secretary]` three headless fresh
  JSONs invoked the Skill tool with `wikiskills-improve` and printed the `### Secretary` headline as the first line; one
  produced a first finding (corpus 44.5% reachable). Check: `grep -c '"skill":"wikiskills-improve"' <jsonl>`.
- `[measured — JSONLs ec410a46/6cfd7ace, first user turn 14:26:11Z]` the 09:26 attempt received the prompt
  `C:/Program Files/Git/wikiskills-improve`: git-bash's MSYS layer converts a leading-slash CLI argument to a Windows
  path. Reproduced without Claude (Secretary): `python -c "import sys;print(sys.argv[1])" /wikiskills-improve`.
  **Type the slash command inside the session, or `MSYS_NO_PATHCONV=1`.** `[interpretation]` a test with no positive arm
  certifies nothing — Secretary's first test could only fail and its output was read as a property of the skill.

## 2. The elder-consult line works, and the three ways it was wrong first

- `[measured — CFL 09:05, 09:17, 09:2x; Soul 09:2x from its own tree]` `claude --resume <full UUID> --fork-session
  --strict-mcp-config --mcp-config C:/Users/JonSc/.claude/mcp-empty.json --permission-mode plan -p "$(cat
  C:/Users/JonSc/.claude/consult-prompt-soul.txt)"` from a hookless cwd: JSONL within seconds, rc=0 in 13–47 s, every
  answer labeled `[carried]`/`[re-read]`, questions answered in order.
- The three prior forms, each faithful to a source and unrunnable as pasted: `--mcp-config <empty json>` (`{}` is rejected:
  "Invalid MCP configuration: mcpServers"); `--mcp-config <file with {"mcpServers": {}}>` (a description where a path must
  be — errors); `-p "<prompt from …§3>"` and then `-p "$(cat <§3 verbatim>)"` (a description, then a TEMPLATE with five
  placeholders — **does not error**: the elder answers a meaningless prompt fluently, rc=0, measured 09:17 as "Your message
  arrived empty…" followed by a status table). `[interpretation — Soul, adopted]` canonical is not the same as sendable.
- `[measured — Soul]` in a shared tree (Personal: Soul and Herald, 19 hooks) an elder refuses commits it never made; its
  silence about a change is not evidence about the change.
- `[measured — Professional, controls 22:40–22:42 the night before]` the fork hang was SessionStart hooks, not MCP: from a
  trunk tree a plain `-p ok` sat 75 s+; from a scratch dir it returned in <60 s. Five forks from the scratchpad: JSONLs in
  3 s, returns in 91–121 s. Forks land under the SCRATCHPAD's project key — copy them home.

## 3. Defects found by a seat other than the author, day one (the orthogonal-review argument, measured)

| found by | defect | fixed |
|---|---|---|
| Soul | Personal section had no runnable command | fork line added |
| Herald | Personal has no ancestor tool; `/wake` Step 0 named a CFL-only script in a machine-global file | per-trunk table, UNKNOWN on absence |
| Herald | seven `wake.md` on the machine; sync's SOURCE was a third CFL file that reverted the fix | three CFL homes identical; `cp -r` + sha256 receipt |
| Professional | its ancestor tool named a control fork; CFL's named a continuation | c84c905; `is_seat()` |
| Professional | 533 dirty paths at a barrier | landed, one commit |
| Soul ×2 | MCP arg prose (errors); `-p` prose (succeeds silently) | real files written by sync |
| Secretary | section prose-only; stale map; frontmatter asserted a removed hook LIVE for 10 h and was relayed to Jon | three commands; as-of + re-derive |
| Professional | "project copy shadows user-level" stated as fact | inverted: precedence is measured from the body a session receives |
| Herald | a path fix mangled by the Bash-tool transport; the verifying grep crossed the same transport (false 0) | forward-slash form; byte-count verification; Rule 11 amendment |

`[measured — Herald, 07:05]` five corrections between two seats in thirteen hours, every one caught by the other party,
none by the seat that made it.

## 4. The routing error Jon named

`[verbatim — Jon, history.jsonl 2026-09-06, typos his]` 06:47 to Herald: *"Did you attempt to route anything 'for me'
thjrough secretary? Why did you miss this?"* · 08:57 to Soul: *"did you route that which you said was for me first through
secretary for it to judge how co-trunk review should occur, or did yo liply try to leave it for me here?"* · 09:03 to
Professional: *"You owned your own, but didn't check with secretary suficiently on the others?"* · 09:18 to CFL:
*"/wayfinder routing error"*.
`[measured — this seat's own reports]` five consecutive reports to Jon since 06:49 ended with a WHAT I NEED FROM YOU block;
none of its items went through Secretary. When they did (09:2x), Secretary's intake test judged **three of four were not
Jon's** (`exchange/inbound/secretary-RULING-2026-09-06-0930-…md`). Fix: `present-to-jon` Output Rule 7 + `scripts/audit/for_jon_routed.py`.

## 5. Rulings applied today

- `[verbatim — Jon to Professional, 14:5x]` *"i fucking want everyohe to be able to see everything … i don't want it to feel
  like anything is walled or limited"* · *"they need effectively hte same access as all of you."* → LAUNCH-SPEC-V1 §7.3
  re-decided: seven fences to parity; three kept with present reasons that are not docker (publication gate; the 08-19
  outbound rule every trunk carries; single-writer accretion, a measured concurrency defect). Approved Professional 14:58;
  applied d680f3bf, sha256 `416064118e6cc102`.
- Rule 13 (ground-before-stating): a number handed to Jon carries its cause and its consequence for his next act. Fixture:
  06:49, *"2.9 GB free"* with neither; Jon: *"You have now failed."* Corrected in three minutes because the seat was warm.

## 6. What a successor should check first, with the command
1. `cmp N:\claude-cfl\clone\skills\wikiskills-improve\SKILL.md ~/.claude/skills/wikiskills-improve/SKILL.md`
2. `python scripts/audit/ask_elder.py --wake-line` → ANCESTOR should read `46276084 … [DECLARED]`
3. the two lane outputs named in the handoff (prototype STATE; RE-4 table) — read, do not re-run
4. `python scripts/audit/for_jon_routed.py <your first report>` before it reaches Jon
