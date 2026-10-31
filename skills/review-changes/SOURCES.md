# Sources

`review-changes` is assembled from upstream review skills and condensed. `SKILL.md` keeps upstream's ideas in as few words as they need, and the loop stays close to `sol-loop`. Agents do not need this file to run the skill.

## Pinned upstream files

Each row is one upstream file, the commit that last changed it when it was copied, and where its text lives here.

| Upstream file | Pinned commit | Copied into | Licence |
| --- | --- | --- | --- |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) `skills/code-review-and-quality/SKILL.md` | `28f435ea69a7` (2026-09-26) | `SKILL.md` | MIT, Copyright (c) 2025 Addy Osmani |
| [`cursor/plugins`](https://github.com/cursor/plugins) `thermos/skills/thermos/SKILL.md` | `5080d38e4c52` (2026-05-28) | `SKILL.md` | MIT, Copyright (c) 2026 Cursor |
| [`garrytan/gstack`](https://github.com/garrytan/gstack) `review/SKILL.md` | `5d647455f21e` (2026-10-11) | `SKILL.md` | MIT, Copyright (c) 2026 Garry Tan |
| `cursor/plugins` `thermos/skills/thermo-nuclear-review/SKILL.md` | `5102244dabd6` (2026-05-28) | `SKILL.md` | MIT, Copyright (c) 2026 Cursor |
| `cursor/plugins` `thermos/skills/thermo-nuclear-code-quality-review/SKILL.md` | `5102244dabd6` (2026-05-28) | `SKILL.md` | MIT, Copyright (c) 2026 Cursor |
| [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) `skills/ponytail-review/SKILL.md` | `2a1fe842d078` (2026-10-08) | `SKILL.md` | MIT, Copyright (c) 2026 DietrichGebert |
| [`t3dotgg/tstack`](https://github.com/t3dotgg/tstack) `skills/sol-loop/SKILL.md` | `6efae364201a` (2026-10-24) | `references/loop.md` | MIT, Copyright (c) 2026 Theo Browne |
| [`garrytan/gstack`](https://github.com/garrytan/gstack) `review/checklist.md` | `ab79e55119b7` (2026-10-11) | `SKILL.md` | MIT, Copyright (c) 2026 Garry Tan |
| [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) `plugins/code-review/commands/code-review.md` | `c905cd8fec34` (2026-10-26) | `SKILL.md` | Apache-2.0, see [`LICENSES/Apache-2.0.txt`](../../LICENSES/Apache-2.0.txt) |

## What each part takes

| Part | Upstream |
| --- | --- |
| Opening line, scope default, "Validate", "Report" format | `ponytail-review` |
| Approval standard, the closing lines of "Report" | `code-review-and-quality` |
| "Workflow" steps 1 and 2 | `thermos` |
| Quoting and generated-symbol bullets in "Validate" | gstack `review/SKILL.md`, "Pre-emit verification gate" |
| "Bugs": side effects, developer setup, feature gates, intended breakage, finishing research, the PR discussion | `thermo-nuclear-review` |
| "Bugs": new values and gate integrity | gstack `review/checklist.md` |
| "Bugs": skipping what a linter catches; "Instructions": opening | `/code-review` |
| "Instructions": the restructuring line | `code-review-and-quality` |
| "Reviewer" and `references/loop.md` | `sol-loop` |

## Local edits

- `references/bugs.md` and `references/instructions.md` are folded into `SKILL.md`: every review reads both, so nothing is saved by keeping them apart. The start of a reviewer moved from the loop to "Reviewer", since a session that wrote the change needs it too.
- "Bugs" is condensed from about 1,000 words to about 300. Three calls for extreme thoroughness, the persona, the examples under each guideline, and the grep walkthrough are gone. Gate integrity keeps gstack's definition and its one question, and its grouping rule is covered by Workflow step 5.
- "Instructions" drops the eight named remedies and the lines on nits: the first repeat `AGENTS.md`, the second repeat "Report".
- "Report" drops "Honesty in Review" down to two sentences.
- The review runs read-only `git` and `gh`, where it used to forbid all network commands while its scope and PR discussion steps need `gh`.
- In the loop, Sol reads "the reviewer" and the blocker / should / nit labels read Must fix / Should fix / Nice to have. The T3 tool details, the Sol default, the `git fetch` base rules and usage reporting are gone. The brief asks for this skill's Workflow where `sol-loop` gives its own review rules, and the report adds that fixes after the last round are unreviewed.

Written for this repo, with no upstream: the scope commands and the rule for a revision that is not checked out, and the validation completion rule.

## Quality rules in AGENTS.md

Standards 0 to 6 of `thermo-nuclear-code-quality-review`, and gstack's "Enum & Value Completeness" as a rule for writing code, live in the "Code quality" section of this repo's [`rules/AGENTS.md`](../../rules/AGENTS.md), in that file's words: they apply whenever code is written, not only when it is reviewed. The structure reviewer became "Instructions": like the `CLAUDE.md` compliance agents of Anthropic's `/code-review`, it checks the change against the loaded `AGENTS.md` and `CLAUDE.md`, code-quality rules included, and keeps the remedies and a one-line approval bar. Its opening is `/code-review`'s wording with `CLAUDE.md` read as the instruction files, and the global instructions added, since they apply to every path. Standard 7, on sequential orchestration and non-atomic updates, is dropped: it is system design more than everyday code, and the bugs reviewer covers half-applied state. The type rules of standard 5 are in the language skills (`typescript-development`, `python-development`); only its rule against silent fallbacks is in `AGENTS.md`. Anthropic's `/code-review` works the same way: it flags quality only when `CLAUDE.md` asks for it.

## Convergence

Step 5's one finding per class of bug comes from the Claude Code team's [How the Claude Code team does code review](https://claude.dev/blog/solving-code-review-at-anthropic/) (2026-10-15), written in this repo's words. The same post caps review at three rounds and re-reviews only the diff after the first, as `sol-loop` does: the team saw an agent author and an agent reviewer run more than fifty rounds on one pull request, and about 59% of what the reviewer kept flagging was code it had already seen on the first pass.

## Left out on purpose

- From `code-review-and-quality`: the five review axes and their question lists, tests first, verify the verification, change sizing, dead code hygiene, dependency discipline, the multi-model review pattern, review speed, handling disagreements, change descriptions, the severity prefix table, the review checklist, common rationalisations, red flags, and the `references/` checklists. See "Why the reviewers are short".
- From `thermo-nuclear-code-quality-review`: the primary questions, the list of what to flag, the list of preferred remedies, and the review tone phrases. Its standards and the Approval Bar list moved out: see "Quality rules in AGENTS.md".
- From `ponytail-review`: the `shortcut:` comment convention and the `Lean:` line.
- From `sol-loop`: the T3 tools, the default to Sol, and the token usage line.

## Why the reviewers are short

The question lists and checklists were removed after two comparisons on merged pull requests, run on 2026-10-10 with one reviewer per variant and no repeats. Each finding was checked against the code afterwards.

| Round | Pull requests | Bugs, confirmed: with lists | Bugs, confirmed: short | Tokens per bugs review |
| --- | --- | --- | --- | --- |
| 1, default effort | `saml-rs` #166 and #178, `better-auth-rb` #98 | 3 of 5 | 7 of 7 | 95k against 91k |
| 2, `high` effort | `compitienda` #1569 | 5 of 5 | 5 of 5 | 146k against 150k |

Each variant found one real defect the other missed, which is within the noise between runs. The structure reviewers agreed on four of five findings in round 2. The lists added no finding and no saving, so the short files win on upkeep. Before adding a list back, run the same comparison.

The structure reviewer in round 1 carried three of the eight code-quality standards; round 2 used all eight.

## Why the review does not delegate

`thermos` launches each reviewer as a subagent. This skill reviews in the session that was asked for the review. A session that wrote the change starts one reviewer subagent: see "Reviewer".

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

The [first 2026-10-29 round for #53](https://github.com/salasebas/skills/blob/08096e507ade1442e52b16fb67eb085540b8c6a5/experiments/review-changes-53/REPORT.md) repeats the question with this candidate's instructions reviewer instead of the old structure reviewer, using `gpt-6.1-sol` at `high` effort. One paired run on each of five cases found both known Mastodon defects in both variants. The one-session variant reported all five clear planted violations and one additional real defect that two reviewers omitted; two reviewers reported four of the five clear violations. Across the five cases, the one-session variant had 15 distinct confirmed problems and two reviewers had 13, excluding an ambiguous synthetic file-size finding. Two reviewers used 4.31 times the total tokens, or 2.28 times when cache-hit input is excluded, and summed review durations were 8.18 versus 9.72 minutes. This small comparison supports keeping the sequential default; it does not measure loop passes or self-review.

A [second round](https://github.com/salasebas/skills/blob/08096e507ade1442e52b16fb67eb085540b8c6a5/experiments/review-changes-53/ROUND2.md) uses the same cases, prompts, fixture, and model with new sessions. It ends at 15 confirmed problems each: two reviewers add two instruction findings but again omit the cross-API bug and narrative comment. They use 4.30 times the total tokens, or 2.31 times with cache-hit input excluded. Across both rounds, each variant finds fifteen distinct problems at least once, with two unique to each. The differing findings do not establish a general recall winner; the sequential workflow remains the cheaper default.

The loop is that unmeasured case: the session would re-review code it has just written, with its own conclusions still in context. So every round goes to a new reviewer subagent, as `sol-loop` does with a separate reviewer model. This rests on that reasoning (anchoring), not on a comparison here; none has been run on loop rounds.

The reviewer prefers another model after a run on 2026-10-29 in T3 Code: three merged `compitienda` pull requests (#1962, #1935, #1917), one run per reviewer model, each started by a GPT-6.1-Sol coordinator through `delegate_task` and its findings confirmed by that coordinator. Of seven distinct problems, a GPT-6.1-Sol reviewer found 2, GPT-6-Astra 4 and Claude Opus 5.5 6; Sol approved two pull requests that had confirmed problems. Opus took 2.7 to 12.5 minutes, the others 1.5 to 3.7. One run per cell, so this sets a default, not a ranking.

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

3. Decide whether the change alters what a review should do. If it does, write it here in as few words as it needs.
4. If upstream added a section, decide whether it belongs here or under "Left out on purpose", and record the decision in this file.
5. Update the pinned commit and date in the table.

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
