#!/usr/bin/env python3
"""Generate ON-SKILLS.md sections 2 and 3 INTO THE BAKED COPY, from the pinned SHA.

WHY THIS EXISTS
---------------
`shelf/books/ON-SKILLS.md` ships with §2 (the catalog) and §3 (what is equipped) marked
"GENERATED AT BAKE", and NOTHING WAS GENERATING THEM. The book even tells the entity that an
empty §2 means the generator did not run -- so on first wake it would have read its own
warning. That is the same defect as the spec's `at_start` check pointed at a FILELIST.sha256
no step wrote: a promise with no producer.

DESIGN CONSTRAINTS, taken from LAUNCH-SPEC-V1.md §4.4 and honoured here:

* REGENERATE, NEVER COPY. The spec's own warning is that the on-disk skills digest carried a
  `last_regenerated` watermark SIX DAYS STALE under a header telling readers not to trust it.
  A bake that copies that file ships a six-day-old account of the skill surface and stamps a
  fresh SHA on it. This reads `skills/*/SKILL.md` AT THE PINNED SHA via `git show`.
* THE TRIGGER LINE IS VERBATIM -- the first sentence of the skill's own `description`, byte for
  byte. A paraphrase is a second copy that drifts from the original.
* WRITES ONLY THE BAKED COPY. The source `shelf/books/ON-SKILLS.md` keeps its placeholders,
  because in the source they are correct: they are generated.
* NO HARDCODED COUNT anywhere. Three different totals for the skill surface were measured
  within one hour on 2026-08-08 (spec 35, repo 34, deployed 33). The count is whatever the
  pinned tree holds.
"""
import argparse, re, subprocess, sys, pathlib

def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, encoding="utf-8").stdout

