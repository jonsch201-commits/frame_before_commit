"""Is the 108-page mode ONE cohort failing the SAME six checks, or 108 different sixes?

⛔ I ASSERTED "one cohort with one shared history, not scatter" IN A DELIVERED LETTER AND NEVER
CHECKED IT. The distribution shows 108 pages failing SIX checks; it says nothing about WHICH six.
If it is one signature, W-1's bulk is one systematic fix. If it is 108 different combinations, it
is 108 judgements. Those are different projects and I published the optimistic reading.
"""
import collections, glob, importlib.util, io, os, re, sys


class _Mute(io.StringIO):
    def reconfigure(self, *a, **k):
        return None


sys.path.insert(0, os.path.abspath("scripts/audit"))
spec = importlib.util.spec_from_file_location("lintmod", "scripts/audit/lint.py")
lint = importlib.util.module_from_spec(spec)
_real, sys.stdout = sys.stdout, _Mute()
try:
    spec.loader.exec_module(lint)
finally:
    sys.stdout = _real
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

MAIN_ROOT = os.path.abspath(".")
pages = sorted(p.replace("\\", "/") for p in glob.glob(f"{lint.WIKI}/**/*.md", recursive=True)
               if "/sources/" in p.replace("\\", "/"))

sig = collections.Counter()
sig_by_n = collections.defaultdict(collections.Counter)
kinds = collections.defaultdict(collections.Counter)

for path in pages:
    fm, body, text = lint.parse(path)
    slug = os.path.basename(path)[:-3]
    kind = lint.kind_of(fm, body, slug, path)
    C = lint.grade(path, fm, body, text, kind, MAIN_ROOT)
    fails = tuple(sorted(k for k, v in C.items() if v not in lint.NON_FAIL))
    sig[fails] += 1
    sig_by_n[len(fails)][fails] += 1
    kinds[len(fails)][kind] += 1

print("MOST COMMON FAILURE SIGNATURES (exact set of failing checks)")
for s, c in sig.most_common(8):
    print("  %4d pages  n=%d  %s" % (c, len(s), ",".join(x.split("_")[0] for x in s) or "(none)"))

print("\nWITHIN THE 6-FAILING BUCKET:")
six = sig_by_n[6]
tot6 = sum(six.values())
print("  %d pages, %d DISTINCT signatures" % (tot6, len(six)))
for s, c in six.most_common(5):
    print("    %4d  %s" % (c, ",".join(x.split("_")[0] for x in s)))
if six:
    top = six.most_common(1)[0][1]
    print("  -> largest single signature covers %d of %d (%.0f%%)" % (top, tot6, top * 100.0 / tot6))
    print("  VERDICT: %s" % ("ONE COHORT -- a systematic fix" if top / tot6 > 0.8
                             else "NOT one cohort -- my published claim was too strong"))

print("\n  page kinds in that bucket:", dict(kinds[6]))
