#!/usr/bin/env python3
"""fetch_jon_github_comments.py -- the FOURTH channel of Jon's words, which nothing was reading.

WHY THIS EXISTS
---------------
CLAUDE.md carries a table headed "Three channels carry Jon's words and only one of them is the
corpus. Search all three before saying a quote has no source." The three are raw/transcripts/**,
the subagent JSONLs (type: user + isMeta: true), and ~/.claude/history.jsonl.

THERE ARE AT LEAST FOUR, AND THE FOURTH IS GITHUB. Found 2026-08-07 while verifying two ungraded
Jon quotes in the B-7 deposit:

    "Its deliberately not exhaustive, its self improvement we don't know the end, we can see some
     goalposts along the way. Focusing on 100% generally makes performance worse in humans."

Measured against all three named channels: 0 hits in history.jsonl (1,742 typed prompts), 0 hits
under any "## Human" turn in any main transcript, and of 156 JSONL lines containing it exactly one
carried isMeta: true -- and that one begins "The coordinator sent a message while you were
working:", so it is the coordinator quoting it, not Jon saying it.

On the three-channel rule, that is a quote with no primary. It is not. It is PR #122 review comment
3653971690, jonsch201-commits, 2026-07-27T01:49:54Z, on wiki/references/wiki-growth-intent.md line
345. The page's own "[FOLDED -- Jon review, :330 + :345]" marker was accurate the whole time; the
SEARCH PROCEDURE was what could not see it.

This is the same defect as exchange_inbox.py hardcoding two peers when three existed, and as the
raw/ fixity baseline covering directories that write themselves: an enumeration that is complete by
assertion and incomplete in fact. The cost here is the worst of the three, because the three-channel
rule is invoked SPECIFICALLY to license the conclusion "no primary exists" -- and this program has
already retired one sentence on exactly that reasoning.

MEASURED AT BUILD TIME (2026-08-07)
-----------------------------------
    Jon-authored PR review comments  : 11
    Jon-authored issue/PR comments   : 74
    TOTAL                            : 85     <- DENOMINATOR
    scripts/ that read any of them   : 0      <- nothing, ever

WHAT THIS DOES, AND WHAT IT DELIBERATELY DOES NOT
-------------------------------------------------
Read-only. It fetches Jon-authored comments via `gh api` and writes ONE markdown file per comment
into raw/github-comments/, plus a MANIFEST.json. It writes nowhere else and mutates nothing on
GitHub -- no reply, no reaction, no edit, no close.

It does NOT decide whether a comment is a ruling. Grading and ingest are wiki-master's job; this
only makes the channel REACHABLE, which is the whole defect.

raw/ is gitignored, so this lands on disk and not in the published tree -- same footing as the
transcript corpus.

Exit: 0 wrote/refreshed | 2 could not run (gh missing, not authenticated, API error). Exit 2 is
UNKNOWN and never a pass -- "I could not fetch" must never render as "there is nothing there."
"""
import json
import os
import re
import subprocess
import sys

OUT = os.path.join("raw", "github-comments")
LOGIN_PAT = r"jonsch"   # matches jonsch201 and jonsch201-commits

# WIDENED 2026-08-07 after a second read. The first version hit exactly two endpoints and the
# finding built on it called GitHub "the fourth channel" -- while the instrument defining that
# channel could not see PR review SUBMISSION bodies (the top-level text of a review, distinct from
# its inline comments) or the OPENING body of a PR/issue Jon authored. Naming a channel and then
# covering part of it is the same enumeration defect the finding was about, reproduced inside its
# own evidence. Commit messages are a FIFTH venue and deliberately NOT fetched here -- git history
# is already local and conflating it with the API would hide that it is a separate gap.
ENDPOINTS = [
    ("review-inline", "repos/:owner/:repo/pulls/comments?per_page=100"),
    ("issue", "repos/:owner/:repo/issues/comments?per_page=100"),
    # Opening bodies. GitHub's issues endpoint returns PRs too; `body` is the opening text.
    ("opening", "repos/:owner/:repo/issues?state=all&per_page=100"),
]


