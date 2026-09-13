---
title: "LessWrong posting policy as read on 2026-09-11: LLM writing policy, new-user moderation, frontpage criteria"
kind: source
date: 2026-09-11
fetched: "2026-09-11 16:2x CDT by professional (session 682d274b) via WebFetch; summaries by a small model over the fetched pages; quoted sentences are verbatim from the pages"
status: LIVE — re-fetch before publication; the LLM policy page is dated 2025-03-24 and may have been amended
sensitivity: T1
sources:
  - "https://www.lesswrong.com/posts/KXujJjnmP85u8eM6B/policy-for-llm-writing-on-lesswrong"
  - "https://www.lesswrong.com/posts/LbbrnRvc9QwjJeics/new-user-s-guide-to-lesswrong"
  - "https://www.lesswrong.com/faq"
links: "lesswrong-publication-standards (wanted, not yet written), DOSSIER-JON-LESSWRONG-POST-1.md (exchange/inbound on master, not a wiki page -- see disposition footer)"
query_keys:
  - "LessWrong LLM writing policy first-time writers AI text"
  - "LessWrong new user first post moderation"
  - "LessWrong frontpage criteria personal blog"
---

# Why this page exists
Jon, 09-11 turn 1610, verbatim: *"Professionalism must fully read lesswrong policy and ensure lesswrong context is meaningfully in its graph."* Before this page the graph held only Antigravity's paraphrase of the policy `[queried 16:0x: five hits, all Antigravity letters]`. This page is the policy in the policy's own words.

# 1. Policy for LLM writing on LessWrong (page dated 2025-03-24)

Verbatim sentences from the page:

- *"first-time writers are not permitted to use any AI text output in their submissions"*
- For established users: *"you must have added significant value beyond what the AI produced, the result must meet a high quality standard, and you must vouch for everything in the result"*
- *"if you are using AI for writing assistance, you should spend a minimum of 1 minute per 50 words"*, and avoid unverified information and stereotypical AI writing patterns.

Allowed with restrictions, paraphrased by the fetch model:
- Collapsible sections: AI-generated content may be placed in collapsible blocks without quality vetting if labeled, provided the post makes sense without expanding it.
- Quotation for analysis: AI passages may be included when labeled with generation metadata, as the subject of analysis, with substantive human commentary.
- AI agent exception: autonomous agents may post without human collaboration only with non-public information substantially improving humanity's prospects, after contacting moderators first.

**What this means for PR 4 and the first post, stated here so it is retrievable:** the collapsible LLM block is an allowance that sits under the established-user standard. The first-time-writer sentence is unconditional. A first post by Jon that embeds any AI-written text, in a block or not, is outside the policy as written. The technical addendum therefore belongs in the repository, linked from the post, not inside the post. Whether Jon is a first-time writer on LessWrong is not known to this trunk and is question 7 for him.

# 2. New user's guide

- *"We review every first post and comment before it goes live to ensure it's up to par."* Rejected submissions appear on a public page with moderator feedback.
- Rejection dimensions, paraphrased: epistemic standards (probabilistic reasoning, calibration), clarity (*"Write a clear introduction"*), engagement with prior LessWrong discussion on the topic, audience awareness (not a generic cross-post), and a higher bar on AI topics: *"Aim for a high standard if you're contributing on the topic AI"*.
- Prohibited: sock-puppet upvoting, evading moderation with new accounts, vote brigading.

# 3. FAQ

- Frontpage posts should be *"broadly relevant to LessWrong's main interests; timeless, i.e. not about recent events; and are attempts to explain not persuade."*
- Personal blogposts *"can be on any topic of interest to the author including divisive topics (which we generally keep off the frontpage), discussions about the community, and meta posts about LessWrong itself."*
- The FAQ does not address AI-generated content, self-promotion, or linking to external repositories. Alignment Forum posts are automatically cross-posted to LessWrong.

# 4. Consequences carried into the PR 4 frame
1. The post is Jon's, in Jon's words, with zero AI text if he is a first-time writer. Consistent with his own 09-11 words: *"I must own the first lesswrong LLM post."*
2. The post must open with its main point. The "literary" opening is reserved for established users.
3. The post should cite prior LessWrong discussion of memory, wikis and multi-agent setups; that is external research and Antigravity's row.
4. Frontpage is plausible only if the post explains rather than persuades and is not about a recent event. The Hugging Face incident, which Jon names as a motivation, should be motivation in his head, not the post's subject.
5. Reviewing his draft against these criteria is this trunk's review-layer job, and the review must not cost him more than the draft did.

**Disposition (2026-09-12 wiki-master, C22):** the frontmatter `links:` field carried two dangling body wikilinks. `lesswrong-publication-standards` is OPEN — no page under this name exists in `wiki/`; it would be a distillation of this source into standing rules and is wanted, not written; do not stub it. `DOSSIER-JON-LESSWRONG-POST-1.md` exists at `N:/claude-professional/exchange/inbound/DOSSIER-JON-LESSWRONG-POST-1.md` (master's inbound, confirmed on disk) but is an exchange artifact, not a wiki page, so no wikilink can resolve to it under this check's roots (`wiki/` + `CLAUDE.md`/`WAKE.md`); cited above as a plain path instead.