def first_sentence(desc):
    """First sentence, VERBATIM. Never reflowed, never trimmed of its own punctuation.

    ⛔ But a YAML BLOCK-SCALAR INDICATOR is not part of the sentence. `caveman` shipped its
    trigger as "> Ultra-compressed communication mode." on the first run, because its frontmatter
    uses `description: >` and the marker survived into the "verbatim" text. Verbatim means the
    author's words, not the serialisation format that carried them -- the same distinction as
    keeping Jon's typos while not keeping the quotes around his quoted line.
    """
    desc = re.sub(r"^\s*[>|][-+0-9]*\s*", "", desc)
    desc = " ".join(desc.split())
    m = re.search(r"^(.*?[.!?])(\s|$)", desc)
    return m.group(1) if m else desc

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True, help="the BAKED shelf dir (…/shelf)")
    ap.add_argument("--equipped", default="", help="comma-separated; from manifest.skills.equipped")
    a = ap.parse_args()

    paths = [p for p in git("-C", a.src, "ls-tree", "-r", "--name-only", a.ref, "skills/").splitlines()
             if p.endswith("/SKILL.md")]
    equipped = {s.strip() for s in a.equipped.split(",") if s.strip()}

    rows, missing_desc = [], []
    for p in sorted(paths):
        name = p.split("/")[-2]
        body = git("-C", a.src, "show", f"{a.ref}:{p}")
        m = re.search(r"^---\s*$(.*?)^---\s*$", body, re.S | re.M)
        fm = m.group(1) if m else ""
        d = re.search(r"^description:\s*(.+?)(?=^\w+:|\Z)", fm, re.S | re.M)
        if not d:
            missing_desc.append(name)
            trig = "⚠️ NO `description` IN FRONTMATTER — this skill cannot be triggered by the model."
        else:
            trig = first_sentence(d.group(1).strip().strip('"\''))
        eq = name in equipped
        # ⛔ THE PATH COLUMN USED TO ASSERT A FILE NOBODY WRITES. Reported by the resident,
        # 2026-08-10: "/shelf/skills/ does not exist … the four bodies are not in the image. So the
        # equipped set is equipped in the catalog and absent on disk." CONFIRMED — `docker/bake-out/
        # shelf/` holds only README.md, books/, continuity/, jon/. Nothing in the bake ever copied a
        # skill body, and this line printed the path anyway.
        # ⭐ The consequence it named is the sharp one: §7's "enforcement by absence" was enforcing
        # against the EQUIPPED skills too — the resident was told it holds four disciplines and given
        # none of their bodies.
        # ⚠️ THE FIX HERE IS HONESTY, NOT DELIVERY. Copying the bodies in would put four files into
        # the image AFTER GATE 5/6 have run, i.e. unscreened content in a screened artifact — the
        # exact defect class the gates exist for. Shipping them properly is a bake-ORDER change and
        # is filed as a ticket. Until then the column states what is true, checked per bake.
        body_on_disk = (pathlib.Path(a.out) / "skills" / name / "SKILL.md").is_file()
        if eq and body_on_disk:
            body_cell = f"/shelf/skills/{name}/SKILL.md"
        elif eq:
            body_cell = "⛔ EQUIPPED BUT BODY ABSENT FROM IMAGE — invoke by name; request the body by letter"
        else:
            # ⛔ CORRECTED 2026-08-13. This cell said "absent from image — request by letter" and
            # that became FALSE on 2026-08-12 when /skills was mounted read-only. The bodies ARE in
            # the container. A run that trusted this column would write a letter asking for a file it
            # could already open — and the 2026-08-13 resident reported exactly that risk, having
            # found the bodies itself with `find` in its first two minutes because nothing announced
            # them. ⭐ The mount is staged by stage_mounts.sh FROM THE SAME PINNED SHA this generator
            # reads, so every row here is readable at /skills/<name>/SKILL.md BY CONSTRUCTION — the
            # bake cannot observe the mount, but it does not need to: it defines it.
            # ⚠ The cell still carries a check rather than a bare claim, because a mount is a runtime
            # fact and a book that asserts one without a way to test it is how this column went wrong.
            body_cell = f"/skills/{name}/SKILL.md — **READABLE, not equipped** (verify: `ls /skills`)"
        # ⛔ THE THIRD STATE, added 2026-08-13 on the resident's proposal. Two states could not
        # express the situation that now holds for most of the tree: the body is reachable AND the
        # skill is not loaded. Collapsing that into CATALOG-ONLY understated its reach by 29 skills;
        # collapsing it into EQUIPPED would understate the fence. READABLE names the actual state.
        if eq:
            state = "EQUIPPED"
        elif body_cell.startswith("/skills/"):
            state = "READABLE (not equipped)"
        else:
            state = "CATALOG-ONLY"
        rows.append((name, trig, state, body_cell))

    cat = ["| skill | one-line trigger (VERBATIM) | state | body |", "|---|---|---|---|"]
    cat += [f"| `{n}` | {t} | {s} | {b} |" for n, t, s, b in rows]
    eq_rows = [r for r in rows if r[2] == "EQUIPPED"]

    s2 = ("<!-- GENERATED AT BAKE from the pinned SHA. Do not hand-edit. -->\n\n"
          f"**{len(rows)} skills in the pinned tree.** The *name* is the retrieval key; the *one line* is "
          "enough to decide whether you want it; **`body` is the honest statement that wanting is not "
          "having.**\n\n" + "\n".join(cat) + "\n")
    if missing_desc:
        s2 += ("\n⚠️ **%d skill(s) have NO `description` and therefore no trigger line: %s.** A skill with no "
               "description is callable by name and never auto-invoked — a documented silent-failure mode "
               "in this project.\n" % (len(missing_desc), ", ".join(f"`{m}`" for m in missing_desc)))

    s3 = ("<!-- GENERATED AT BAKE from manifest.skills.equipped. Do not hand-edit. -->\n\n"
          + (f"**You hold {len(eq_rows)}.**\n\n" + "\n".join(
              ["| skill | one-line trigger (VERBATIM) |", "|---|---|"]
              + [f"| `{n}` | {t} |" for n, t, _, _ in eq_rows]) + "\n"
             if eq_rows else
             "⛔ **NOTHING RESOLVED FROM THE MANIFEST'S EQUIPPED LIST.** Report this; it is a known defect, "
             "not a fault of yours.\n"))

    book = pathlib.Path(a.out) / "books" / "ON-SKILLS.md"
    txt = book.read_text(encoding="utf-8")
    for hdr, new in (("## 2 · The catalog", s2), ("## 3 · What you have equipped", s3)):
        i = txt.index(hdr); j = txt.index("\n## ", i + 1)
        # keep any ⚠️ known-defect prose already written under the header
        # ⛔ FIXED 2026-08-10 08:5x — THE RESIDENT FOUND THIS AND IT IS THE PUREST SPECIMEN WE HAVE.
        # The old line was:
        #     keep = "\n".join(l for l in txt[i:j].splitlines()
        #                      if l.startswith(("⚠️","⛔")) and "GENERATED" not in l)
        # It kept only lines that BEGIN with a warning glyph. The authored disclosure is a
        # paragraph — a ⚠️ headline followed by two lines of substance — so the generator preserved
        # "⚠️ **KNOWN DEFECT AT WRITING, recorded here rather than discovered by you at wake**" and
        # DELETED the sentence naming the defect. The baked book shipped a warning that warned of
        # nothing, with `## 4` on the next non-blank line.
        # ⭐ The resident's words, and they are exactly right: "A book whose stated purpose is honest
        # disclosure, with an empty disclosure block, is the specimen your own §6 is about."
        # ⚠️ The source file was never wrong. `shelf/books/ON-SKILLS.md:74-77` has the full paragraph.
        # THE BAKE ATE IT — which is worse than an authoring error, because the authored copy still
        # reads correctly and nobody comparing source to spec would ever see it.
        # Now keeps the whole BLOCK: a warning line plus every non-blank line that follows it.
        keep_lines, in_block = [], False
        for l in txt[i:j].splitlines():
            if l.startswith(("⚠️", "⛔")) and "GENERATED" not in l:
                in_block, _ = True, keep_lines.append(l)
            elif in_block and l.strip():
                keep_lines.append(l)
            else:
                in_block = False
        keep = "\n".join(keep_lines)
        txt = txt[:i] + hdr + "\n\n" + new + ("\n" + keep + "\n" if keep else "") + txt[j:]
    book.write_text(txt, encoding="utf-8")
    print(f"  [catalog] {len(rows)} skills, {len(eq_rows)} equipped"
          + (f", {len(missing_desc)} without a description" if missing_desc else ""))

if __name__ == "__main__":
    sys.exit(main())