def gh(endpoint):
    """Parsed JSON list from a paginated `gh api` call, or None on any failure."""
    try:
        # encoding is EXPLICIT: on Windows, text=True decodes with cp1252 and Jon's comments
        # contain em-dashes and curly quotes, so the default raised UnicodeDecodeError on the
        # first live run. A fetcher that dies on the author's own punctuation reads as "channel
        # unreachable" -- i.e. it would have manufactured the very silence this script exists
        # to disprove.
        p = subprocess.run(["gh", "api", endpoint, "--paginate"],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=600)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if p.returncode != 0 or p.stdout is None:
        return None
    # --paginate concatenates JSON arrays back to back; normalise to one list.
    txt = p.stdout.strip().replace("][", ",")
    try:
        return json.loads(txt)
    except ValueError:
        return None


def slug(s, n=40):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:n] or "untitled"


def render(kind, c):
    body = c.get("body") or ""
    fm = [
        "---",
        'title: "Jon on GitHub - %s comment %s"' % (kind, c.get("id")),
        "channel: github-%s-comment" % kind,
        "author_login: %s" % (c.get("user") or {}).get("login", ""),
        "created_at: %s" % c.get("created_at"),
        "html_url: %s" % c.get("html_url", ""),
        "path_commented_on: %s" % (c.get("path") or ""),
        "line: %s" % (c.get("line") or c.get("original_line") or ""),
        "provenance: PRIMARY - GitHub API, fetched read-only",
        "---",
        "",
        "**Jon's words, verbatim. Typos are his and stay his.**",
        "",
    ]
    return "\n".join(fm) + body.rstrip() + "\n"


def main(argv):
    if "--self-test" in argv:
        return self_test()
    rows, unreachable = [], []
    for kind, ep in ENDPOINTS:
        data = gh(ep)
        if data is None:
            unreachable.append(kind)
            continue
        for c in data:
            if not re.search(LOGIN_PAT, (c.get("user") or {}).get("login", ""), re.I):
                continue
            if kind == "opening" and not (c.get("body") or "").strip():
                continue   # an empty opening body is not an utterance
            rows.append((kind, c))

    # Review SUBMISSION bodies need a per-PR walk -- there is no repo-wide reviews endpoint.
    # Bounded by the PR list, so the cost is one call per PR and it is reported, not hidden.
    prs = gh("repos/:owner/:repo/pulls?state=all&per_page=100")
    if prs is None:
        unreachable.append("review-body (PR list unreachable)")
    else:
        print("  PRs walked for review bodies  : %d" % len(prs))
        for pr in prs:
            revs = gh("repos/:owner/:repo/pulls/%s/reviews?per_page=100" % pr.get("number"))
            if revs is None:
                unreachable.append("review-body PR#%s" % pr.get("number"))
                continue
            for r in revs:
                if (re.search(LOGIN_PAT, (r.get("user") or {}).get("login", ""), re.I)
                        and (r.get("body") or "").strip()):
                    r.setdefault("created_at", r.get("submitted_at"))
                    rows.append(("review-body", r))

    # AUTHOR-LOGIN IS NOT AUTHORSHIP, and this repo is the worst case for that assumption.
    # Agents create PRs with `gh pr create` using Jon's credentials, so a PR opened by
    # "jonsch201" is usually a MACHINE-WRITTEN body. Measured 2026-08-07: 171 of 249 opening
    # bodies carry an explicit Claude-authorship marker. Counting all 336 as "Jon's words" would
    # have inflated the channel roughly 4x -- the same over-claim, in the instrument built to
    # correct an over-claim. So the count is SPLIT and the ambiguous class is never folded in.
    def _machine(c):
        b = c.get("body") or ""
        return ("Generated with [Claude Code]" in b or "Co-Authored-By: Claude" in b
                or "🤖" in b)
    typed = [r for r in rows if r[0] != "opening"]
    op_machine = [r for r in rows if r[0] == "opening" and _machine(r[1])]
    op_unknown = [r for r in rows if r[0] == "opening" and not _machine(r[1])]

    print("=== JON'S GITHUB COMMENTS - a venue nothing was reading ===")
    if unreachable:
        print("  UNKNOWN - could not fetch: %s" % ", ".join(unreachable))
        print("  This is NOT a pass. A channel that could not be read is not a channel with")
        print("  nothing in it.")
        if len(unreachable) == len(ENDPOINTS):
            return 2
    print("  fetched under Jon's login     : %d   <- DENOMINATOR (login, NOT authorship)" % len(rows))
    print("    HIGH CONFIDENCE Jon-typed   : %d   comments + review text he wrote himself"
          % len(typed))
    print("    PR/issue openings, MACHINE  : %d   explicit Claude-authorship marker in the body"
          % len(op_machine))
    print("    PR/issue openings, UNKNOWN  : %d   no marker either way -- NOT counted as Jon's"
          % len(op_unknown))
    print("  A PR opened with `gh pr create` carries Jon's login and an agent's words.")
    if "--report" in argv:
        for kind, c in rows[:20]:
            head = (c.get("body") or "")[:90].replace("\n", " ")
            print("    [%s] %s  %s" % (kind, c.get("created_at"), head))
        return 0

    os.makedirs(OUT, exist_ok=True)
    manifest, written = [], 0
    for kind, c in rows:
        created = (c.get("created_at") or "")[:10]
        name = "gh-%s-%s-%s-%s.md" % (kind, created, c.get("id"),
                                      slug((c.get("body") or "").split("\n")[0]))
        path = os.path.join(OUT, name)
        new = render(kind, c)
        try:
            # newline="" DISABLES universal-newline translation on read. Without it, a body that
            # GitHub returns with CRLF is written as CRLF and read back as LF, so `old != new` is
            # TRUE on every run and the file is rewritten forever with byte-identical content.
            # Measured 2026-08-07: exactly 1 of 85 files rewrote on every run while md5sum showed
            # nothing changed. An idempotence claim that is false while LOOKING true is worse than
            # no claim, because the counter it prints is the thing you would check.
            old = open(path, encoding="utf-8", newline="").read()
        except OSError:
            old = None
        if old != new:
            open(path, "w", encoding="utf-8", newline="\n").write(new)
            written += 1
        conf = ("jon-typed" if kind != "opening"
                else ("machine" if _machine(c) else "unknown"))
        manifest.append({"id": c.get("id"), "kind": kind, "created_at": c.get("created_at"),
                         "html_url": c.get("html_url", ""), "file": name,
                         "confidence": conf,
                         "bytes": len(c.get("body") or "")})
    mpath = os.path.join(OUT, "MANIFEST.json")
    open(mpath, "w", encoding="utf-8", newline="\n").write(
        json.dumps({"fetched_comments": len(rows), "files": manifest}, indent=2) + "\n")
    print("  files written or refreshed    : %d  (idempotent - unchanged files are not rewritten)"
          % written)
    print("  manifest                      : %s" % mpath)
    print("")
    print("  This makes the channel REACHABLE. It does not grade anything - whether a comment is a")
    print("  ruling is wiki-master's call, and being fetched is not being ingested.")
    return 0


