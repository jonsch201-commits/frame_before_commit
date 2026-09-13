---
# DRAFT dataset card, rewritten 2026-09-13 07:5x CDT to HuggingFace's datasetcard_template.md after Jon asked how the
# first draft compared to gold-standard cards. The first draft (01:19) was written from memory, not from the template;
# that failure is logged in the assembling seat's session log with its detector.
# Status: not uploaded. Numbers describe the PRIVATE candidate; the public derivation re-applies the
# personal-identifier fences and replaces them. License and third skill are Jon's decisions.
pretty_name: "WikiSkills in Practice: a five-trunk Claude knowledge base, its skills, and its retrieval graph"
language:
- en
license: other
tags:
- text
- wikiskills
- knowledge-base
- graph-rag
- agent-skills
- claude-code
- personal-project
task_categories:
- text-retrieval
size_categories:
- 10K<n<100K
configs:
- config_name: chunks
  data_files: data/chunks.jsonl
  default: true
- config_name: files
  data_files: data/files.jsonl
- config_name: edges
  data_files: data/edges.jsonl
---

# Dataset Card for WikiSkills in Practice

The derived, combined tree of two trunks of a six-agent Claude Code project (CFL, the foundational layer; Professional, the rigor seat), the skills those agents run, and the retrieval graph built from empty over that tree. It is the artifact Jon's LessWrong post points at.

## Dataset Details

### Dataset Description

Six months of a personal project in which Claude agents maintain a wiki as their record, read it before acting through named skills, and retrieve over it with a hybrid lexical, dense and link-graph index. This dataset is the shipped tree after derivation (an explicit include spec and exclusion list per trunk, with a manifest and a derivation log per half) plus the index built from that tree only. It is the private candidate; a public version re-applies identifier fences and will carry its own numbers.

- **Curated by:** Jon (first name only; organisation n/a, by his ruling of 2026-09-12: *"Jon, n/a, first push is private."*)
- **Funded by:** no one; personal project
- **Shared by:** Jon
- **Language:** English
- **License:** pending Jon's choice (`other` until he names one)

### Dataset Sources

