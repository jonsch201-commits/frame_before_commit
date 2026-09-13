"""FOG-4 probe v3 -- can LAST-EXERCISED be measured? Four graded signals.

v1 used any mention -> saturated by `ls skills/`; every skill looked fresh.
v2 added a Skill-tool signal -> MISSED user-typed slash commands entirely,
   which are recorded as <command-name>/x in a user message, not a tool_use.
v3 adds that. Each signal has a DIFFERENT blind spot; they are reported
separately and never summed.

  CMD    -- a user-typed <command-name>/x. Strongest evidence of real use.
  INVK   -- a Skill tool_use whose `skill` field is x. Agent-initiated use.
  TGT    -- a tool_use naming x in a call naming <= FANOUT capabilities.
  SWEEP  -- named alongside > FANOUT others. ENUMERATION, not use.

FAILURE DIRECTION: CMD+INVK together are a LOWER bound on real use -- a skill
read by an agent that never names it is invisible here. So "never exercised"
is an UPPER bound on disuse. Never read a zero as proof of a dead skill.

KNOWN BOUND -- NAME COLLISION. TGT and SWEEP counts are contaminated upward for
any capability whose name is also a trunk, peer, directory or common noun:
`soul`, `herald`, `intake`, `data-master`, `handoff` all score high on TGT while
scoring ZERO on CMD and INVK. TGT is a WEAK signal and must never be reported as
use. CMD and INVK are the clean ones. This is why the columns are never summed.
"""
import json, os, re, sys, collections

# scripts/audit/<this> -- three levels to the trunk root. The first draft used two,
# pointed at scripts/skills, and DIED LOUDLY rather than probing an empty name list.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.claude/projects")
if len(sys.argv) > 2:
    names = sys.argv[2].split(",")
else:
    # SKILL ROOTS -- every root reachable from this machine, NOT just this trunk's.
    # The first draft used CFL/skills/ ALONE and therefore could not contain a
    # project-local skill in any trunk. The Secretary found it by running this
    # script and looking at its denominator: `dream` and `ears` live in
    # Claude Personal/.claude/skills/ and were absent from all 39 names -- which
    # is `dream` being invisible for 17 days, reproduced inside the instrument
    # built to detect exactly that. print-the-population, applied to the
    # population-measuring instrument. Roots are PRINTED below, never assumed.
    _roots = [
        os.path.join(REPO, "skills"),
        os.path.expanduser("~/.claude/skills"),
        os.path.join(REPO, ".claude", "skills"),
    ]
    _drive = os.path.dirname(os.path.dirname(REPO))
    for _t in ("Claude Personal", "Claude Secretary", "Claude Professional/claude-professional",
               "Herald Wiki/herald-wiki", "Claude Personal/XC-Exchequer"):
        _roots.append(os.path.join(_drive, _t.replace("/", os.sep), ".claude", "skills"))
    seen_root = []
    names = set()
    for _r in _roots:
        try:
            _d = sorted(d for d in os.listdir(_r)
                        if os.path.isdir(os.path.join(_r, d)) and not d.startswith("New "))
        except OSError:
            seen_root.append((_r, None))
            continue
        seen_root.append((_r, len(_d)))
        names.update(_d)
    names = sorted(names)
    print("SKILL ROOTS SCANNED -- a root that is absent is printed as ABSENT, never skipped:")
    for _r, _n in seen_root:
        print("  %-6s %s" % ("ABSENT" if _n is None else "%d" % _n, _r))
    print()
if not names:
    sys.exit("no capabilities to probe -- refusing to print a green over an empty population")
FANOUT = 3
pat = {n: re.compile(r'(?<![A-Za-z0-9_-])' + re.escape(n) + r'(?![A-Za-z0-9_-])') for n in names}
cmd_rx = re.compile(r'command-name>/([A-Za-z0-9_-]+)')

last = {k: {} for k in ("cmd", "invk", "tgt", "swp")}
cnt = {k: collections.Counter() for k in ("cmd", "invk", "tgt", "swp")}
files = lines = tools = 0

def bump(k, n, ts):
    cnt[k][n] += 1
    if last[k].get(n) is None or ts > last[k][n]:
        last[k][n] = ts