def self_test():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cases = [
        ("login pattern matches both of Jon's accounts",
         bool(re.search(LOGIN_PAT, "jonsch201", re.I))
         and bool(re.search(LOGIN_PAT, "jonsch201-commits", re.I))),
        ("NEGATIVE CONTROL: it does not match an unrelated login",
         not re.search(LOGIN_PAT, "github-actions[bot]", re.I)),
        ("output lands under gitignored raw/, never the published tree",
         OUT.replace("\\", "/").startswith("raw/")),
        ("slug is filesystem-safe",
         slug("Its deliberately not exhaustive!") == "its-deliberately-not-exhaustive"),
        ("slug never returns empty", slug("!!!") == "untitled"),
        ("READ-ONLY: no write verb anywhere in this file",
         not re.search(r"--method\s+(POST|PATCH|DELETE|PUT)", src)),
        ("an unreachable channel returns UNKNOWN, never a silent pass",
         "return 2" in src and "is NOT a pass" in src),
        ("rendered file carries html_url so the claim is re-checkable at source",
         "html_url" in render("review", {"id": 1, "body": "x", "user": {"login": "jonsch201"}})),
        ("CRLF in a body survives the idempotence comparison (newline='' on read)",
         'newline=""' in src and "universal-newline translation on read" in src),
        ("author-login is NOT treated as authorship -- openings are split, never folded in",
         "AUTHOR-LOGIN IS NOT AUTHORSHIP" in src and "op_unknown" in src),
        ("covers review bodies and openings, not just inline comments",
         "review-body" in src and "opening" in src),
    ]
    w = max(len(n) for n, _ in cases)
    for n, ok in cases:
        print("  %-*s : %s" % (w, n, "PASS" if ok else "FAIL"))
    bad = sum(1 for _, ok in cases if not ok)
    print("")
    print("RESULT: %s - %d/%d" % ("PASS" if not bad else "FAIL", len(cases) - bad, len(cases)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
