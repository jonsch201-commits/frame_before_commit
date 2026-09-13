#!/usr/bin/env python3
"""Regenerate wiki/tracker/skills-frontmatter-digest.md from skills/*/SKILL.md frontmatter.

This is the deriving mechanism for a file that was previously a one-time hand
snapshot with no regeneration step ("regenerated as a step inside wiki-master's
standard-update operation" was aspirational prose with no script behind it).
This script IS that step.

Usage:
    python regen_skills_digest.py --as-of 2026-07-26
    python regen_skills_digest.py --as-of 2026-07-26 --check
    python regen_skills_digest.py --as-of 2026-07-26 --root skills --digest wiki/tracker/skills-frontmatter-digest.md

Design notes (read before "fixing" the heuristics below):

- The digest's prose header (title, "Why this file exists", "Freshness
  mechanism", "do not edit by hand" warning) is preserved VERBATIM from
  whatever is currently on disk. This script never rewrites that prose in its
  own words -- it only touches the frontmatter watermark and everything from
  the "## Index" heading down.
- `status` and `vendored` columns cannot always be read off a single YAML key
  (some skills, e.g. data-master/test-master, embed "Status: STUB" in prose
  rather than declaring a `status:` key). The fallbacks below are documented,
  regex-based, and deterministic -- same input always produces the same
  output -- which is the property that actually matters for this file, not
  bit-for-bit fidelity with the previous hand-curated table.
- `vendored` is derived uniformly from `upstream.repo` whenever an `upstream:`
  block exists, regardless of `relationship` (adapted/forked/vendored). The
  previous hand-built table gave `reverse-grill-me` a special-cased
  "(CFL-internal)" despite it having the same upstream.repo as grill-me --
  that distinction is a semantic judgment call, not something recoverable
  from the YAML schema, so it is intentionally not reproduced. See the run
  report for the concrete before/after.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

FRONTMATTER_DELIM = "---"
INDEX_HEADING_RE = re.compile(r"^## Index \(\d+ skills\)\s*$")
LAST_REGEN_RE = re.compile(r"(?m)^last_regenerated:\s*\S+\s*$")
STATUS_PROSE_RE = re.compile(r"\bStatus:\s*([A-Za-z][A-Za-z ]*?)(?:[—–.,;]|$)")
QUOTED_RE = re.compile(r'"([^"\n]{2,80})"')
SLASH_CMD_RE = re.compile(r"(?<![\w/])(/[a-zA-Z][\w-]*)")
TRIGGER_CUE_RE = re.compile(r"\b(Use when|Uses? when|Triggers?:?|Invoked when|Invoke(?:d)? when)\b", re.IGNORECASE)

TRIGGERS_CELL_MAX = 110


@dataclass
class SkillRecord:
    directory: str
    name: str
    raw_frontmatter: str
    data: dict = field(default_factory=dict)

    @property
    def sort_key(self):
        return (self.name.lower(), self.directory.lower())

    @property
    def type_col(self) -> str:
        t = self.data.get("type")
        return str(t) if t else "—"

    @property
    def status_col(self) -> tuple[str, bool]:
        """Returns (display_text, found)."""
        status = self.data.get("status")
        source = "field"
        if not status:
            desc = str(self.data.get("description") or "")
            m = STATUS_PROSE_RE.search(desc)
            if m:
                status = m.group(1).strip()
                source = "prose"
        if not status:
            return "—", False
        return status, True

    @property
    def vendored_col(self) -> str:
        upstream = self.data.get("upstream")
        if not isinstance(upstream, dict):
            return "—"
        repo = str(upstream.get("repo") or "")
        if not repo:
            return "—"
        parts = [p for p in repo.split("/") if p]
        if not parts:
            return "—"
        if "." in parts[0] and len(parts) > 1:
            org = parts[1]
        else:
            org = parts[0]
        return f"**{org}**"

    @property
    def triggers_col(self) -> str:
        desc = str(self.data.get("description") or "")
        found: list[str] = []
        seen: set[str] = set()
        # Walk the description left to right, collecting slash-commands and
        # quoted phrases in the order they appear so the cell reads like the
        # skill's own trigger list, not a jumbled bag.
        tokens = []
        for m in SLASH_CMD_RE.finditer(desc):
            tokens.append((m.start(), f"`{m.group(1)}`"))
        for m in QUOTED_RE.finditer(desc):
            tokens.append((m.start(), f'"{m.group(1)}"'))
        tokens.sort(key=lambda t: t[0])
        for _, text in tokens:
            if text not in seen:
                seen.add(text)
                found.append(text)
        if found:
            cell = ", ".join(found)
        else:
            # No quoted phrases or slash-commands at all (mission-statement-style
            # descriptions like project-manager's). Prefer the substring from a
            # "Use when" / "Triggers" / "Invoked when" cue onward -- still just a
            # slice of the same text, not a hand paraphrase -- else fall back to
            # the description from the start.
            m = TRIGGER_CUE_RE.search(desc)
            cell = desc[m.start():].strip() if m else desc.strip()
        cell = cell.replace("|", "\\|")
        if len(cell) > TRIGGERS_CELL_MAX:
            cell = cell[: TRIGGERS_CELL_MAX - 1].rstrip() + "…"
        return cell


class DigestError(Exception):
    pass


def strip_bom_and_report(raw: bytes, path: Path, warnings: list[str]) -> str:
    if raw.startswith(b"\xef\xbb\xbf"):
        warnings.append(f"{path}: UTF-8 BOM present -- stripped for parsing (source file untouched)")
    return raw.decode("utf-8-sig")


def extract_frontmatter_block(text: str, path: Path) -> str:
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        raise DigestError(f"{path}: does not start with a '---' frontmatter delimiter")
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIM:
            end_idx = i
            break
    if end_idx is None:
        raise DigestError(f"{path}: no closing '---' delimiter found for frontmatter block")
    return "\n".join(lines[1:end_idx])


def load_skill(path: Path, warnings: list[str]) -> SkillRecord:
    directory = path.parent.name
    raw_bytes = path.read_bytes()
    text = strip_bom_and_report(raw_bytes, path, warnings)
    block = extract_frontmatter_block(text, path)
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError as e:
        raise DigestError(f"{path}: YAML parse error: {e}") from e
    if not isinstance(data, dict):
        raise DigestError(f"{path}: frontmatter did not parse to a mapping (got {type(data).__name__})")
    name = data.get("name")
    if not name:
        warnings.append(f"{directory}: missing 'name' key in frontmatter (using directory name as fallback)")
        name = directory
    return SkillRecord(directory=directory, name=str(name), raw_frontmatter=block, data=data)


def collect_skills(root: Path) -> tuple[list[SkillRecord], list[str], list[str]]:
    """Returns (records, parse_errors, warnings). Records empty if any parse_errors."""
    parse_errors: list[str] = []
    warnings: list[str] = []
    records: list[SkillRecord] = []
    skill_files = sorted(root.glob("*/SKILL.md"))
    for path in skill_files:
        try:
            records.append(load_skill(path, warnings))
        except DigestError as e:
            parse_errors.append(str(e))
    records.sort(key=lambda r: r.sort_key)
    return records, parse_errors, warnings


def build_index_table(records: list[SkillRecord]) -> str:
    lines = [
        "| Skill | type | status | vendored | Primary triggers (abbrev.) |",
        "|-------|------|--------|----------|----------------------------|",
    ]
    for r in records:
        status_text, found = r.status_col
        status_cell = f"**{status_text}**" if found else status_text
        lines.append(
            f"| {r.name} | {r.type_col} | {status_cell} | {r.vendored_col} | {r.triggers_col} |"
        )
    return "\n".join(lines)


def build_mismatch_footnote(records: list[SkillRecord]) -> str:
    mismatches = [r for r in records if r.name != r.directory]
    if not mismatches:
        return ""
    notes = []
    for r in mismatches:
        notes.append(
            f"*`name` note: the `{r.directory}/` directory declares `name: {r.name}` "
            f"(directory/name mismatch -- flagged for skills-master).*"
        )
    return "\n\n".join(notes)


def build_full_blocks(records: list[SkillRecord]) -> str:
    # Full-blocks section is keyed by directory heading (matches prior convention),
    # but iterated in the same name-sorted order as the Index table above.
    parts = []
    for r in records:
        parts.append(f"### {r.directory}\n```yaml\n{r.raw_frontmatter.rstrip()}\n```")
    return "\n\n".join(parts)


def build_generated_section(records: list[SkillRecord]) -> str:
    count = len(records)
    section = [f"## Index ({count} skills)", "", build_index_table(records)]
    footnote = build_mismatch_footnote(records)
    if footnote:
        section += ["", footnote]
    section += ["", "---", "", "## Full frontmatter blocks", "", build_full_blocks(records)]
    return "\n".join(section) + "\n"


def split_existing_digest(text: str, digest_path: Path) -> tuple[str, str]:
    """Returns (frontmatter_block_with_delims, preserved_prose_block)."""
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        raise DigestError(f"{digest_path}: existing digest does not start with '---'")
    fm_end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIM:
            fm_end = i
            break
    if fm_end is None:
        raise DigestError(f"{digest_path}: no closing '---' for existing digest frontmatter")
    frontmatter_block = "\n".join(lines[: fm_end + 1])
    sep_idx = None
    for i in range(fm_end + 1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIM:
            sep_idx = i
            break
    if sep_idx is None:
        raise DigestError(f"{digest_path}: no second '---' separator found before generated section")
    prose_block = "\n".join(lines[fm_end + 1 : sep_idx])
    return frontmatter_block, prose_block


def render_digest(existing_text: str, digest_path: Path, records: list[SkillRecord], as_of: str) -> str:
    frontmatter_block, prose_block = split_existing_digest(existing_text, digest_path)
    if not LAST_REGEN_RE.search(frontmatter_block):
        raise DigestError(f"{digest_path}: no 'last_regenerated:' line found in frontmatter template")
    new_frontmatter = LAST_REGEN_RE.sub(f"last_regenerated: {as_of}", frontmatter_block)
    generated = build_generated_section(records)
    out = new_frontmatter + "\n" + prose_block + "\n---\n\n" + generated
    if not out.endswith("\n"):
        out += "\n"
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="skills", help="Directory containing skill subdirectories (default: skills)")
    parser.add_argument(
        "--digest",
        default="wiki/tracker/skills-frontmatter-digest.md",
        help="Path to the digest file to read/write (default: wiki/tracker/skills-frontmatter-digest.md)",
    )
    parser.add_argument("--as-of", required=True, help="Watermark date (YYYY-MM-DD) to stamp as last_regenerated. Required -- no silent today() default.")
    parser.add_argument("--check", action="store_true", help="Regenerate in memory and diff against disk; exit 1 on mismatch; write nothing.")
    args = parser.parse_args()

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.as_of):
        print(f"error: --as-of must be YYYY-MM-DD, got {args.as_of!r}", file=sys.stderr)
        return 2

    root = Path(args.root)
    digest_path = Path(args.digest)

    if not root.is_dir():
        print(f"error: --root {root} is not a directory", file=sys.stderr)
        return 2
    if not digest_path.is_file():
        print(f"error: digest file {digest_path} does not exist", file=sys.stderr)
        return 2

    records, parse_errors, warnings = collect_skills(root)

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    if parse_errors:
        print(f"error: {len(parse_errors)} SKILL.md file(s) failed to parse:", file=sys.stderr)
        for e in parse_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    existing_text = digest_path.read_text(encoding="utf-8")
    try:
        new_text = render_digest(existing_text, digest_path, records, args.as_of)
    except DigestError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.check:
        # STALENESS IS CONTENT DRIFT, NOT THE PASSAGE OF TIME.
        #
        # Calibration, 2026-07-27, found by running this check exactly one day after writing it.
        # `--check` compared the whole file including `last_regenerated:`, so passing a different
        # `--as-of` reported STALE against a digest whose body was byte-identical. The check fired
        # on the calendar. Wired into the standard-update gate, it would have gone red EVERY DAY
        # regardless of whether any skill changed — the always-fires failure that got `index_counts`
        # demoted and the quote check rescoped, committed a third time, here, by me.
        #
        # A digest whose body matches the sources is CURRENT. Its watermark records when it was last
        # rebuilt, which is a fact about history, not a defect. So the comparison ignores that one
        # line — and only that one line, so any real drift still fails.
        def _body(text):
            return re.sub(r"^last_regenerated:.*$", "", text, count=1, flags=re.M)

        if _body(new_text) == _body(existing_text):
            stamped = re.search(r"^last_regenerated:\s*(\S+)", existing_text, re.M)
            stamped = stamped.group(1) if stamped else "unknown"
            print(f"OK: {digest_path} is up to date ({len(records)} skills, "
                  f"last rebuilt {stamped}).")
            return 0
        else:
            print(f"STALE: {digest_path} does not match regenerated output.", file=sys.stderr)
            import difflib

            diff = difflib.unified_diff(
                existing_text.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=str(digest_path),
                tofile="<regenerated>",
            )
            sys.stderr.writelines(list(diff)[:200])
            return 1

    digest_path.write_text(new_text, encoding="utf-8")
    print(f"Regenerated {digest_path}: {len(records)} skills, watermark {args.as_of}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
