# Plan: adaptive reviewers for large diffs and loop rounds

Pre-registered for [issue #73](https://github.com/salasebas/skills/issues/73) before any review ran. The cases, the expected defects and the selection criteria below do not change after the runs start.

## Question

Does splitting the review into specialized reviewers find more confirmed problems, or finish sooner, on large diffs and loop rounds, at a cost worth paying? Small changes are already covered by [#53](https://github.com/salasebas/skills/blob/08096e507ade1442e52b16fb67eb085540b8c6a5/experiments/review-changes-53/REPORT.md); this plan adds only what #53 did not measure.

## Variants

All variants use the skill at `73683e5f0af7cb4417a5cd48a9c1b5cec1309c3a` and change only Workflow step 3 (and, for loop rounds, the reviewer count in `references/loop.md`).

- **A, current.** One review follows `bugs.md`, then `instructions.md`. Outside a loop it runs in the session; in a loop round the session starts one fresh reviewer.
- **B, two specialists.** Two fresh-context subagents in parallel, one per reference file.
- **C, adaptive.** The session chooses reviewers by the criteria below.

### Selection criteria for C

- **Behavior lines:** added plus deleted lines, not counting lockfiles, generated or vendored files, and documentation.
- **Risk:** the change touches money or payments, authentication or authorization, concurrency or locking, or schema and data migrations.
- **Small** (under 500 behavior lines) without risk: one review in the session, as A.
- **Small with risk:** the B pair, plus one more bugs reviewer limited to the risky files.
- **Large** (500 behavior lines or more): one bugs reviewer per domain (two to four domains, grouped by the code they own) and one instructions reviewer across the whole change. With risk, one more bugs reviewer limited to the risky files. Five subagents at most.

500 lines sits above the #53 medium case (ports #67, 430 lines), which one reviewer handled without misses. File count is not a trigger.

## Cases

All from `compitienda/compitienda` (private). Each has a known defect: the pull request itself later added a commit that fixes it, so the reviewed head is the commit before that fix. Reviewers get a repository fetched only up to the reviewed head, so the fix is not visible.

| Case | Pull request | Base | Reviewed head | Size | Behavior lines | C class |
| --- | --- | --- | --- | --- | ---: | --- |
| `mech` | #2067, Ruby 3.4 and official Standard, mostly autocorrect | `4d788af37134` | `b4cda5b926e4` | 987 files, +3,012/-4,965 | 7,458 | Large, risk (migrations) |
| `cross` | #2096, Rails 7.2, across jobs, search, storage, config | `0b1f0356dff1` | `d8dfb3b13295` | 134 files, +766/-467 | 697 | Large, risk (migrations, locking) |
| `risk` | #2122, fixed table tip, money | `1f799b11ebc5` | `84577c314b3c` | 10 files, +286/-39 | 325 | Small, risk (payments) |
| `loop` | #2122 round 2, after the fix | `1f799b11ebc5` | `87f6bd97c774` | round change: 1 file, +4/-3 | 7 | Small, risk (payments) |

### Known defects

- `mech`: a unique-index migration switches its guard to `index_name_exists?`, which is true for an index left invalid by an interrupted concurrent build, so a replay skips the unique index; the `change` method with a conditional is also not reliably reversible. Fixed by `fbb58d476b3e`.
- `cross`: pg_search stays on a version without Active Record 7.2 support (search breaks), and two serializers call an Active Storage URL-options API that Rails 7.2 changed (attachment URLs break). Fixed by `dcc9421ac4`. The same commit also stabilizes two specs; those count as test findings, not as the known defects.
- `risk`: the change sends a fixed `tip_cents` into `Payments::CreatePayment`, whose unchanged guard still requires the whole charge to fit the session's percent-tip capacity, so a valid fixed tip above the session percent is rejected. The defect sits outside the diff. Fixed by `87f6bd97c7`.
- `loop`: no known defect. Every confirmed finding counts.

## Held constant

Codex CLI 0.167.0, `gpt-6.1-sol` at `high` effort for every session and subagent, the same prompt per case, a fresh HOME per run with only `rules/AGENTS.md` and the skill variant, plugins, apps, memories and web search off, read-only sandbox, and the #53 read-only command allowlist. See Amendments: the runs use Claude Opus 5.5. Each case and variant runs twice, each time from a fresh session.

## Recorded per run

Confirmed problems (known defect found or missed), refuted findings, duplicates in the final report, wall time from launch to exit, sum of session durations, total tokens, cache-hit input, and output. Coordinator validation is part of every run's cost, because the coordinator is the root session.

## Amendments

These change the harness only. Cases, known defects, criteria and the decision rule stay as written above.

1. 2026-11-10: the Codex account reached its usage limit after the pilot and three batch runs; the rest failed on start. On the owner's instruction, every run uses Claude Code 2.1.322 with `claude-opus-5-5` at `high` effort instead, subagents through the Agent tool. User settings, skills and MCP servers are off (`--setting-sources ""`, `--disable-slash-commands`, `--strict-mcp-config`); the global rules arrive through `--append-system-prompt`, the skill as files.
2. 2026-11-10: the first Claude batch allowed only a list of read-only command prefixes. It denied `cd`, `git -C`, shell variables and chained commands, and most subagents, which get absolute paths, then reviewed with no git access at all. That batch is discarded as a comparison. The rerun allows Bash inside Claude Code's OS sandbox (no network, writes only to the worktree and temporary paths) and denies reads under `~/Projects`, `~/.t3`, `~/.claude` and `~/.codex`, so the source checkout that holds the fix commits cannot be read.

## Decision rule

Change the default only if a split variant finds a known defect that A misses in both repeats, or cuts wall time by a third at no loss of findings, and the cost stays under twice A's uncached tokens. Otherwise keep one reviewer and record the evidence in `SOURCES.md`.
