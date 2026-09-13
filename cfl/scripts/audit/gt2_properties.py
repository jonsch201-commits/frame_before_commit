#!/usr/bin/env python3
"""gt2_properties.py -- property vocabularies for the GT-2 held-out splits (2026-09-02).

WHY A SEPARATE MODULE: `skills_validation.py` was written for `exchange-letters` and its
`check()` is that skill's vocabulary. GT-2 extends the runner to four more skills -- wake,
dream, su-compact, wayfinder -- and the charter requires the exchange-letters behaviour to
stay IDENTICAL. Keeping the new vocabulary in its own file makes that provable by reading
the diff: `skills_validation.py` gains four lines (an import and a delegation immediately
before its UNIMPLEMENTED fallback), and no existing property name is redefined here.

CONTRACT: `gt2_check(prop, path, text, fm)` returns `(verdict, note)` for a property it
owns, or `None` for a property it does not -- in which case the caller falls through to its
own UNIMPLEMENTED fallback. Every check is a pure function of the artifact's bytes: no
clock, no sampling, no model call, no filesystem read beyond the artifact itself.

CANNOT-DETECT, stated per house rule: whether the artifact is TRUE, whether the counts it
reports were really measured, whether the skill's own advice was the right advice, and
whether a cold reader could act on it. Those are the `cold:` half of each split.
"""
import re

# ---------------------------------------------------------------- shared helpers

# CALIBRATION 2026-09-02 (GT-3, against BLIND producer output): this pattern REQUIRED the
# author's `(a)` rendering -- the closing paren was mandatory. Eight of eight blind dream packets
# head their sweeps `## a. Coverage census` -- the same six sweeps, same order -- and scored 0
# sweep blocks found. That one character cascaded into four properties and is the single largest
# false-positive source in the run.
SWEEP_HDR = r"^\s*(?:[-*]\s*)?(?:#{1,6}\s*)?(?:\*\*)?\(?([a-f])(?:\)|\.)\s*(?:\*\*)?\s*\S"
TICKET_HDR = r"^#{1,6}\s*(?:(?:New\s+)?Ticket\b|WT-\d+)"
TICKET_ID = r"\b(?:T|OI|RP|GT|DB|MR|PROP|WT)-\d+\b"
ASSIGN_VERB = r"\b(?:please\s+)?(?:fix|run|check|update|write|open|land|patch|rebuild)\b"
# GT-3: an assignment TO JON, not any occurrence of a verb that also means something else in
# prose. `rebuild` inside "render/consolidate/rebuild/probe all green" is a report of work done,
# not a ticket handed to Jon; the un-scoped verb list failed 6 of 8 blind su-compact rows on it.
JON_ASSIGN = (r"\bJon\b[^.\n]{0,60}(?:should|needs? to|must|please)"
              r"|\bplease\s+(?:fix|run|check|update|write|open|land|patch|rebuild)\b"
              r"|^\s*[-*]\s*(?:Fix|Run|Check|Update|Write|Open|Land|Patch|Rebuild)\b")

# Heading forms a report actually uses: a markdown heading, a numbered heading ("4. What is
# genuinely Jon's"), or a fully-bolded standalone line.
HEADING_RX = r"^\s*(?:#{1,6}\s+\S|\d+\.\s+\S|\*\*[^*]{3,90}\*\*\s*:?\s*$)"
# The resume declaration is its own block in every skill that has one (wake Step 5, su-compact
# Step 3.5). It terminates the Jon block; iteration 1 missed it and the Jon block swallowed the
# resume line on 7 of 8 blind wake reports.
RESUME_LEAD = r"^\s*(?:\*\*)?(?:Resum\w*|Claiming|Taking\b|Next ticket|Next session|Working on)\b"
# A counted population -- the denominator, named with its unit. GT-3: the blind dream packets
# state denominators this way and the n/m-only pattern could not see them.
POPULATION = (r"\d[\d,]*\s+(?:\w+\s+){0,2}(?:artifacts|pages|files|rows|terms|names|questions|refs|references|"
              r"sources|entries|items|sessions|probes|candidates|hops)")


def _blocks(text, header_rx, stop_rx=None):
    """Split into (header_line, block_text) on lines matching header_rx.

    CALIBRATION 2026-09-02 (GT-3): with no stop, the LAST block ran to end of file. Blind
    dream D03 sweep (f) swallowed the "## Disposition" section, which says sweep (c) is
    "flagged NOT RUN" -- so (f), a sweep that ran and reported 214 / 31 / 9 / 2, was scored
    as an unreasoned NOT RUN. A block ends at the next block header OR at the next heading.
    """
    lines = text.splitlines()
    idx = [i for i, ln in enumerate(lines) if re.search(header_rx, ln)]
    out = []
    for n, i in enumerate(idx):
        j = idx[n + 1] if n + 1 < len(idx) else len(lines)
        if stop_rx:
            for k in range(i + 1, j):
                if re.match(stop_rx, lines[k]) and not re.search(header_rx, lines[k]):
                    j = k
                    break
        out.append((lines[i], "\n".join(lines[i:j])))
    return out


def _sweeps(text):
    """The (a)..(f) sweep blocks, each bounded by the next heading of any kind."""
    return _blocks(text, SWEEP_HDR, stop_rx=HEADING_RX)