- **Repository:** the private git branch `pr4-combined-private` (Jon's push); the public repository does not yet exist
- **Paper:** none. Jon's LessWrong post is the companion text; it is not yet posted
- **Related paper Jon asked about, 2026-09-07:** https://huggingface.co/papers/2608.13940, not yet read by the assembling seat

## Uses

### Direct Use

Reading the skills (`cfl/skills/`, `professional/skills/`) and their reference material as worked examples of agent discipline; querying the graph (`graph/index.sqlite`, or the `chunks` config) to see how a six-month agent record retrieves; reproducing every measurement in the README with the command beside it; studying the derivation logs as an example of publishing a subset of a working tree with per-file provenance.

### Out-of-Scope Use

Training a model to imitate the author or the agents; treating any number in the tree as current without re-running its command; using the skills as actuarial guidance (the author is an actuary and says this is not actuarial work; see Bias, Risks and Limitations); resolving any name found here to a person.

## Dataset Structure

Three configs, all JSONL, exported from `graph/index.sqlite` so the Hub viewer can render them:

| config | rows | fields |
|---|---|---|
| `chunks` (default) | 13,290 | `chunk_id`, `path`, `ord`, `heading`, `start_line`, `end_line`, `ntok`, `text`, `kind`, `tier` |
| `files` | 1,302 | `path`, `sha256`, `bytes`, `kind`, `tier` |
| `edges` | 4,169 | `src`, `dst`, `kind`, `raw` (wikilink and path references; 2,032 resolve to a shipped file) |

The full index `graph/index.sqlite` (157.4 MB) adds `vectors` (13,290 rows, 512-d, potion-retrieval-32M), `docvecs` (1,302), `postings` (1,106,443 term to chunk rows), `terms` (25,314), `vocab_tri` (135,572 trigram rows) and `meta`. All chunks are in the `knowledge` tier; no transcripts ship. The source tree itself: 1,002 markdown pages, 278 Python and 39 shell scripts, 16 JSON files, across `cfl/` (1,015 files) and `professional/` (330). No splits: this is a record, not a benchmark.

## Dataset Creation

### Curation Rationale

Jon's post claims a repository with skills, their test data, and a knowledge graph. This tree exists so that every sentence of the post is true of an artifact a reader can open, and so that what was cut is defended by class and reason rather than absent.

### Source Data

#### Data Collection and Processing

Each half is derived, not authored, by one deriver (`cfl/scripts/audit/derive_public_tree.py`) run against an explicit include spec and exclusion list; the deriver writes `MANIFEST.sha256` (every shipped file with hash and size) and `DERIVATION-LOG.md` (every excluded file with class, line and reason, plus a report-only section for files flagged and deliberately kept). Both manifests were recomputed against disk by two seats other than the author. The graph was built from empty over the shipped tree with CFL's `build_index.py`; the command is in the README. Nothing was hand-placed or hand-removed. CFL's half was derived three times on 2026-09-13 as its spec was corrected (dependency directories added, hook runtime state withheld); the superseded derivations are kept off-artifact.

#### Who are the source data producers?

Jon, whose typed prompts and rulings are the wiki's primary sources, and six Claude agents across five knowledge bases: Professional (the assembler, a Fable model), CFL, Secretary, Herald and Soul (Claude Personal), and Antigravity. Each agent's pages carry its seat and session in frontmatter where the trunk's conventions require it.

### Annotations

#### Annotation process

None in the labelling sense. Frontmatter fields (`kind`, `status`, `trunk`, dates) are written by the agents as they work and are what the deriver's frontmatter rules read.

#### Who are the annotators?

The agents named above; no external annotators.

### Personal and Sensitive Information

This private candidate does **not** claim to be scrubbed of personal information. Jon's ruling of 2026-08-19 makes identifiers a non-cut on his private repositories; the public derivation re-applies fences for names, e-mail addresses, phone numbers, addresses, account and money identifiers, and one no-remote path, each with a planted-file leak control that must exclude and log every class before publication. Two rows are held on Jon's read and neither seat decides them: eleven Professional pages and one script carrying four family names; one CFL module and one CFL reference file carrying 65 and 121 name hits respectively. Third-party and family names are gated on consent in both versions. There is no removal-request channel yet; the public card must have one before upload.

## Bias, Risks, and Limitations

- **The tree points at files it does not contain.** 66 of CFL's 259 excluded files (92 content exclusions plus 167 withheld state files) are referenced by name from shipping files, 859 references; 5 of Professional's 12, 6 references. Each name has a row in a derivation log. A citation can land on a name with nothing behind it.
- **Skills are typed as commands often and invoked by name by the agents rarely.** Across 197 main sessions since 2026-09-05: frame-before-commit 26 tool calls, wiki-query 5, ground-before-stating 0. The zero is an invocation record, not a measure of the discipline, because that skill loads at session open in one trunk and is applied without its name elsewhere. No measurement here shows effect.
- **The post says three skills; 47 skill directories ship.** Three carry reference material. The third skill named in the post is pending Jon's confirmation, and the sentence of his draft that names it is truncated in every copy on this machine.
- **Code that cannot run.** Of 125 shipped CFL scripts with selftests, 97 pass, 9 were unresolved at a 40-second cap, and all six missing-dependency failures are one module withheld by the name fence. 111 shipped scripts have no selftest and are ungraded.
- **Not actuarial work.** The author is an actuary and grounds the skills in actuarial standards; nothing here was produced as actuarial work and the post's disclaimer says so.
- **A single author's record.** Six months of one person's project with one person's framing. The wiki records what the agents believed at the time, including claims later struck; struck text is kept and marked, never deleted.
- **The graph is derived and only as rich as its source.** It is rebuildable in about 22 seconds from the tree; it should never be treated as containing anything the tree does not.

### Recommendations

Re-run any number before citing it; read the derivation log before concluding a referenced file is missing; treat invocation counts as floors on invocation and as nothing about effect; do not use the skills in professional work without testing them against the standards that apply to that work.

## Citation

Pending: Jon's LessWrong post, once posted, is the citation. Until then, cite the repository and its commit.

## Glossary

- **Trunk:** one agent's knowledge base and working tree; the project runs five.
- **Seat:** one Claude Code session acting for a trunk.
- **Derivation:** producing the shipped subset of a working tree from an explicit spec, with manifest and log.
- **WikiSkills:** the pattern of a wiki as the record and skills that read it before acting.

## More Information

The README beside this card carries the criteria table (what passed, what failed by measured number), the build command, and both trunks' cut defences. The assembling seat's session log records every struck claim of the assembly night as it happened.

## Dataset Card Authors

Claude Professional (Fable 5.1), session 682d274b, on Jon's instruction; artifact verified against disk by Claude CFL and Antigravity.

## Dataset Card Contact

Jon, via the repository's issues once it is public. No e-mail is published.
