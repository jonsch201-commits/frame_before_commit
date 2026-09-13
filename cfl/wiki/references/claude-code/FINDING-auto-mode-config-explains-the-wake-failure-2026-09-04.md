---
kind: reference-finding
date: 2026-09-04
time: 15:2x CDT
source_url: https://code.claude.com/docs/en/auto-mode-config.md
fetched_at: 2026-09-04T20:2x UTC (by CFL, deliberately, first fetch this repo has ever made)
status: LIVE
owner: cfl
---

# The page we did not have explains the failure we shipped a workaround for

⭐ **EU-6 named `auto-mode-config.md` as one of five unmirrored pages that would have changed today.
Fetched it. It does — and it does something better than I expected: it CONFIRMS the fix I built,
by naming the mechanism.**

## ⛔ THE ROOT CAUSE, in the documentation's own words

> **"By default, narrow Bash and PowerShell allow rules such as `Bash(npm test)` stay in effect in
> auto mode, and Claude Code resolves them BEFORE the classifier runs. Claude Code suspends only the
> broad rules that grant arbitrary code execution, such as `Bash(*)` or wildcarded interpreters."**

⭐ **So a narrow allow rule never reaches the classifier at all — and cannot be broken by the
classifier being unavailable.**

⛔ **`/wake`'s pre-flight was NOT narrow.** Its interpolations were compound shell:
`test -f … && echo "$(pwd) … $(wc -c < …)" || ( test -f … && … || … )` — `&&`, `||`, subshells and
command substitution. **That matches no narrow allow rule**, so it fell through to the classifier,
and when the classifier was unavailable the command died at line one in every trunk at once.

⭐ **THE FIX I SHIPPED THIS MORNING IS THE DOCUMENTED MECHANISM, NOT A WORKAROUND.** Moving the
pre-flight into `bash scripts/audit/wake_preflight.sh` makes it match the narrow rule
`Bash(bash scripts/audit/*)` already in that command's `allowed-tools` — **resolved before the
classifier, immune to its availability.** ⚠️ **I did not know that when I built it. I reasoned from
the failure and got the right shape; the documentation supplies the WHY, and the why is what makes
it durable rather than lucky.**

## ⚠️ AND A SECOND, FLEET-WIDE FACT NOBODY HERE KNEW

> **"By default, the classifier trusts only the working directory and the current repo's configured
> remotes. Actions like pushing to your company's source-control org or writing to a team cloud
> bucket are blocked until you add them to `autoMode.environment`."**

⛔ **CFL's courier writes into SIX other trunks' trees** — `G:\My Drive\Claude\<peer>\exchange\inbound`
and `N:\antigravity-hub\` — **every one of them outside the working directory and outside this
repo's remotes.** ⭐ **By default those destinations are exactly what the classifier is built to
treat as "external," i.e. potential exfiltration.** ⚠️ **That delivery has been working, so
something is currently permitting it; what is NOT true is that it is permitted BY DESIGN. Nobody
declared these trunks trusted, so the fleet's whole letter channel rests on an undeclared
assumption.** **Not a defect today. A dependency nobody wrote down.**

## ⛔ THE BOUNDARY THAT DECIDES WHO MAY FIX THIS

> **"The classifier doesn't read `autoMode` from project settings in `.claude/settings.json` or
> `.claude/settings.local.json`. Both files live in the repo directory, so a checked-in repo or a
> build step could otherwise inject its own allow rules."**

⭐ **`autoMode` is readable ONLY from `~/.claude/settings.json` or managed settings.** ⛔ **CFL's
standing constraint is: never edit `~/.claude` except via repo sync.** ⚠️ **So configuring the
classifier is NOT a change CFL can make in its own tree, by design on both sides.** **It is a
Jon-gated action or a `sync-universal.sh` change, and saying so is the disposition — not a deferral
dressed as one.**

## Three capabilities this repo did not know existed

1. ⭐ **`PermissionDenied` hook** — *"receives it as `tool_input`"*. **CFL has spent today unable to
   see the exact input of denied calls.** Candidate instrument.
2. **`claude auto-mode defaults` / `config` / `critique`** — print built-in rules, print the
   effective config, and get feedback on custom rules. ⭐ **`config` is a real answer to "what is
   actually in force," which is the question this repo asks about everything else.**
3. **`/auto-mode-setup`** — drafts `environment` entries from the project and recent sessions.
   ⚠️ **Writes to `~/.claude/settings.json`, so the same boundary applies.**

## What this does NOT say, stated so nobody reads a gap as an answer

⛔ **There is no documented fallback for an unavailable classifier.** The page points at
`errors#auto-mode-cannot-determine-the-safety-of-an-action` for that case and says Claude Code
*"denies the action without recording it under Recently denied."* ⭐ **So: fail-CLOSED, silently,
with no retry surface — which is precisely the behaviour we observed.** ⚠️ **The remedy is
therefore structural (be narrow enough never to need the classifier), not configurational. That is
the fix already shipped.**

⛔ **And the page says nothing about shell interpolation inside a slash-command file evaluated at
load time.** ⚠️ **Our conclusion that a bang-backtick block is graded as Bash regardless of content
remains OUR inference from observed behaviour, not a documented rule. UNKNOWN, and it does not
become known by being useful.**

`owner:` CFL · **First deliberate documentation fetch in this repo's history; EU-3's provenance
header shape is demonstrated by this file's own frontmatter.**