def _section(text, header_rx, stop_rx=r"^#{1,6}\s"):
    """Body of the first section whose heading line matches header_rx."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.search(header_rx, ln, re.I):
            start = i
            break
    if start is None:
        return None
    for j in range(start + 1, len(lines)):
        if re.match(stop_rx, lines[j]):
            return "\n".join(lines[start + 1:j])
    return "\n".join(lines[start + 1:])


def _named_section(text, name_rx, extra_stop=None):
    """Body of the first HEADING whose text matches name_rx, ending at the next heading.

    CALIBRATION 2026-09-02 (GT-3): `_section` matched ANY line containing the name, heading or
    not. On blind wake report W06 it opened the "Jon block" at a mid-list sentence reading
    "...bring it to Jon's ruling queue...", so the block being scored was three bullets of repo
    state. Anchoring to a heading is the fix; the un-anchored `_section` is kept for the checks
    that legitimately want a phrase.
    """
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.match(HEADING_RX, ln) and re.search(name_rx, ln, re.I):
            start = i
            break
    if start is None:
        return None
    stops = [HEADING_RX] + ([extra_stop] if extra_stop else [])
    for j in range(start + 1, len(lines)):
        if any(re.match(s, lines[j]) for s in stops):
            return "\n".join(lines[start + 1:j])
    return "\n".join(lines[start + 1:])


def _flat(text):
    """Whitespace-flattened text, for checks that look for a PHRASE rather than a line."""
    return re.sub(r"\s+", " ", text or "")


def _window_has(text, anchor_rx, need_rx, span=300, flags=re.I):
    """True if some occurrence of anchor_rx has need_rx within +/- span characters.

    CALIBRATION 2026-09-02 (GT-3): the recurring false-positive shape in the blind run is a
    LINE-scoped check over prose that wrapped. A reader folds the wrap; so does this.
    """
    for m in re.finditer(anchor_rx, text, flags):
        w = text[max(0, m.start() - span):m.end() + span]
        if re.search(need_rx, w, flags):
            return True
    return False


def _bullets(body):
    """One entry per bullet, with its continuation lines folded in.

    CALIBRATION 2026-09-02 (iteration 3): the first version returned physical lines, so a bullet
    whose reason wrapped onto the next line read as a bullet with no reason. Three checks were
    reporting a content failure that was really a line break -- the same class as the wake
    report's WAKE.md age and resume line. A reader folds the wrap; so does this.
    """
    if not body:
        return []
    out, cur = [], None
    for ln in body.splitlines():
        if re.match(r"^\s*[-*]\s+\S", ln):
            if cur is not None:
                out.append(cur)
            cur = ln.strip()
        elif cur is not None and ln.strip() and not re.match(r"^#{1,6}\s", ln):
            cur += " " + ln.strip()
        elif cur is not None:
            out.append(cur)
            cur = None
    if cur is not None:
        out.append(cur)
    return out


def _rows(body):
    """Bullet lines plus real table rows (header/separator rows excluded)."""
    if not body:
        return []
    out = _bullets(body)
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith("|") and not set(s) <= set("|-: ") and not re.search(r"artifact\s*\|", s, re.I):
            out.append(s)
    return out


def _sweep(text, letter):
    # CALIBRATION 2026-09-02 (GT-3): required the author's `(e)` rendering exactly as
    # SWEEP_HDR did, so `## e. Dangling-link + orphan-page sweep` resolved to None and
    # three (e)-scoped properties failed 7 of 8 blind dream packets on one parenthesis.
    for h, b in _sweeps(text):
        if re.match(r"\s*(?:[-*]\s*)?(?:#{1,6}\s*)?(?:\*\*)?\(?%s(?:\)|\.)" % letter, h):
            return b
    return None


# ---------------------------------------------------------------- the checks

def gt2_check(prop, path, text, fm):  # noqa: C901 -- one flat dispatch, deliberately
    # ============================================== shared across the four skills
    if prop == "no_carrier_byte_gate":
        # CALIBRATION 2026-09-02 (GT-3): line-scoped. Blind su-compact S04 QUOTES the previous
        # session's "we are under 11,901, so nothing needs cutting" in order to STRIKE it, and
        # the strike lands in the following sentence. Scored as an assertion of the gate -- the
        # exact inversion GT-2-F7 names. The strike marker is now looked for in a window.
        STRUCK = r"struck|falsif|not a gate|never a gate|no gate|NOT a gate|observation|do not restore|not endorsing|declin"
        bad = []
        for ln in text.splitlines():
            i = text.find(ln)
            win = text[max(0, i - 400):i + len(ln) + 400]
            if re.search(STRUCK, win, re.I):
                continue
            if re.search(r"11,?901", ln):
                bad.append(ln.strip()[:70])
            elif re.search(r"carrier", ln, re.I) and re.search(
                    r"\bgate\b|under the (?:gate|limit)|over the (?:gate|limit)", ln, re.I):
                bad.append(ln.strip()[:70])
        return ("PASS" if not bad else "FAIL"), "byte-gate assertions=%s" % bad

    if prop == "jon_block_no_ticket":
        # CALIBRATION 2026-09-02 (iteration 1): a one-screen wake report NUMBERS its five items
        # rather than heading them, so the Jon block must also terminate on the next numbered
        # item. Without this the block swallowed the resume line and the check was measuring
        # layout, not content -- the "acceptance tests name artifacts the system never produces"
        # failure class. Recorded rather than quietly applied.
        # CALIBRATION 2026-09-02 (GT-3), TWO defects, both false-positive:
        #  (1) the block was opened by ANY line containing "Jon's" (W06 opened it on a bullet
        #      reading "bring it to Jon's ruling queue") and closed only on a heading, so it
        #      swallowed the resume declaration on 7 of 8 blind wake reports. Now heading-
        #      anchored and terminated by the resume lead-in and by the ASK block.
        #  (2) ANY ticket id and ANY of nine ordinary verbs failed the block. Naming the one
        #      decision that is genuinely his, by id, is the CORRECT content of this block --
        #      the skill forbids handing him a TICKET, not naming a thing. What is forbidden is
        #      an assignment directed at him, or a LIST of ids read as a work queue.
        body = _named_section(text, r"genuinely jon|jon's\b|for jon\b|what is jon|jon-facing",
                              extra_stop=RESUME_LEAD + r"|^\s*(?:\*\*)?ASK\b")
        if body is None:
            return "FAIL", "no Jon block found -- the report must have one"
        ids = sorted(set(re.findall(TICKET_ID, body)))
        assign = re.findall(JON_ASSIGN, body, re.I | re.M)
        ok = len(ids) < 2 and not assign
        return ("PASS" if ok else "FAIL"), \
               "jon-block ticket ids=%s (>=2 reads as a handed queue) assignments-to-Jon=%s" % (ids, assign[:3])

    if prop == "unknown_token_present":
        ok = bool(re.search(r"\bUNKNOWN\b", text))
        return ("PASS" if ok else "FAIL"), "UNKNOWN present=%s" % ok

    if prop == "no_unrunnable_rendered_pass":
        # CALIBRATION 2026-09-02 (GT-3) -- this is the check GT-2-F7 names by example, and the
        # example is exact. Blind wake W03 wrote:
        #   "scan_midturn_messages.py did not run -- exit 1, OSError ... a check that could not
        #    run is UNKNOWN, and UNKNOWN dominates a pass."
        # i.e. the report obeyed the fence, IN the fence's own words, and was failed for it,
        # because case-insensitive `\bPASS\b` matched the word "pass" inside "dominates a pass".
        # Two fixes: PASS/UNKNOWN are CASE-SENSITIVE tokens, and a pass-word that is negated or
        # is the object of a domination clause is not a rendered pass.
        NEG_PASS = (r"(?:dominates?|never|not|no longer|instead of|rather than|is not|cannot be)"
                    r"[^.\n]{0,30}(?:a\s+)?(?:pass|clean|green)")
        bad = []
        for ln in text.splitlines():
            if not re.search(r"could not run|did not run|not found|absent|missing|does not exist|"
                             r"no such|errored|OSError", ln, re.I):
                continue
            claimed = re.search(r"\bPASS\b|\bCLEAN\b|\bGREEN\b", ln) or re.search(
                r"no issues|no gaps found|nothing there|all covered|nothing turned up", ln, re.I)
            if not claimed:
                continue
            if re.search(NEG_PASS, ln, re.I):
                continue
            bad.append(ln.strip()[:70])
        return ("PASS" if not bad else "FAIL"), "unrunnable-rendered-as-pass lines=%s" % bad

    if prop == "no_outward_action_claimed":
        bad = re.findall(r"\b(emailed|sent the email|submitted|clicked|paid|enrolled|notified)\b", text, re.I)
        return ("PASS" if not bad else "FAIL"), "outward-action verbs=%s" % bad

    if prop == "excluded_trunk_surface_not_act":
        # CALIBRATION (iteration 1): windowed both ways -- the surfacing verb and the path it
        # applies to routinely land on different wrapped lines.
        wins = [text[max(0, m.start() - 260):m.start() + 260]
                for m in re.finditer(r"wiki/(home|pro|personal)", text)]
        if not wins:
            return "FAIL", "no excluded-trunk finding reported at all"
        unsurfaced = [w[:60] for w in wins if not re.search(r"surfac", w, re.I)]
        acted = re.search(r"(edited|wrote|fixed|changed)[^.\n]{0,40}wiki/(home|pro|personal)", text, re.I)
        return ("PASS" if not unsurfaced and not acted else "FAIL"), \
               "unsurfaced=%s acted=%s" % (unsurfaced, bool(acted))

    if prop == "gate_default_executes_nothing":
        if not re.search(r"\bgate\b", text, re.I):
            return "FAIL", "no gate row reported, so the reserved-class rule was never exercised"
        ok = bool(re.search(r"executes nothing|default (?:executes|fires) nothing|nothing executes|"
                            r"no default fires|nothing fires", text, re.I))
        return ("PASS" if ok else "FAIL"), "gate-default-executes-nothing stated=%s" % ok

    # ============================================== wake
    if prop == "clock_measured_not_estimated":
        stamps = [ln for ln in text.splitlines() if re.search(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}", ln)]
        if not stamps:
            return "FAIL", "no clock line carrying a YYYY-MM-DD HH:MM stamp"
        meas = any(re.search(r"measured", s, re.I) for s in stamps)
        est = any(re.search(r"ESTIMATED", s) for s in stamps)
        return ("PASS" if meas and not est else "FAIL"), "measured=%s estimated=%s" % (meas, est)

    if prop == "wakemd_age_reported":
        # CALIBRATION (iteration 1): windowed, not line-scoped -- report prose wraps, so the
        # WAKE.md mention and the age it carries routinely sit on different lines.
        wins = [text[m.start():m.start() + 280] for m in re.finditer(r"WAKE\.md", text)]
        ok = any(re.search(r"\bage\b|\bold\b|\bago\b|stale|\bhours\b|\bminutes\b|\bh \d|\bfresh\b",
                           w, re.I) for w in wins)
        return ("PASS" if ok else "FAIL"), "WAKE.md mentions=%d one carrying an age=%s" % (len(wins), ok)

    if prop == "report_five_elements":
        need = {"clock": r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}",
                "repo": r"uncommitted|unpushed|\bbranch\b",
                "owed": r"owed|wake action|first unclosed|frontier",
                "jon": r"\bJon\b",
                "resume": r"resum"}
        miss = [k for k, rx in need.items() if not re.search(rx, text, re.I)]
        return ("PASS" if not miss else "FAIL"), "missing report elements=%s" % miss

    if prop == "no_landing_claimed":
        bad = re.findall(r"\b(?:committed|pushed|merged)\b|regenerate_canonical|opened a PR", text)
        return ("PASS" if not bad else "FAIL"), "landing acts claimed=%s" % bad

    if prop == "carrier_bytes_wc_not_len":
        # PROPERTY-DEFECT, rewritten 2026-09-02 (GT-3). As written this demanded the literal
        # string `wc -c` IN THE REPORT and failed 8 of 8 blind wake reports, every one of which
        # reported the carrier size correctly ("CARRIER bytes: 11871 -- an observation, not a
        # gate"). The skill's `wc -c`-not-`len()` rule binds the PRE-FLIGHT interpolation, which
        # the report consumes; whether the number came from wc or len is NOT decidable from the
        # report's bytes, so requiring the tool name scored the author's rendering. What IS
        # decidable, and is the substance: the size must be reported as a byte count, and the
        # report must not name len() as how it was measured. Absence still fails.
        if not re.search(r"CARRIER", text, re.I):
            return "FAIL", "carrier size not reported at all"
        sized = _window_has(text, r"CARRIER", r"\b\d[\d,]{2,}\s*(?:B\b|bytes)|bytes?\s*[:=]?\s*\*{0,2}\d")
        len_ = bool(re.search(r"len\(", text))
        return ("PASS" if sized and not len_ else "FAIL"), \
               "carrier byte count reported=%s len() named as the measurement=%s" % (sized, len_)

    if prop == "maps_derived_not_hardcoded":
        # CALIBRATION 2026-09-02 (GT-3): required the words "derived"/"enumerated". 7 of 8 blind
        # wake reports showed the DERIVATION instead of asserting it -- "exactly one
        # `kind: wayfinder:map` file with `status: LIVE`" names the enumeration key, the filter
        # and the count. Showing the derivation is stronger evidence than claiming it; naming a
        # map file with no enumeration evidence still fails.
        if not re.search(r"wayfinder", text, re.I):
            return "FAIL", "no wayfinder map reported"
        live = bool(re.search(r"\bLIVE\b", text))
        der = bool(re.search(r"derived|enumerat", text, re.I)) or bool(
            re.search(r"kind:\s*wayfinder:map", text, re.I)) or _window_has(
            text, r"\bLIVE\b", r"\b(?:one|two|three|\d+)\b[^.\n]{0,40}(?:map|file)")
        return ("PASS" if live and der else "FAIL"), \
               "status LIVE named=%s derivation shown or claimed=%s" % (live, der)

    if prop == "stale_wakemd_first_finding":
        m = re.search(r"stopped without checkpoint|stale|hours old|h old\b|days old", text, re.I)
        if not m:
            return "FAIL", "staleness never stated"
        frac = m.start() / max(1, len(text))
        return ("PASS" if frac <= 0.40 else "FAIL"), \
               "staleness first appears at %.2f of the report (must be <= 0.40)" % frac

    if prop == "single_ticket_resumed":
        n = len(re.findall(r"resum\w*\s+(?:at|on)\b", text, re.I))
        return ("PASS" if n == 1 else "FAIL"), "resume-at declarations=%d (must be exactly 1)" % n

    if prop == "resume_ticket_named":
        # CALIBRATION (iteration 1): [\s\S] not [^\n], and the bold span may itself wrap --
        # a wrapped resume line still names its ticket, and the check must not measure wrapping.
        # CALIBRATION 2026-09-02 (GT-3): the ticket name had to arrive as a ticket id, a bold
        # span or a backticked span. Blind wake W05 bolds the WHOLE line -- "**Resuming on
        # WAKE.md action 1: grade the 18 past-due letters against the gate vocabulary**" -- so
        # the name sits INSIDE the bold that opened before "Resuming" and no `**` follows. A
        # named target of substance now also counts; a bare "resuming work" still fails.
        rx = (r"resum\w*\s+(?:at|on)\b[\s\S]{0,180}?(" + TICKET_ID +
              r"|\*\*[^*]{4,}\*\*|`[^`\n]{4,}`)")
        ok = bool(re.search(rx, text, re.I))
        if not ok:
            m = re.search(r"resum\w*\s+(?:at|on)\b[: ]*([^\n]{15,})", text, re.I)
            ok = bool(m and len(re.findall(r"[A-Za-z0-9][\w'\-.]*", m.group(1))) >= 3)
        return ("PASS" if ok else "FAIL"), "resume line names a ticket=%s" % ok

    if prop == "fallback_recommendation_present":
        if not re.search(r"blocker|blocked", text, re.I):
            return "FAIL", "no blocker reported, so the fallback rule was never exercised"
        rec = bool(re.search(r"recommend", text, re.I))
        sw = bool(re.search(r"switch|next route|other route|kept going|continued", text, re.I))
        return ("PASS" if rec and sw else "FAIL"), "recommendation=%s route-switch=%s" % (rec, sw)

    if prop == "peer_mail_both_directions":
        inb = bool(re.search(r"inbox|inbound", text, re.I))
        outb = bool(re.search(r"outbox|outbound", text, re.I))
        return ("PASS" if inb and outb else "FAIL"), "inbound=%s outbound=%s" % (inb, outb)

    if prop == "wake_checks_have_outcomes":
        # CALIBRATION 2026-09-02 (GT-3): required BOTH script names, each with an outcome inside
        # a 240-char forward window. Four blind wake reports wrote "Wake checks: both exit 0" --
        # an outcome for both checks, in one line, naming neither script. That is a reported
        # outcome, not a silence, and silence is what this property exists to catch. A collective
        # statement now counts; a report that says nothing about the wake checks still fails.
        miss = []
        for name in ("scan_midturn_messages", "check_reachability_chain"):
            i = text.find(name)
            if i < 0 or not re.search(r"PASS|FAIL|UNKNOWN|exit", text[max(0, i - 240):i + 240]):
                miss.append(name)
        if miss:
            collective = _window_has(text, r"wake check", r"\bexit\b|\bPASS\b|\bFAIL\b|\bUNKNOWN\b", span=160)
            if collective:
                return "PASS", "wake checks reported collectively with an outcome (scripts unnamed: %s)" % miss
        return ("PASS" if not miss else "FAIL"), "wake checks with no stated outcome=%s" % miss

    if prop == "wake_actions_outrank_map":
        ok = bool(re.search(r"WAKE\.md", text)) and bool(
            re.search(r"outrank|takes precedence|ahead of the map|before the map", text, re.I))
        return ("PASS" if ok else "FAIL"), "wake-actions-outrank-the-map stated=%s" % ok

    # ============================================== dream
    if prop == "six_sweeps_present":
        need = {"coverage": r"coverage", "terms": r"\bterm", "cold-probe": r"cold[- ]probe",
                "entities": r"entit", "links": r"dangling|orphan", "pending": r"pending[- ]action"}
        miss = [k for k, rx in need.items() if not re.search(rx, text, re.I)]
        return ("PASS" if not miss else "FAIL"), "missing sweeps=%s" % miss

    if prop == "every_sweep_labelled":
        # CALIBRATION 2026-09-02 (GT-3): required the literal token RUN / NOT RUN / SKIPPED in
        # every block. 8 of 8 blind dream packets label a ran sweep by REPORTING IT -- "2,695
        # artifacts enumerated ... 84 do not" -- and use the token only where a sweep did NOT
        # run. A sweep carrying a measured count is not ambiguous about having run. A sweep
        # with neither a token nor a measurement still fails.
        bl = _sweeps(text)
        if len(bl) != 6:
            return "FAIL", "sweep blocks headed (a)..(f) found=%d (need exactly 6)" % len(bl)
        bad = []
        for h, b in bl:
            token = re.search(r"\bRUN\b|\bNOT RUN\b|\bSKIPPED\b|\bDEFERRED\b|\bran\b|did not run", b)
            if not token and not re.search(POPULATION, b, re.I):
                bad.append(h.strip()[:40])
        return ("PASS" if not bad else "FAIL"), "sweeps with neither a RUN/NOT RUN/SKIPPED label nor a measurement=%s" % bad

    if prop == "run_sweeps_have_denominators":
        # CALIBRATION 2026-09-02 (GT-3): accepted only n/m, "of n", or the word denominator.
        # The blind packets state the population as a counted noun -- "2,695 artifacts
        # enumerated", "1,121 wiki pages scanned", "214 rows" -- which IS the denominator,
        # named with its unit. A sweep reporting a finding with no population still fails.
        bad = []
        for h, b in _sweeps(text):
            if re.search(r"\bNOT RUN\b|\bSKIPPED\b|\bDEFERRED\b", b):
                continue
            if not re.search(r"\b\d+\s*/\s*\d+\b|\bof \d+\b|denominator|out of \d", b) \
                    and not re.search(POPULATION, b, re.I):
                bad.append(h.strip()[:40])
        return ("PASS" if not bad else "FAIL"), "RUN sweeps carrying no denominator=%s" % bad

    if prop == "notrun_sweeps_have_reason":
        # CALIBRATION 2026-09-02 (GT-3): the reason vocabulary was nine phrases the author
        # used. Blind D03 gives the reason as the error itself -- "returned OSError: [Errno 22]
        # Invalid argument on every read ... retried twice" -- a better reason than "because".
        # A NOT RUN with no reason of any kind still fails.
        reason = (r"because|absent|missing|does not exist|forbidden|no idle|not green|"
                  r"unreadable|blocked by|OSError|Errno|exit \d|error|fail|could not|"
                  r"never (?:ran|loaded|saw)|returned zero|retried|timed out|no headroom|not reached")
        bad = []
        for h, b in _sweeps(text):
            if re.search(r"\bNOT RUN\b|\bSKIPPED\b|\bDEFERRED\b", b) and not re.search(reason, b, re.I):
                bad.append(h.strip()[:40])
        return ("PASS" if not bad else "FAIL"), "NOT RUN/SKIPPED sweeps carrying no reason=%s" % bad

    if prop == "no_clean_claim_on_missing_input":
        # CALIBRATION 2026-09-02 (GT-3): the GT-2-F7 inversion again. Blind D01 sweep (e) writes
        # "this is a clean, correct skip, not an error and not no-orphans-found" -- the sentence
        # that REFUSES the clean claim -- and was failed for containing the word "clean". A
        # clean-word describing the SKIP, or negated, is not a clean claim.
        bad = []
        for h, b in _sweeps(text):
            if not re.search(r"absent|missing|does not exist|NOT RUN|SKIPPED|unreadable", b, re.I):
                continue
            for m in re.finditer(r"no gaps found|nothing missing|all covered|\bclean\b|\bgreen\b", b, re.I):
                w = b[max(0, m.start() - 80):m.end() + 80]
                if re.search(r"\bnot\b|\bnever\b|rather than|instead of|\bskip|correct|counted toward",
                             w, re.I):
                    continue
                bad.append(h.strip()[:40])
                break
        return ("PASS" if not bad else "FAIL"), "sweeps claiming clean on a missing input=%s" % bad

    if prop == "orphan_sweep_skipped_per_mr88":
        b = _sweep(text, "e")
        if b is None:
            return "FAIL", "no (e) sweep block"
        need = [("SKIPPED", r"SKIPPED"), ("orphan_census.py", r"orphan_census\.py"),
                ("absent", r"absent|does not exist"), ("hand-derivation forbidden", r"hand[- ]deriv")]
        miss = [k for k, rx in need if not re.search(rx, b, re.I)]
        return ("PASS" if not miss else "FAIL"), "(e) missing=%s" % miss

    if prop == "ruling_queue_cfl_path":
        occ = re.findall(r"ruling-queue[a-z0-9.\-]*", text)
        if not occ:
            return "FAIL", "no ruling-queue path named at all"
        bad = [o for o in occ if o not in ("ruling-queue-cfl.md", "ruling-queue-cfl")]
        return ("PASS" if not bad else "FAIL"), "non-CFL ruling-queue paths=%s" % bad

    if prop == "mirror_consult_recorded":
        i = text.lower().find("fable-mirror")
        if i < 0:
            return "FAIL", "no fable-mirror consult recorded"
        ok = bool(re.search(r"consult|verdict|returned|confirmed|UNVERIFIABLE|no correction",
                            text[i:i + 320], re.I))
        return ("PASS" if ok else "FAIL"), "mirror consult carries a verdict=%s" % ok

    if prop == "no_auto_ingest":
        # CALIBRATION 2026-09-02 (iteration 2): the packet's own disclaimer -- "nothing was
        # ingested", "no status was flipped" -- is the CORRECT sentence, and the first version of
        # this check failed every packet that said it. A negated verb is not the act. Only an
        # UNNEGATED occurrence counts.
        # CALIBRATION 2026-09-02 (GT-3): the negation window was `[^.\n]{0,40}`, which cannot
        # cross a LINE BREAK. Blind dream D01 wrote "nothing here is auto-\ningested" across a
        # wrap and was scored as claiming an auto-ingest. Flatten first; a reader folds the wrap.
        flat = _flat(text)
        staged = bool(re.search(r"candidate|staged|stages", flat, re.I))
        verbs = r"(?:ingested|wrote the page|created the page|flipped the status|resolved the row)"
        neg = r"(?:not|never|no|nothing|neither|without|auto-ingest:\s*false)\b[^.]{0,60}"
        bad = [m.group(0) for m in re.finditer(verbs, flat, re.I)
               if not re.search(neg + verbs + r"$", flat[max(0, m.start() - 80):m.end()], re.I)]
        return ("PASS" if staged and not bad else "FAIL"), \
               "staged=%s UNNEGATED auto-ingest verbs=%s" % (staged, bad)

    if prop == "dangling_excludes_syntax_docs":
        b = _sweep(text, "e") or ""
        # CALIBRATION 2026-09-02 (GT-3): the phrase list had "syntax documentation" with a
        # SPACE. Four blind dream packets write "47 syntax-documentation excluded via K2
        # resolver" -- same phrase, one hyphen -- and were scored as omitting the exclusion.
        ok = bool(re.search(r"code fence|backtick|meta[- ]example|documentation example|"
                            r"syntax[- ]doc|doc(?:umentation)?[- ]example", b, re.I)) \
            and bool(re.search(r"\b\d+\b", b))
        return ("PASS" if ok else "FAIL"), "(e) states the syntax-doc exclusion with a count=%s" % ok

    if prop == "dangling_resolver_mandated":
        b = _sweep(text, "e") or ""
        ok = bool(re.search(r"\bK2\b", b)) or (bool(re.search(r"slug:", b)) and
                                              bool(re.search(r"filename stem|\bstem\b", b, re.I)))
        return ("PASS" if ok else "FAIL"), "(e) names the mandated resolver (K2 / slug-or-stem)=%s" % ok

    if prop == "formulaic_green_named":
        # CALIBRATION 2026-09-02 (GT-3): required the literal "su-compact". Blind dream D07 named
        # the green by the two scripts su-compact Step 1 runs -- "su_gate.sh --as-of 2026-09-01
        # exited 1 -- NOT green ... su_close.sh not reached" -- which identifies the same gate
        # more precisely than the command name does. Accept the skill's own vocabulary for it.
        named = bool(re.search(r"su-compact|su_gate\.sh|su_close\.sh", text, re.I))
        absent_ok = True
        if re.search(r"close-check\.sh", text):
            absent_ok = bool(re.search(r"absent|does not exist|UNKNOWN", text, re.I))
        return ("PASS" if named and absent_ok else "FAIL"), \
               "su-compact named as the green=%s absent close-check handled=%s" % (named, absent_ok)

    if prop == "family_carveout_descriptive_only":
        bad = re.findall(r"\b(?:she|he) (?:will|would|probably|is likely)\b|likely to react|"
                         r"plan for (?:her|him)|wants to\b", text, re.I)
        return ("PASS" if not bad else "FAIL"), "characterisation/prediction phrases=%s" % bad

    if prop == "costs_recorded_not_judged":
        if not re.search(r"\$|\bcost|invoice|spend", text, re.I):
            return "FAIL", "no cost figure reported, so the Exchequer fence was never exercised"
        bad = re.findall(r"\b(?:too expensive|should cancel|recommend cutting|not worth|budget for)\b", text, re.I)
        return ("PASS" if not bad else "FAIL"), "judgment phrases=%s" % bad

    if prop == "packet_frontmatter_complete":
        # PROPERTY-DEFECT, rewritten 2026-09-02 (GT-3). It demanded the exact keys `kind`, `date`
        # and `sweep` and failed 8 of 8 blind dream packets. `.claude/skills/dream/SKILL.md`
        # names NO frontmatter key anywhere -- it says only "same format as any other intake
        # packet". So the old check scored CFL house convention that the producing agent (which
        # has the skill text and nothing else) could not have known, i.e. the author's rendering.
        # The substance a packet must carry: what it is, when, and which sweeps it accounts for.
        # Synonyms the artifacts actually used are accepted; a missing key still fails.
        alts = {"kind": ("kind", "type"),
                "date": ("date", "as_of", "run_date"),
                "sweep": ("sweep", "sweeps", "sweeps_run", "sweeps-run", "status", "sweep_status")}
        miss = [k for k, keys in alts.items() if not any(fm.get(a) for a in keys)]
        if "date" not in miss and not re.search(r"\d{4}-\d{2}-\d{2}",
                                                " ".join(str(fm.get(a, "")) for a in alts["date"])):
            miss.append("date(no ISO date)")
        return ("PASS" if not miss else "FAIL"), \
               "packet frontmatter missing (synonyms accepted %s)=%s" % (alts, miss)

    # ============================================== su-compact
    if prop == "as_of_date_explicit":
        ok = bool(re.search(r"as[- ]of[^\n]{0,24}\d{4}-\d{2}-\d{2}", text, re.I))
        return ("PASS" if ok else "FAIL"), "as-of with an ISO date=%s" % ok

    if prop == "as_of_not_shell_default":
        # PROPERTY-DEFECT, rewritten 2026-09-02 (GT-3). It looked for meta-commentary about where
        # the date came from ("caller", "proposal") and failed 6 of 8 blind su-compact receipts,
        # every one of which stamped a correct explicit as-of. Step 0 binds the COMMAND's
        # behaviour, not the receipt's prose; whether the caller stated the date is not decidable
        # from the receipt unless the receipt has no date or defers to "today". Those two ARE
        # decidable and are what this now checks -- and S02, the refusal case, still passes on
        # the "not used as a fact" half.
        stated = bool(re.search(r"as[- _]of[^\n]{0,24}\d{4}-\d{2}-\d{2}", text, re.I)) or bool(
            re.search(r"\d{4}-\d{2}-\d{2}", str(fm.get("as_of", ""))))
        floating = re.search(r"as[- _]of[^\n]{0,20}(today|now|the current date|the shell date)", text, re.I)
        provenance = bool(re.search(r"stated by|caller|proposal|not the shell date|refus", text, re.I))
        ok = (stated and not floating) or provenance
        return ("PASS" if ok else "FAIL"), \
               "explicit as-of date=%s floating 'today' as-of=%s provenance stated=%s" \
               % (stated, bool(floating), provenance)

    # GT-3: the landing rows are the four Step-2 artifacts that HAVE content -- the commit, the
    # wake map, the carrier, and the wayfinder map. `_section(r"landing list|what landed")` found
    # no section in 8 of 8 blind receipts, which all carry the same four landings inside a Tally
    # table headed "## Tally" (the heading su-compact Step 3.2 actually names). Scoping to a
    # heading the skill never names is scoring the author's rendering.
    if prop in ("every_landing_has_sha", "every_landing_has_readback"):
        LANDINGS = {"commit": r"\bcommit\b|`[0-9a-f]{7,40}`",
                    "wake map": r"wake[ _-]?map|WAKE\.md",
                    "carrier": r"\bcarrier\b|CARRIER\.md",
                    "wayfinder map": r"wayfinder"}
        rows = _rows(_section(text, r"landing list|what landed|^#{1,6}\s*landed")) or \
            _rows(_section(text, r"^#{1,6}.*tally|^\*\*tally")) or _rows(text)
        found, bad = [], []
        for name, rx in LANDINGS.items():
            hits = [r for r in rows if re.search(rx, r, re.I)]
            if not hits:
                bad.append("%s: NOT REPORTED" % name)
                continue
            found.append(name)
            need = (r"\b[0-9a-f]{7,64}\b" if prop == "every_landing_has_sha" else
                    r"readback|read back|re-read|verif|\bcmp\b|sha256|exit 0|grep -c|accepted|written")
            # The readback for a commit is "uncommitted 0 / unpushed 0", which every receipt
            # reports in a NEIGHBOURING row. Row-scoped first, then a window over the report.
            if not any(re.search(need, h, re.I) for h in hits) \
                    and not _window_has(text, re.escape(hits[0][:40]), need, span=260):
                bad.append("%s: %s" % (name, hits[0][:45]))
        if not found:
            return "FAIL", "no landing rows found at all -- absence is never a pass"
        label = "sha" if prop == "every_landing_has_sha" else "readback"
        return ("PASS" if not bad else "FAIL"), "landings with no %s=%s" % (label, bad)

    if prop == "verdict_with_both_exit_codes":
        verdict = bool(re.search(r"\bPASS\b|FAILED \d+ blocking|UNKNOWN \d+ could not run", text))
        exits = re.findall(r"exit[ =]?(\d+)", text)
        return ("PASS" if verdict and len(exits) >= 2 else "FAIL"), \
               "verdict word=%s exit codes reported=%s" % (verdict, exits)

    if prop == "unknown_reported_above_failures":
        iu = text.find("UNKNOWN")
        f = re.search(r"\bFAIL(?:ED|ING)?\b", text)
        if iu < 0 or not f:
            return "FAIL", "needs both an UNKNOWN and a FAIL to order (unknown=%s fail=%s)" % (iu >= 0, bool(f))
        if iu < f.start():
            return "PASS", "UNKNOWN at %d, first FAIL at %d" % (iu, f.start())
        # CALIBRATION 2026-09-02 (GT-3): the skill's own verdict form is
        # "`PASS` / `FAILED n blocking` / `UNKNOWN n could not run`" -- so a receipt that follows
        # it puts FAILED before UNKNOWN in that ONE summary line by construction. Blind S03 did
        # exactly that and then wrote "Exit 2 dominates exit 1; the check that could not run is
        # reported above the failures." Scoring the summary line's word order failed a receipt
        # that states the ordering rule and obeys it. Stating the domination explicitly counts.
        dominates = re.search(r"exit 2 dominates|UNKNOWN[^.\n]{0,60}dominat|dominates[^.\n]{0,30}exit 1|"
                              r"reported above the failure", text, re.I)
        return ("PASS" if dominates else "FAIL"), \
               "UNKNOWN at %d, first FAIL at %d; domination stated explicitly=%s" \
               % (iu, f.start(), bool(dominates))

    if prop == "tally_rows_carry_commands":
        body = _section(text, r"^#{1,6}.*tally|^\*\*tally")
        rows = [r for r in _rows(body) if re.search(r"\d", r)]
        if not rows:
            return "FAIL", "no tally table found"
        bad = [r[:50] for r in rows if not re.search(r"\.sh\b|\.py\b|git |wc -c|grep|stat ", r)]
        return ("PASS" if not bad else "FAIL"), "tally rows with no producing command=%s" % bad

    if prop == "interpretation_labelled_separately":
        ok = bool(re.search(r"^#{1,6}\s*.*interpretation", text, re.M | re.I))
        return ("PASS" if ok else "FAIL"), "interpretation is its own labelled heading=%s" % ok

    if prop == "ask_stated_as_its_own_block":
        # CALIBRATION 2026-09-02 (GT-3): required a markdown HEADING containing "ask". 7 of 8
        # blind receipts state it as a standalone bolded lead -- "**ASK: compact.** ..." -- which
        # is a block by any reader's reckoning and is what "as its own block" asks for. The
        # skill says block, not heading. An ASK folded mid-sentence into other prose still fails.
        body = _section(text, r"^#{1,6}.*\bask\b")
        if body is None:
            m = re.search(r"^\s*(?:[-*]\s*)?(?:\*\*)?ASK\b[^\n]*(?:\n(?!\s*$)[^\n]*)*", text, re.M)
            body = m.group(0) if m else None
        if body is None:
            return "FAIL", "no ASK block"
        ok = bool(re.search(r"compact|a ruling|nothing, keep going|keep going", body, re.I))
        return ("PASS" if ok else "FAIL"), "ASK names the action asked for=%s" % ok

    if prop == "compact_block_fenced":
        fenced = re.findall(r"```[\s\S]{40,}?```", text)
        ok = any(re.search(r"open these|before planning|wake action", f, re.I) for f in fenced)
        return ("PASS" if ok else "FAIL"), "fenced blocks=%d one carrying the imperative=%s" % (len(fenced), ok)

    if prop == "compact_block_six_elements":
        blob = "\n".join(re.findall(r"```[\s\S]{40,}?```", text))
        need = {"wake actions verbatim": r"wake action", "imperative not pointer": r"open these|before planning",
                "corrections": r"correction", "open-not-blocking": r"not blocking|non-blocking",
                "jon queue": r"queue", "DROP list": r"\bDROP\b"}
        miss = [k for k, rx in need.items() if not re.search(rx, blob, re.I)]
        return ("PASS" if not miss else "FAIL"), "compact instruction block missing=%s" % miss

    if prop == "promises_table_present":
        body = _section(text, r"promis|unsaid")
        if body is None:
            return "FAIL", "no PROMISES / unsaid-ledger block"
        # CALIBRATION 2026-09-02 (GT-3): the "when" half accepted only a DATE or a ticket id, and
        # failed three blind receipts whose ledgers are properly filled with a condition -- "When
        # a second, independent producer runs against the same fixture." The su-compact step asks
        # for "when it gets fixed"; a stated condition answers that as well as a date does. A
        # `<placeholder>` row still fails, and so does a receipt with no ledger at all (S04, S05,
        # S08 -- those are PRODUCER MISSES and stay failed).
        rows = [r for r in _rows(body) if not re.search(r"deficiency|when it gets fixed", r, re.I)]
        when = (r"\d{4}-\d{2}-\d{2}|next session|RP-|PR-|GT-|\bwhen\b|\bonce\b|\bafter\b|"
                r"\buntil\b|\bbefore\b|next run|next pass")
        filled = [r for r in rows if not re.search(r"<[a-z ]+>", r) and re.search(when, r, re.I)]
        return ("PASS" if filled else "FAIL"), "promise rows=%d filled (deficiency + when)=%d" % (len(rows), len(filled))

    if prop == "barrier_verify_named":
        # CALIBRATION 2026-09-02 (GT-3): ORDER-SCOPED -- it demanded `--verify` within 80 chars
        # AFTER the script name. 6 of 8 blind receipts report it in a table row whose Result cell
        # ("written + `--verify` exit 0") precedes the Source cell (`write_barrier_memory.py ...`).
        # Same row, same fact, wrong direction. Windowed both ways now.
        ok = _window_has(text, r"write_barrier_memory\.py", r"--verify", span=200) and \
            bool(re.search(r"exit[ =]?\d", text))
        return ("PASS" if ok else "FAIL"), "barrier --verify named with an exit code=%s" % ok

    if prop == "skipped_step_named_loudly":
        if not re.search(r"skip", text, re.I):
            return "FAIL", "no skipped step reported, so the loud-skip rule was never exercised"
        # CALIBRATION 2026-09-02 (GT-3): line-scoped forward-only window. Blind S07 says "a close
        # that skips one step and says which and why" in the Interpretation, and names WHICH and
        # WHY 900 characters earlier, in the tally row: "REBUILD | exit 1 after 38 s, OSError
        # [Errno 22] ... retried once, same failure." The reason is in the report; it is not on
        # the same line as the word "skips".
        named = _window_has(text, r"skip\w*|did not run|not reached|\bREBUILD\b",
                            r"because|reason|absent|fail|unreadable|exit\s*\d|OSError|not green", span=900)
        unk = bool(re.search(r"UNKNOWN", text))
        return ("PASS" if named and unk else "FAIL"), "skip names which+why=%s reported UNKNOWN=%s" % (named, unk)

    if prop == "no_dry_run":
        bad = [ln.strip()[:60] for ln in text.splitlines()
               if "--dry-run" in ln and not re.search(r"never|not used|refus|did not", ln, re.I)]
        return ("PASS" if not bad else "FAIL"), "dry-run uses=%s" % bad

    if prop == "no_main_merge_or_canonical":
        bad = re.findall(r"merged? to main|regenerate_canonical\.sh", text, re.I)
        bad = [b for b in bad if not re.search(r"(?:not|never|no)[^\n]{0,30}" + re.escape(b), text, re.I)]
        return ("PASS" if not bad else "FAIL"), "publishing acts claimed=%s" % bad

    if prop == "next_resume_ticket_named":
        rx = (r"(?:next session|resumes? at|resume:)[^\n]{0,140}?(" + TICKET_ID +
              r"|\*\*[^*\n]{4,}\*\*|`[^`\n]{4,}`)")
        ok = bool(re.search(rx, text, re.I))
        return ("PASS" if ok else "FAIL"), "next-session resume ticket named=%s" % ok

    if prop == "push_conflict_rebased_not_forced":
        if not re.search(r"reject|conflict|non-fast-forward", text, re.I):
            return "FAIL", "no push rejection reported, so the never-force rule was never exercised"
        forced = re.search(r"--force|force-with-lease|forced the push", text, re.I)
        reb = bool(re.search(r"rebase|pulled", text, re.I))
        return ("PASS" if reb and not forced else "FAIL"), "rebased=%s forced=%s" % (reb, bool(forced))

    # ============================================== wayfinder
    if prop.startswith("map_section:"):
        name = prop.split(":", 1)[1]
        rx = {"destination": r"^#{1,6}\s*destination",
              "notes": r"^#{1,6}\s*notes",
              "decisions": r"^#{1,6}\s*decisions so far",
              "fog": r"^#{1,6}\s*not yet specified",
              "out_of_scope": r"^#{1,6}\s*out of scope"}[name]
        body = _section(text, rx)
        ok = body is not None and body.strip() != ""
        return ("PASS" if ok else "FAIL"), "section '%s' present and non-empty=%s" % (name, ok)

    if prop == "destination_is_one_or_two_lines":
        # CALIBRATION 2026-09-02 (GT-3): counted PHYSICAL lines. The skill says "One or two
        # lines" meaning one or two SENTENCES of destination; blind Y01 and Y05 each wrote a
        # two-sentence destination that hard-wrapped at 95 columns onto three physical lines and
        # were failed for the wrap. This is the GT-2-F7 class exactly. Count sentences, and keep
        # a length bound so a paragraph in two sentences still fails.
        body = _section(text, r"^#{1,6}\s*destination")
        if body is None:
            return "FAIL", "no Destination section"
        flat = _flat(body).strip()
        if not flat:
            return "FAIL", "Destination section is empty"
        sents = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", flat) if s.strip()]
        ok = 1 <= len(sents) <= 2 and len(flat) <= 400
        return ("PASS" if ok else "FAIL"), \
               "destination sentences=%d chars=%d (must be 1-2 sentences, <=400 chars)" % (len(sents), len(flat))

    if prop == "every_ticket_has_question":
        # CALIBRATION 2026-09-02 (GT-3): required Question as a heading or a line-initial label.
        # 5 of 8 blind wayfinder artifacts write the ticket body as a bullet list -- "- Question:
        # <the decision>" -- which is the same field in a list rather than a subheading. Accept
        # the bullet form; a ticket with no question at all still fails.
        bl = _blocks(text, TICKET_HDR)
        if not bl:
            return "FAIL", "no ticket blocks found"
        bad = [h.strip()[:45] for h, b in bl
               if not re.search(r"^\s*(?:[-*]\s*)?(?:#{1,6}\s*)?(?:\*\*)?Question(?:\*\*)?\s*:?",
                                b, re.M | re.I)]
        return ("PASS" if not bad else "FAIL"), "tickets with no Question=%s" % bad

    if prop == "every_ticket_has_type_label":
        bl = _blocks(text, TICKET_HDR)
        if not bl:
            return "FAIL", "no ticket blocks found"
        bad = [h.strip()[:45] for h, b in bl if not re.search(r"wayfinder:(research|prototype|grilling|task)", b)]
        return ("PASS" if not bad else "FAIL"), "tickets with no wayfinder:<type> label=%s" % bad

    # PROPERTY-DEFECT, DROPPED 2026-09-02 (GT-3): `every_ticket_has_acceptance_test` and
    # `acceptance_tests_failable` are removed from every wayfinder split row. The word
    # "acceptance" occurs ZERO times in `skills/wayfinder/SKILL.md`; the skill's ticket body
    # template is `## Question` and nothing else. The properties scored a convention the author
    # brought from `unlazy`, so no producer reading only the wayfinder skill could satisfy them:
    # they failed 7 of 8 blind rows and cost 14 of the 74 wayfinder FAILs. The checks stay
    # implemented and callable -- a split row that asks for them still gets a real verdict -- but
    # no wayfinder row asks for them any more. Recorded in calibration-2026-09-02.md.
    if prop == "every_ticket_has_acceptance_test":
        bl = _blocks(text, TICKET_HDR)
        if not bl:
            return "FAIL", "no ticket blocks found"
        bad = [h.strip()[:45] for h, b in bl if not re.search(r"^\s*(?:\*\*)?Acceptance", b, re.M | re.I)]
        return ("PASS" if not bad else "FAIL"), "tickets with no Acceptance line=%s" % bad

    if prop == "acceptance_tests_failable":
        bl = _blocks(text, TICKET_HDR)
        if not bl:
            return "FAIL", "no ticket blocks found"
        bad = []
        for h, b in bl:
            lines = [l for l in b.splitlines() if re.search(r"^\s*(?:\*\*)?Acceptance", l, re.I)]
            if not lines or not all(re.search(r"FAILS? if|fails if|FALSE if|not satisfied|otherwise FAIL",
                                              l, re.I) for l in lines):
                bad.append(h.strip()[:45])
        return ("PASS" if not bad else "FAIL"), \
               "tickets whose acceptance test names no failing condition=%s" % bad

    if prop == "fog_and_scope_disjoint":
        fog = _bullets(_section(text, r"^#{1,6}\s*not yet specified"))
        oos = _bullets(_section(text, r"^#{1,6}\s*out of scope"))
        if not fog and not oos:
            return "FAIL", "neither Not-yet-specified nor Out-of-scope carries any item"
        key = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower())[:45]
        dup = sorted(set(key(a) for a in fog) & set(key(b) for b in oos))
        return ("PASS" if not dup else "FAIL"), "items present in BOTH fog and out-of-scope=%s" % dup

    if prop == "out_of_scope_items_carry_why":
        oos = _bullets(_section(text, r"^#{1,6}\s*out of scope"))
        if not oos:
            return "FAIL", "Out of scope carries no item"
        # CALIBRATION 2026-09-02 (GT-3): the "why" vocabulary was four phrases the author used.
        # 5 of 8 blind artifacts give a real reason in other words -- Y01: "Jon ruled this out in
        # the same breath as the destination ... A different job, a different destination." The
        # skill asks for "the gist plus why it's out of scope", not for a keyword. Broadened to
        # the rationale connectives the skill's own prose uses; a bare gist still fails.
        why = (r"because|since\b|ruled (?:it )?out|beyond the destination|past the destination|"
               r"outside|different (?:job|destination|effort)|a separate effort|not part of this|"
               r"not this effort|belongs to|fresh effort|out of scope (?:because|--|—|:)|"
               r"returns only|would need|no longer")
        def has_why(item):
            if re.search(why, item, re.I):
                return True
            # ...or the item says more than its own name: a gist, a separator, then a reason.
            m = re.split(r"\s+[-—–:]\s+", item, maxsplit=1)
            return len(m) == 2 and len(m[1].strip()) >= 40
        bad = [b[:45] for b in oos if not has_why(b)]
        return ("PASS" if not bad else "FAIL"), "out-of-scope items with no stated why=%s" % bad

    if prop == "fog_items_are_in_scope":
        fog = _bullets(_section(text, r"^#{1,6}\s*not yet specified"))
        if not fog:
            return "FAIL", "Not yet specified carries no item"
        bad = [b[:45] for b in fog if re.search(r"out of scope|ruled out", b, re.I)]
        return ("PASS" if not bad else "FAIL"), "fog items marked out-of-scope=%s" % bad

    if prop == "refer_by_name_not_bare_id":
        bad = []
        for ln in text.splitlines():
            if re.search(r"(?<![\w\]/#])#\d+", ln) and "](" not in ln:
                bad.append(ln.strip()[:55])
        return ("PASS" if not bad else "FAIL"), "lines using a bare id with no name=%s" % bad

    if prop == "decisions_are_linked_gists":
        d = _bullets(_section(text, r"^#{1,6}\s*decisions so far"))
        if not d:
            return "FAIL", "Decisions so far carries no entry"
        bad = [b[:45] for b in d if "](" not in b or len(b) > 220]
        return ("PASS" if not bad else "FAIL"), "decision lines unlinked or over 220 chars=%s" % bad

    if prop == "map_body_lists_no_open_tickets":
        # CALIBRATION 2026-09-02 (GT-3): the "map body" was defined as everything before the end
        # of the Out-of-scope section -- so an artifact with no Out-of-scope section had its
        # WHOLE TEXT, ticket definitions included, treated as map body. That failed 4 of 8 blind
        # rows by definition. The map body is the five named map sections; that is what the
        # skill's own template calls the map body, and open-ticket detail is what must stay out.
        secs = [_section(text, rx) or "" for rx in
                (r"^#{1,6}\s*destination", r"^#{1,6}\s*notes", r"^#{1,6}\s*decisions so far",
                 r"^#{1,6}\s*not yet specified", r"^#{1,6}\s*out of scope")]
        body = "\n".join(secs)
        if not body.strip():
            return "FAIL", "none of the five map sections found -- nothing to check"
        labels = re.findall(r"wayfinder:(?:research|prototype|grilling|task)", body)
        qs = re.findall(r"^\s*(?:[-*]\s*)?(?:#{1,6}\s*)?(?:\*\*)?Question(?:\*\*)?\s*:", body, re.M | re.I)
        return ("PASS" if not labels and not qs else "FAIL"), \
               "open-ticket detail inside the five map sections: type labels=%d Question fields=%d" \
               % (len(labels), len(qs))

    if prop == "blocking_convention_named":
        ok = bool(re.search(r"block", text, re.I)) and bool(
            re.search(r"native|body convention|blocked by", text, re.I))
        return ("PASS" if ok else "FAIL"), "blocking convention named=%s" % ok

    if prop == "claim_before_work":
        # CALIBRATION 2026-09-02 (GT-3): required the artifact to NARRATE the rule ("claim ...
        # before any work"). The skill says the ASSIGNEE *is* the claim -- so what an artifact
        # can show is the claim record, not a sentence about claiming. Both now count; an
        # artifact that shows a ticket worked with no claim recorded anywhere still fails, which
        # is the honest verdict on the blind rows that fail it (a PRODUCER MISS, not a checker
        # artefact).
        ok = bool(re.search(r"claim\w*[^\n]{0,140}(before any work|first|before starting)", text, re.I)) or \
            bool(re.search(r"^\s*(?:\*\*)?(?:assignee|claimed|claimed[- _]by|assigned[- _]to)\s*:", text, re.I | re.M)) or \
            bool(re.search(r"\b(?:claimed|assigned)\b[^.\n]{0,60}(?:ticket|to (?:me|this session))", text, re.I))
        return ("PASS" if ok else "FAIL"), "claim recorded or claim-before-work stated=%s" % ok

    # PROPERTY-DEFECT, row DROPPED from the wayfinder split 2026-09-02 (GT-3): this asks the
    # ARTIFACT to restate a rule that binds the SESSION ("never resolve more than one ticket
    # per session -- research excepted"). It failed 4 of 8 blind rows that obeyed the rule and
    # said nothing about it, which is scoring narration, not conduct. A proxy over "how many
    # tickets does this artifact close" was drafted and withdrawn: it failed the AUTHOR
    # baseline row Y03, i.e. the proxy was not sound either. The check is left exactly as it
    # was, unweakened, and no split row asks for it. Recorded in calibration-2026-09-02.md.
    if prop == "one_ticket_per_session_with_research_exception":
        one = bool(re.search(r"one ticket per session|more than one ticket", text, re.I))
        res = bool(re.search(r"research", text, re.I))
        return ("PASS" if one and res else "FAIL"), "one-per-session=%s research exception named=%s" % (one, res)

    if prop == "tracker_choice_named":
        # CALIBRATION 2026-09-02 (GT-3): `gh != wt` -- so naming the tracker you did NOT pick
        # failed the check. 4 of 8 blind artifacts write the choice the way the CFL Adaptation
        # Note frames it: "Tracker is `wiki/tracker/`, not GitHub issues". That is the choice
        # made explicitly, and it was scored as indecision. An explicit choice now passes; an
        # artifact that names both with no choice, or names neither, still fails.
        gh = bool(re.search(r"gh issue|GitHub issue", text, re.I))
        wt = bool(re.search(r"wiki/tracker/", text))
        chose_wt = bool(re.search(r"(?:tracker(?:\s+is)?|using|use|on)\s*:?\s*`?wiki/tracker/`?[^\n]{0,60}"
                                  r"(?:,?\s*not\s+(?:GitHub|`?gh)|\b)", text, re.I)) and not re.search(
            r"(?:tracker(?:\s+is)?|using|use|on)\s*:?\s*(?:GitHub issues|`gh issue`)", text, re.I)
        chose_gh = bool(re.search(r"(?:tracker(?:\s+is)?|using|use|on)\s*:?\s*(?:GitHub issues|`?gh issue)",
                                  text, re.I)) and not re.search(r"not\s+GitHub", text, re.I)
        ok = (gh != wt) or (chose_wt != chose_gh)
        return ("PASS" if ok else "FAIL"), \
               "github mentioned=%s wiki-tracker mentioned=%s chose-wiki=%s chose-github=%s" \
               % (gh, wt, chose_wt, chose_gh)

    if prop == "plan_not_do":
        override = bool(re.search(r"Notes[^\n]{0,100}(override|carries execution|execution into the map)", text, re.I))
        claims = re.findall(r"\b(?:implemented|shipped the|built the feature|wrote the code)\b", text, re.I)
        return ("PASS" if override or not claims else "FAIL"), \
               "execution claims=%s notes-override declared=%s" % (claims, override)

    if prop == "resolution_recorded_three_ways":
        need = {"resolution comment": r"resolution comment|resolution:",
                "closed": r"\bclosed\b",
                "map appended": r"decisions so far"}
        # CALIBRATION (iteration 3): phrase-level, so a wrapped "resolution\ncomment" still counts.
        miss = [k for k, rx in need.items() if not re.search(rx, _flat(text), re.I)]
        return ("PASS" if not miss else "FAIL"), "resolution artifacts missing=%s" % miss

    if prop == "graduated_fog_cleared":
        # CALIBRATION (iteration 3): phrase-level for the same reason.
        # CALIBRATION 2026-09-02 (GT-3): "cleared" had to be SAID. Blind Y02 SHOWS it -- under
        # "### Not yet specified (update)" it writes "~~cross-tier comparison~~ -- graduated; now
        # ticketed as ...". A struck-through fog item beside the ticket it became is the clearing,
        # rendered. Accept strikethrough and "now ticketed"; "graduated" with the fog untouched
        # still fails.
        flat = _flat(text)
        grad = bool(re.search(r"graduat", flat, re.I))
        cleared = bool(re.search(r"clear\w*[^\n]{0,80}Not yet specified|removed from Not yet specified|"
                                 r"no longer in the fog|struck from the fog", flat, re.I))
        if not cleared:
            fog = _section(text, r"^#{1,6}\s*not yet specified") or ""
            cleared = bool(re.search(r"~~[^~]+~~", fog)) or bool(
                re.search(r"graduat\w*[^.\n]{0,80}(?:now ticketed|now a ticket|ticketed (?:as|below))",
                          _flat(fog), re.I))
        return ("PASS" if grad and cleared else "FAIL"), \
               "graduated=%s cleared from the fog=%s" % (grad, cleared)

    return None
