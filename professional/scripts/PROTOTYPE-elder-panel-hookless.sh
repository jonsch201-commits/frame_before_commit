#!/usr/bin/env bash
# BP-2 elder panel v2: run from a HOOKLESS cwd (the scratchpad), MCP restricted to an empty config, five in parallel, 15-min watchdog each.
# Measured 22:42: from the G: tree a plain `claude -p` hung >75 s (SessionStart hooks: lint 120 s, render 180 s, pipeline 900 s x2);
# from the scratchpad both a plain -p and a --resume --fork-session of the same session returned "ok" in <60 s. --resume resolves the UUID across project dirs.
OUT="N:/claude-professional/evidence/elders/2026-09-05-BP2-oaths"
cd "C:/Users/JonSc/AppData/Local/Temp/claude/N--claude-professional/5f0ee997-6a2f-4e7d-9612-81fda4bf8823/scratchpad" || exit 9
printf '{"mcpServers":{}}' > "$OUT/empty-mcp.json"
Q='You are being consulted read-only as an ELDER of the Professional trunk (a forked resume; nothing persists except this reply). LABEL EVERY ANSWER: [carried] = you hold it from the session itself. [re-read] = you are reconstructing from files loaded now; a [re-read] answer is worth strictly less and must say so. Answer in this exact schema, one block per oath you swore or were bound by in your window (especially ones never written to a file), then the two closing blocks. Do not summarise the project. Do not invent an oath you did not hold. Stop after UNFINISHED.
OATH: <verbatim as sworn, or the closest wording you actually used>
WHERE: <file path, or "in conversation only" with approximate date/time>
KIND: <method | restraint | confession | other>
KEPT/BROKEN: <one instance, what happened>
WHAT-CHECK-WOULD-CATCH-A-BREACH: <one concrete check over files that could FAIL: population, planted-breach control>
DISAGREEMENTS: <where your oath conflicts with CLAUDE.md, WAKE.md, or a peer letter — unmerged>
UNFINISHED: <what you left undone that your descendant should know first>'
run_one() {
  S="$1"
  date "+%F %T start ${S:0:8} (scratch cwd, no hooks)" >> "$OUT/rc.log"
  claude --resume "$S" --fork-session --permission-mode plan --strict-mcp-config --mcp-config "$OUT/empty-mcp.json" --no-chrome -p "$Q" > "$OUT/elder-${S:0:8}.txt" 2> "$OUT/elder-${S:0:8}.err" &
  CP=$!
  for i in $(seq 1 90); do sleep 10; kill -0 $CP 2>/dev/null || break; done
  if kill -0 $CP 2>/dev/null; then kill $CP; echo "TIMEOUT 900s $(date '+%F %T') ${S:0:8}" >> "$OUT/rc.log"
  else wait $CP; echo "rc=$? $(date '+%F %T') ${S:0:8} bytes=$(wc -c < "$OUT/elder-${S:0:8}.txt")" >> "$OUT/rc.log"; fi
}
for S in bdbb3dc0-2fe0-4c23-820a-3416f385231a e8f94111-c511-494b-85b2-d68c261eedb9 a90e0dcc-79ea-4237-8a6c-0f46d34e8be2 20690e2b-9d74-4a97-81e2-dc46e796d26b 592c3c16-bf91-471a-a5c1-b11f573b8918; do
  run_one "$S" &
done
wait
echo "PANEL v2 DONE $(date '+%F %T')" >> "$OUT/rc.log"
wc -c "$OUT"/elder-*.txt