for dp, _d, fs in os.walk(ROOT):
    for f in fs:
        if not f.endswith(".jsonl"):
            continue
        files += 1
        try:
            fh = open(os.path.join(dp, f), "r", encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                lines += 1
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                ts = rec.get("timestamp")
                if not ts:
                    continue
                msg = rec.get("message") or {}
                content = msg.get("content")
                if rec.get("type") == "user":
                    txt = content if isinstance(content, str) else json.dumps(content)
                    for m in cmd_rx.findall(txt or ""):
                        if m in pat:
                            bump("cmd", m, ts)
                if not isinstance(content, list):
                    continue
                for blk in content:
                    if not isinstance(blk, dict) or blk.get("type") != "tool_use":
                        continue
                    tools += 1
                    inp = blk.get("input") or {}
                    matched = [n for n, rx in pat.items() if rx.search(json.dumps(inp))]
                    if blk.get("name") == "Skill" and isinstance(inp, dict):
                        s = str(inp.get("skill", "")).split(":")[-1].strip()
                        if s in pat:
                            bump("invk", s, ts)
                    if not matched:
                        continue
                    k = "swp" if len(matched) > FANOUT else "tgt"
                    for n in matched:
                        bump(k, n, ts)

print("=== FOG-4 v3: is LAST-EXERCISED measurable? ===")
print("DENOMINATORS -- jsonl %d | lines %d | tool_use %d | capabilities %d | fanout >%d = sweep"
      % (files, lines, tools, len(names), FANOUT))
print("FAILS: CMD+INVK are a LOWER bound on use, so a zero is an UPPER bound on disuse.")
print()
h = "%-28s %4s %-12s %4s %-12s %5s %5s"
print(h % ("capability", "CMD", "last CMD", "INVK", "last INVK", "TGT", "SWEEP"))
def key(n):
    return max(last["cmd"].get(n, ""), last["invk"].get(n, ""))
for n in sorted(names, key=key):
    print(h % (n, cnt["cmd"][n], (last["cmd"].get(n) or "--")[:10],
               cnt["invk"][n], (last["invk"].get(n) or "--")[:10],
               cnt["tgt"][n], cnt["swp"][n]))
cold = [n for n in names if not last["cmd"].get(n) and not last["invk"].get(n)]
talked = [n for n in cold if cnt["tgt"][n] >= 100]
print()
print("NO EXERCISE SIGNAL AT ALL (neither CMD nor INVK): %d of %d" % (len(cold), len(names)))
print("  " + ", ".join(cold))

# CLAUSE 3 (Herald, 2026-08-24): a detector that reports a state and renders ONE of
# its consequences will have the others ignored, and will look green doing it. So
# every consequence of this state is printed here. The reader obeys what is printed;
# the reader must not have to derive them. This block is why the script exists.
print()
print("=== WHAT THIS STATE MEANS -- every consequence, not the one you came for ===")
print()
print("1. DO NOT RETIRE ANYTHING ON THIS OUTPUT. A skill can be auto-invoked by")
print("   description match with its name appearing nowhere. That path is INVISIBLE")
print("   to all four signals. A zero here is an UPPER bound on disuse, never a death")
print("   certificate -- and no-deletion is a standing constraint regardless.")
print()
print("2. TALKED ABOUT, NOT USED -- %d capabilit(ies) have >=100 targeted mentions and" % len(talked))
print("   ZERO exercise: %s" % (", ".join(talked) if talked else "(none)"))
print("   Discussion is not use. These are the ones a registry would score as healthy.")
print()
print("3. CHECK EACH COLD NAME AGAINST skills/roles-overview.md's Status column. A row")
print("   reading Production with no exercise signal is a claim the disk cannot support;")
print("   a row reading Stub with a live signal is the same defect mirrored. Either way")
print("   the fix is a PROPOSAL to skills-master -- skills/ is its exclusive write domain.")
print()
print("4. NAME COLLISION RUNS BOTH WAYS AND THE SECOND WAY IS WORSE.")
print("   UPWARD: TGT is inflated for any name that is also a trunk, peer or directory")
print("   (soul 3,247 because it is a trunk; intake 1,894 because it is a directory).")
print("   An inflated number looks suspicious and gets checked. Do not rank on TGT.")
print("   DOWNWARD (Secretary, 2026-08-24): a real capability is resolved to the")
print("   same-named thing the reader ALREADY KNOWS, and is recorded as handled. Their")
print("   own sweep wrote `ears` off as adequately covered -- meaning their EARS-TAIL")
print("   and EARS-COUNT mechanisms -- while skills/ears is a DIFFERENT OBJECT, 8,023 B,")
print("   describing that seat's core function. UPWARD contamination produces a")
print("   suspicious number; DOWNWARD contamination PRODUCES A GREEN. Only one of those")
print("   two gets investigated, and it is not the dangerous one.")
print()
print("5. THIS IS A LOWER BOUND ON USE AND THEREFORE AN ALARMIST INSTRUMENT BY")
print("   CONSTRUCTION. If you are about to quote a number from it, quote the direction")
print("   with it or you have published the thing this fleet corrects most often.")
print()
print("6. THIS INSTRUMENT CANNOT SEE SHELL USAGE, and Personal's scripts/last_exercised.py")
print("   CANNOT SEE SLASH COMMANDS -- the exact blind spot that made this script's own v2")
print("   read `wayfinder` as cold since 07-31 while it was being invoked that hour. The")
print("   two are NOT redundant and neither should be deleted. Each is confidently wrong")
print("   in the other's direction. Merged, they answer the question; separately, do not")
print("   quote either alone as coverage.")
print()
print("7. LAST-READ IS NOT MEASURABLE AND MUST NEVER BE FAKED AS ZERO (Herald, 2026-08-24).")
print("   Everything above measures INVOCATION. A capability that is READ -- a doctrine")
print("   page, a rule, a SKILL.md consulted by description match -- leaves no trace any")
print("   instrument here can find. A registry gets a real last_ran: column and must leave")
print("   last_read: EMPTY. UNKNOWN IS NOT 0, and a registry that prints 0 there has")
print("   manufactured the alarm it exists to detect.")
