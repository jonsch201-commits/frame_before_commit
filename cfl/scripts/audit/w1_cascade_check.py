"""Would fixing E1_form on the 11 cheap pages ACTUALLY make them conformant?

⛔ THE TRAP. lint.py: `claims_blocked = is_session and "## Key Claims" not in body`, and E2/E3/E5
are graded N/A-BLOCKED when that is true. N/A counts as NON_FAIL. So a session page missing
`## Key Claims` is scored as failing ONE check (E1_form) while THREE others are suppressed.

⭐ Adding the heading fixes E1_form AND UNBLOCKS E2, E3, E5 -- which then get graded for real and
can FAIL. "One check from conformant" is therefore an ARTIFACT of a suppressed measurement, not a
promise. This asks what those three would grade if unblocked, using lint.py's own predicates.
"""
import glob, importlib.util, io, os, re, sys


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

really_one = truly_blocked = 0
detail = []
for path in pages:
    fm, body, text = lint.parse(path)
    slug = os.path.basename(path)[:-3]
    kind = lint.kind_of(fm, body, slug, path)
    C = lint.grade(path, fm, body, text, kind, MAIN_ROOT)
    fails = [k for k, v in C.items() if v not in lint.NON_FAIL]
    if fails != ["E1_form"]:
        continue
    if "session" not in kind:
        really_one += 1
        detail.append((slug, "non-session — no cascade", ""))
        continue

    # lint.py's own predicates, verbatim in intent
    has_turn_anchor = bool(re.search(r":T\d+", text))
    has_wikilink = bool(re.search(r"\[\[[^\]]+\]\]", text))
    has_fidelity = bool(re.search(
        r"\[(verbatim|paraphrase|reconstructed|contextual|inferred|uncaptured)\]", text))

    would_fail = []
    if not has_turn_anchor:
        would_fail.append("E2_anchor")
    if not has_fidelity:
        would_fail.append("E3_fidelity")
    if not has_wikilink:
        would_fail.append("E5_link")

    if would_fail:
        truly_blocked += 1
        detail.append((slug, "adding the heading EXPOSES", ",".join(would_fail)))
    else:
        really_one += 1
        detail.append((slug, "genuinely one edit away", ""))

print("Pages whose ONLY failing check is E1_form: %d" % len(detail))
print("  genuinely ONE edit from conformant : %d" % really_one)
print("  ⛔ would EXPOSE further failures    : %d" % truly_blocked)
print()
for slug, verdict, extra in detail:
    print("  %-52s %s %s" % (slug[:52], verdict, extra))
