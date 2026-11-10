# Specialized reviewers on large diffs and loop rounds

Keep one reviewer as the default. Splitting the review added confirmed findings on three of the four cases, but at 2.3 to 4.7 times the cost of one review and about twice the wall time on every case except the loop round. It fails the [pre-registered decision rule](PLAN.md#decision-rule). Neither split caught the known defects in the two large upgrades.

This answers [issue #73](https://github.com/salasebas/skills/issues/73). The cases, criteria and rule were fixed in [PLAN.md](PLAN.md) before the first run. The runs used skill `73683e5`, Claude Code 2.1.322 and `claude-opus-5-5` at `high` effort for every session and subagent, two fresh runs per case and variant: 24 runs, USD 144.89 API-equivalent. Why the model is not the one #53 used, and why one batch was thrown out, is under [Amendments](PLAN.md#amendments).

## Results

A known defect is one the pull request fixed in a later commit; see [PLAN.md](PLAN.md#known-defects). "Confirmed" counts distinct problems that survived checking against the code (below). Each cell shows repeat 1 / repeat 2.

| Case | Variant | Known defect found | Confirmed problems | Refuted | Minutes | USD | Uncached tokens (M) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `mech`, 987 files | A | no / no | 0 / 1 | 1 / 0 | 9.8 / 7.8 | 5.52 / 3.60 | 0.30 / 0.23 |
| | B | no / no | 2 / 1 | 0 / 0 | 20.6 / 18.3 | 12.99 / 12.55 | 0.78 / 0.75 |
| | C | no / one effect, as Nice to have | 2 / 2 | 1 / 0 | 18.6 / 17.0 | 20.70 / 16.65 | 1.37 / 1.21 |
| `cross`, 134 files | A | 0 of 2 / 0 of 2 | 2 / 1 | 0 / 0 | 9.0 / 9.1 | 2.88 / 3.09 | 0.19 / 0.19 |
| | B | 0 of 2 / 0 of 2 | 1 / 5 | 0 / 0 | 24.3 / 24.3 | 7.18 / 8.98 | 0.50 / 0.60 |
| | C | 0 of 2 / 0 of 2 | 3 / 2 | 0 / 0 | 20.0 / 14.9 | 15.62 / 12.67 | 1.14 / 0.97 |
| `risk`, 10 files | A | yes / no | 5 / 4 | 0 / 0 | 4.0 / 2.3 | 1.42 / 0.84 | 0.11 / 0.08 |
| | B | yes / yes | 4 / 4 | 0 / 0 | 6.3 / 5.6 | 2.57 / 2.58 | 0.24 / 0.24 |
| | C | yes / yes | 5 / 6 | 0 / 0 | 6.5 / 6.6 | 3.60 / 3.69 | 0.34 / 0.35 |
| `loop`, round 2 | A | none known | 1 / 1 | 0 / 0 | 2.7 / 3.9 | 0.86 / 1.06 | 0.09 / 0.10 |
| | B | none known | 1 / 3 | 0 / 0 | 2.3 / 2.9 | 1.12 / 1.22 | 0.12 / 0.13 |
| | C | none known | 2 / 3 | 0 / 0 | 2.9 / 4.0 | 1.56 / 1.95 | 0.17 / 0.20 |

Distinct confirmed problems found by at least one of the two repeats:

| Case | A | B | C |
| --- | ---: | ---: | ---: |
| `mech` | 1 | 2 | 4, one a partial known defect |
| `cross` | 2 | 5 | 3 |
| `risk` | 5 | 4 | 7 |
| `loop` | 1 | 3 | 3 |

Cost against A, summed over both repeats:

| Case | B / A cost | C / A cost | B / A uncached tokens | C / A uncached tokens | B / A wall time | C / A wall time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `mech` | 2.8 | 4.1 | 2.9 | 4.9 | 2.2 | 2.0 |
| `cross` | 2.7 | 4.7 | 2.9 | 5.6 | 2.7 | 1.9 |
| `risk` | 2.3 | 3.2 | 2.6 | 3.8 | 1.9 | 2.1 |
| `loop` | 1.2 | 1.8 | 1.3 | 2.0 | 0.8 | 1.0 |

Minutes run from launch to exit and include the coordinator's validation. The split variants run their subagents in parallel, so these are elapsed times, not summed subagent time. Four runs shared the machine and the account at once, so timings carry contention. Cost is the CLI's reported API-equivalent price; uncached tokens are input, cache writes and output. Per-run numbers are in [results.json](results.json).

## What each variant found

`mech` (Ruby 3.4 and official Standard, 7,458 behavior lines). The known defect, a migration guard that skips an index left invalid by an interrupted build and leaves the index behind on rollback, was found once: C-2 reported the rollback effect as Nice to have and missed the invalid-index effect. Every A and B run read past that line, and A-1 and B-1 named it as checked and fine. C found the most other problems: a frozen Bundler setting that the development image now inherits, plus a dead role check and stale version comments that A and B also found. C-1 also reported a false Must fix: it claimed `nil&.refunds.to_a` returns `nil`, while Ruby 3.4 returns `[]`. A-1 reported a false Should fix: that Psych 5 rejects Symbol keys, while Psych 5's `load` permits `Symbol` by default. C-2's coordinator caught and dropped the same false crash claim from one of its reviewers.

`cross` (Rails 7.2, 697 behavior lines across jobs, storage, config, specs). No run found either known defect. Both sit in unchanged code that the upgrade broke: a pinned gem version and a removed Active Storage API. The pull request records that CI, not review, exposed them. The specialists found more of the rest. A development-only `preview_path` setting removed in Rails 7.2, which a later pull request (#2103) fixed, came from B in 2 of 2 runs and C in 1 of 2, but no A run. A blank development secret that now wins over the fallback came from B once and C twice. A found two minor findings: stale docs and a redundant branch.

`risk` (fixed table tip, 325 behavior lines, money). The known defect lies outside the diff: an unchanged payment service still capped the charge by the session's percent tip. B and C found it in both runs, A in one. Every run also found the second real defect, which the pull request fixed in a later commit: the client never sent the new field. C-2 alone found the same old bug in another client screen, which a later pull request (#2125) fixed.

`loop` (round 2 after the fix, one file). Every run confirmed the fix and reported a comment that breaks the global comment rule. In A, the coordinator found that comment, not its reviewer, which had no access to the global rules. B-2 and C-2 also found that the fix's new check can never fail, because every caller already enforces it. No A run reported that.

## Checking the findings

Every finding was checked against the code at the reviewed head. Where the repository later fixed the same code, that fix counts as confirmation. Two Ruby claims were run on Ruby 3.4.9 and Psych 5.5.0, and both were refuted. A finding that depends on framework behavior nobody could read or run here is plausible, not confirmed. Plausible findings are not counted: product images replaced instead of appended (A, B), a landing-page update that removes and adds images (B, C), development ignoring `SECRET_KEY_BASE` (B), and staging tuning shipped ahead of its setting (B). Judgment calls are not counted either, such as a removal grouped into a lint commit.

The checking was done by a session on the same model as the reviewers, and it was not blind to the variant.

## Decision

The pre-registered rule changes the default only if a split finds a known defect that A misses in both repeats, or cuts wall time by a third with no loss of findings, and costs under twice A's uncached tokens. B and C cost 2.6 to 5.6 times A's uncached tokens on every case but the loop round, and they never cut wall time. C's one partial catch of the `mech` defect does not clear the cost bar. On the loop round, where the cost bar holds (1.3 and 2.0 times), no variant found a known defect, because the case had none.

The evidence for specific workflows:

- **One reviewer (A)** stays the default for every size. A domain split does not make the review of a large diff faster; it doubles the time.
- **Two specialists (B)** found more on the cross-domain upgrade and caught the payment defect in both runs. That is the strongest case for paying about 2.5 times the cost. It is still a choice the user makes, not a default.
- **The adaptive domain split (C)** cost the most and found the most on `mech` and `risk`. It also gave the only false Must fix. It does not earn a place over B.
- **Large dependency upgrades:** no variant found the defects that CI found. On these changes, the suite is the review that catches gem incompatibilities.

Overlap: every variant's coordinator validated each finding itself. Duplicates across reviewers were merged in every split report, and no report numbered the same problem twice. The two disagreements that came up, a claimed crash and a claimed dead check, were settled by reading or running the code, not by counting reviewers.

## Limits

- Two repeats per cell, one private repository, one model. Codex ran out of quota, so the runs do not repeat #53's model.
- The global rules reached the session through `--append-system-prompt`. Subagents saw them only when the coordinator quoted them in the brief, which works against B and C's instructions reviewers. In real use, Claude Code subagents load `CLAUDE.md` themselves.
- Some reviewers read installed gem sources outside the repository, which the instructions forbade and the sandbox allowed. That was open to every variant.
- The first Claude batch (24 runs) was discarded because its command allowlist left most subagents without git; see [Amendments](PLAN.md#amendments). Its cost is not in the totals above.

## Reproduce

Point `--source` at a compitienda checkout with `refs/bench/{mech,cross,risk,loop}` set to the reviewed heads in [PLAN.md](PLAN.md#cases), then:

```bash
work=$(mktemp -d)
uv run --python 3.14 python -I experiments/review-changes-73/run.py "$work" --source ~/Projects/compitienda
uv run --python 3.14 python -I experiments/review-changes-73/run.py "$work" --summarize
```

The full reports quote private code, so they stay out of this repository.
