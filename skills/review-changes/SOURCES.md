# Sources

`review-changes` is assembled from upstream review skills. The upstream authors maintain the wording; this skill copies it and changes as little as possible. Agents do not need this file to run the skill.

## Pinned upstream files

Each row is one upstream file, the commit that last changed it when it was copied, and where its text lives here.

| Upstream file | Pinned commit | Copied into | Licence |
| --- | --- | --- | --- |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) `skills/code-review-and-quality/SKILL.md` | `28f435ea69a7` (2026-09-26) | `SKILL.md`, `references/instructions.md` | MIT, Copyright (c) 2025 Addy Osmani |
| [`cursor/plugins`](https://github.com/cursor/plugins) `thermos/skills/thermos/SKILL.md` | `5080d38e4c52` (2026-05-28) | `SKILL.md` | MIT, Copyright (c) 2026 Cursor |
| [`garrytan/gstack`](https://github.com/garrytan/gstack) `review/SKILL.md` | `5d647455f21e` (2026-10-11) | `SKILL.md` | MIT, Copyright (c) 2026 Garry Tan |
| `cursor/plugins` `thermos/skills/thermo-nuclear-review/SKILL.md` | `5102244dabd6` (2026-05-28) | `references/bugs.md` | MIT, Copyright (c) 2026 Cursor |
| `cursor/plugins` `thermos/skills/thermo-nuclear-code-quality-review/SKILL.md` | `5102244dabd6` (2026-05-28) | `references/instructions.md` | MIT, Copyright (c) 2026 Cursor |
| [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) `skills/ponytail-review/SKILL.md` | `2a1fe842d078` (2026-10-08) | `SKILL.md` | MIT, Copyright (c) 2026 DietrichGebert |
| [`2dmurali/review-loop-skill`](https://github.com/2dmurali/review-loop-skill) `review-loop/SKILL.md` | `dec43b15b0e3` (2026-05-08) | `references/loop.md` | MIT, as stated in its `SKILL.md`; the repository has no licence file |
| [`garrytan/gstack`](https://github.com/garrytan/gstack) `review/checklist.md` | `ab79e55119b7` (2026-10-11) | `references/bugs.md` | MIT, Copyright (c) 2026 Garry Tan |
| [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) `plugins/code-review/commands/code-review.md` | `c905cd8fec34` (2026-10-26) | `references/instructions.md` | Apache-2.0, see [`LICENSES/Apache-2.0.txt`](../../LICENSES/Apache-2.0.txt) |

## What each file takes

| File here | Section | Upstream |
| --- | --- | --- |
| `SKILL.md` | Approval standard, "Lead with what matters", "Honesty in Review" | `code-review-and-quality` |
| `SKILL.md` | Workflow steps 1 and 2, and the two reviewer descriptions in step 3 | `thermos` |
| `SKILL.md` | Opening line, scope default, "Validate" bullets, "Report" format | `ponytail-review` |
| `SKILL.md` | Three "Validate" bullets on quoting the code | gstack `review/SKILL.md`, "Pre-emit verification gate" |
| `references/loop.md` | Defaults, stop conditions, revision and memory rules, the two reviewer subagent rules and its no-memory limitation | `review-loop` |
| `references/bugs.md` | Prompt, scope, guidelines, final response, critical rules | `thermo-nuclear-review`, whole |
| `references/bugs.md` | "Enum & Value Completeness" | gstack `review/checklist.md`, whole section |
| `references/bugs.md` | "Gate Integrity" | gstack `review/checklist.md`, cut down |
| `references/instructions.md` | First two lines of "Approval Bar" | `thermo-nuclear-code-quality-review` |
| `references/instructions.md` | Structural remedies | `code-review-and-quality` |
| `references/instructions.md` | Opening | `/code-review`, step 4 agents 1 and 2, and its false-positive list |

## Local edits

These are the only places where the text differs from upstream. Reapply them after every update and add no others.

- Heading levels are shifted so each file has one title.
- In "Report", "Very simple English" reads "Very simple language".
- The reviewers say "the change" where upstream says "this PR" or "the branch", and Must fix where it says High priority, so one skill serves any scope and one scale.
- The bugs reviewer's "Final Response" is shortened and no longer names BugBot.
- In "Loop", the stop condition is "no validated Must fix or Should fix finding" where `review-loop` uses a score, and its Critical / Important / Minor labels read Must fix / Should fix / Nice to have.
- In "Loop", the first pass runs in the session where `review-loop` spawns a reviewer subagent for every pass; from loop 2 on it spawns one as `review-loop` does, and that reviewer runs this skill's workflow where `review-loop` gives it a scoring prompt. See "Why the review does not delegate".
- In "Loop", the max_loops check comes after the revision where `review-loop` checks it before, so the findings of the last pass are fixed too. The revision step also runs the checks its fixes need.
- "Gate Integrity" keeps gstack's definition, its one question, the two unlabelled patterns and the grouping rule. The `gstack-gate-diff` scan, the `RH-*` tags, the confidence score and the fix options are gone; the tagged patterns read as one sentence.
- The three quoting bullets drop gstack's confidence score. An unverified finding follows the existing completion rule: it is dropped or named under `Not checked`.

Written for this repo, with no upstream: the scope commands and the rule for a revision that is not checked out, the in-session review in steps 3 to 5, the concrete case for a structure finding, the validation completion rule, the blocker rule and the "Final report" section of the loop, and the one-line "Coverage" section of the bugs reviewer.

## Quality rules in AGENTS.md

Standards 0 to 6 of `thermo-nuclear-code-quality-review`, and gstack's "Enum & Value Completeness" as a rule for writing code, live in the "Code quality" section of this repo's [`rules/AGENTS.md`](../../rules/AGENTS.md), in that file's words: they apply whenever code is written, not only when it is reviewed. The structure reviewer became the instructions reviewer (`references/instructions.md`): like the `CLAUDE.md` compliance agents of Anthropic's `/code-review`, it checks the change against the loaded `AGENTS.md` and `CLAUDE.md`, code-quality rules included, and keeps the remedies and a one-line approval bar. Its opening is `/code-review`'s wording with `CLAUDE.md` read as the instruction files, and the global instructions added, since they apply to every path. Standard 7, on sequential orchestration and non-atomic updates, is dropped: it is system design more than everyday code, and the bugs reviewer covers half-applied state. The type rules of standard 5 are in the language skills (`typescript-development`, `python-development`); only its rule against silent fallbacks is in `AGENTS.md`. Anthropic's `/code-review` works the same way: it flags quality only when `CLAUDE.md` asks for it.

## Left out on purpose

- From `code-review-and-quality`: the five review axes and their question lists, tests first, verify the verification, change sizing, dead code hygiene, dependency discipline, the multi-model review pattern, review speed, handling disagreements, change descriptions, the severity prefix table, the review checklist, common rationalisations, red flags, and the `references/` checklists. See "Why the reviewers are short".
- From `thermo-nuclear-code-quality-review`: the primary questions, the list of what to flag, the list of preferred remedies, and the review tone phrases. Its standards and the Approval Bar list moved out: see "Quality rules in AGENTS.md".
- From `ponytail-review`: the `shortcut:` comment convention and the `Lean:` line.
- From `review-loop`: the 1 to 10 score, the quality gate, and model selection.

## Why the reviewers are short

The question lists and checklists were removed after two comparisons on merged pull requests, run on 2026-10-10 with one reviewer per variant and no repeats. Each finding was checked against the code afterwards.

| Round | Pull requests | Bugs, confirmed: with lists | Bugs, confirmed: short | Tokens per bugs review |
| --- | --- | --- | --- | --- |
| 1, default effort | `saml-rs` #166 and #178, `better-auth-rb` #98 | 3 of 5 | 7 of 7 | 95k against 91k |
| 2, `high` effort | `compitienda` #1569 | 5 of 5 | 5 of 5 | 146k against 150k |

Each variant found one real defect the other missed, which is within the noise between runs. The structure reviewers agreed on four of five findings in round 2. The lists added no finding and no saving, so the short files win on upkeep. Before adding a list back, run the same comparison.

The structure reviewer in round 1 carried three of the eight code-quality standards; round 2 used all eight.

## Why the review does not delegate

`thermos` launches each reviewer as a subagent. This skill follows both reference files in the session that was asked for the review. A session that wrote the change asks a subagent to run the skill; that rule lives in the user's own instructions, not here.

The comparison ran on 2026-10-10 and 2026-10-11 with Grok CLI (`grok-4.7-build-fast`) and the same reference files. Two pull requests have a documented defect: `mastodon/mastodon` #34489 (a scope removed while a caller remains) and #27511 (GHSA-ww85-x9cp-5v24, a record loaded without an owner scope). The third is a private 4,600-line pull request where two findings had recurred across earlier runs; the count below is for the one that recurred most.

At `high` effort, averaged over the three pull requests:

| How the review ran | Runs | Found the known defect | Minutes | Cost, USD API-equivalent |
| --- | --- | --- | --- | --- |
| In the session | 6 | 6 of 6 | 13 | 1.76 |
| One subagent follows both files | 3 | 3 of 3 | 19 | 3.25 |
| Two subagents, one per file | 4 | 4 of 4 | 22 to 34 | 3.3 to 4.1 |

In the session, by effort, one run per pull request at `medium` and `low`:

| Effort | Found the known defect | Minutes | Cost, USD API-equivalent |
| --- | --- | --- | --- |
| `high` | 6 of 6 | 10 to 16 | 1.76 |
| `medium` | 3 of 3 | 6 to 11 | 1.59 |
| `low` | 3 of 3 | 2 to 10 | 0.54 |

Delegating did 2.5 to 4 times the work for the same result: each subagent re-read the diff and the surrounding files, and the session that launched it re-read the code again to validate findings it had not investigated. Hits were counted by matching the defect's file and symbol in the report. Every run started from a clean session, so none measured a session reviewing its own change.

The 2026-10-29 comparison for #53 (report and data on branch `experiment/review-changes-53`) repeats the question with this candidate's instructions reviewer instead of the old structure reviewer, using `gpt-6.1-sol` at `high` effort. One paired run on each of five cases found both known Mastodon defects in both variants. The one-session variant reported all five clear planted violations and one additional real defect that two reviewers omitted; two reviewers reported four of the five clear violations. Across the five cases, the one-session variant had 15 distinct confirmed problems and two reviewers had 13, excluding an ambiguous synthetic file-size finding. Two reviewers used 4.31 times the total tokens, or 2.28 times when cache-hit input is excluded, and summed review durations were 8.18 versus 9.72 minutes. This small comparison supports keeping the sequential default; it does not measure loop passes or self-review.

The loop is that unmeasured case from its second pass on: the session re-reviews fixes it has just written, with its earlier conclusions still in context. So those passes go to a fresh reviewer subagent, as `review-loop` does for every pass. This rests on `review-loop`'s reasoning (anchoring), not on a comparison here; none has been run on loop passes.

## How to update from upstream

1. For each row of "Pinned upstream files", get the commit that last changed the file:

   ```bash
   gh api "repos/<owner>/<repo>/commits?path=<path>&per_page=1" --jq '.[0].sha'
   ```

   If it starts with the pinned commit, that file has not changed; skip it.
2. For a file that changed, read what changed since the pin:

   ```bash
   gh api "repos/<owner>/<repo>/compare/<pinned>...<new>" --jq '.files[] | select(.filename == "<path>") | .patch'
   ```

3. Paste the new upstream wording over the matching section here. Copy and paste; do not reword.
4. Reapply only the edits listed under "Local edits". If upstream added a section, decide whether it belongs here or under "Left out on purpose", and record the decision in this file.
5. Update the pinned commit and date in the table.
6. Bump `version` in `.claude-plugin/plugin.json`.

## MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
