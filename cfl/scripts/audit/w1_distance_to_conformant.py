"""How FAR is each page from conformant? -- the number nobody has computed.

W-1 reads as "236 pages do not conform", which sounds like 236 independent repairs. But
lint.py scores `conformant = all(checks non-failing)`, so non-conformance is a CONJUNCTION:
a page failing ONE check is one edit from the line, a page failing eight is a rewrite. The
closure test asks for 19/249 -- EIGHT more pages -- and picking the eight cheapest is a
completely different job from "fix 236 pages".

⛔ EVERY RULE COMES FROM lint.py ITSELF -- parse/kind_of/grade/NON_FAIL are imported and called,
never re-implemented. A second copy of the standard is exactly how the two drift, which is this
repo's named characteristic failure. The loop below mirrors lint.py's main() and nothing else.
"""
import collections, glob, importlib.util, io, os, re, sys


class _Mute(io.StringIO):
    # lint.py calls sys.stdout.reconfigure(); a plain StringIO has none and the import dies.
    # Muting a program must not hand it a less capable stdout.
    def reconfigure(self, *a, **k):
        return None


# lint.py does `import turn_index  # same dir`, which only resolves when scripts/audit is on the
# path. Running it as a script works; importing it from elsewhere does not. Put its own directory
# on sys.path rather than vendoring a copy.
sys.path.insert(0, os.path.abspath("scripts/audit"))

spec = importlib.util.spec_from_file_location("lintmod", "scripts/audit/lint.py")
lint = importlib.util.module_from_spec(spec)
_real, sys.stdout = sys.stdout, _Mute()
try:
    spec.loader.exec_module(lint)
finally:
    sys.stdout = _real
    # lint.py reconfigures stdout to utf-8 on import BECAUSE its glyphs are non-cp1252. Restoring
    # the original stdout throws that away, so the very lines that carry the finding die on a
    # star. Re-apply it to the real stream -- the same defect token_spend.py hit last night.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

MAIN_ROOT = os.path.abspath(".")
pages = sorted(p.replace("\\", "/") for p in glob.glob(f"{lint.WIKI}/**/*.md", recursive=True)
               if "/sources/" in p.replace("\\", "/"))

dist = collections.Counter()
cheap = []
blocked_by = collections.Counter()

for path in pages:
    fm, body, text = lint.parse(path)
    slug = os.path.basename(path)[:-3]
    kind = lint.kind_of(fm, body, slug, path)
    C = lint.grade(path, fm, body, text, kind, MAIN_ROOT)

    # anchor_range, exactly as main() computes it
    sf = fm.get("source_file", "")
    anchor_range = lint.NA_KIND
    raw_abs = os.path.join(MAIN_ROOT, sf) if sf and sf.lower() != "none" else None
    anchors = sorted(set(int(n) for n in re.findall(r":T(\d+)", text)))
    if anchors and raw_abs and os.path.isfile(raw_abs):
        try:
            count = lint.turn_index.index(raw_abs)["turn_count"]
            anchor_range = lint.FAIL if [n for n in anchors if n > count] else lint.PASS
        except Exception:
            anchor_range = "ERR"

    fails = [k for k, v in C.items() if v not in lint.NON_FAIL]
    if anchor_range not in lint.NON_FAIL:
        fails.append("anchor_range")

    dist[len(fails)] += 1
    if 1 <= len(fails) <= 2:
        cheap.append((len(fails), tuple(sorted(fails)), slug))
    if len(fails) == 1:
        blocked_by[fails[0]] += 1

tot = sum(dist.values())
print("PAGES BY NUMBER OF FAILING CHECKS   (0 = conformant)   n=%d" % tot)
run = 0
for k in sorted(dist):
    run += dist[k]
    print("  %2d failing : %4d pages    cumulative %4d (%5.1f%%)" % (k, dist[k], run, run * 100.0 / tot))

one = dist.get(1, 0)
two = dist.get(2, 0)
print("\n⭐ ONE CHECK FROM CONFORMANT: %d pages.   TWO CHECKS AWAY: %d pages." % (one, two))
print("   Closure test wants 19/249; today is %d. That is %d more pages."
      % (dist.get(0, 0), 19 - dist.get(0, 0)))
print("   %s" % ("ACHIEVABLE from the one-check bucket alone."
                 if one >= 19 - dist.get(0, 0) else
                 "NOT achievable from the one-check bucket alone."))

if blocked_by:
    print("\n   For pages blocked by exactly ONE check, that check is:")
    for k, v in blocked_by.most_common():
        print("     %4d pages blocked only by %s" % (v, k))

print("\n   Cheapest 14 pages:")
for n, fails, s in sorted(cheap)[:14]:
    print("     %d  %-34s %s" % (n, ",".join(fails), s[:52]))
