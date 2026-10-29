# Second round: one session versus two reviewers

The second round ends at 15 confirmed problems for each variant. They are different sets: A alone reports the cross-endpoint hashtag bug and the narrative comment; B alone reports two additional instruction violations in Mastodon's severance feature. B uses 4.30 times the total tokens, or 2.31 times with cache-hit input excluded. The cheaper sequential default remains reasonable; these two rounds do not establish a general recall winner.

This is a fresh repetition of the [first round](REPORT.md), requested after the first results. All ten first-round reports and their metrics remain unchanged.

## Setup and audit

The five cases, base/head revisions, prompts, candidate skill, and runner are unchanged. The candidate is `0f44728f67333468fa1dcba2b7e54b928c260825`; the runner comes from `613f95738d9b68296fe3c6770a92be01f429b0d3`. The [manifest](round2/manifest.json) records its SHA-256 and the fixture hashes. The fixture's five files match round one byte for byte, including its original two commits and pre-recorded requirements.

Each case receives one new A run and one new B run. A is a standalone `codex exec` session that follows both references sequentially, without subagents. B is a standalone coordinator that starts exactly two fresh-context reviewers in parallel, one for `bugs.md` and one for `instructions.md`, then validates their findings. All roots and children use `gpt-6.1-sol` at `high` effort through Codex CLI 0.165.0.

Every root has a new HOME and detached worktree. The same two harness batches allow up to eight root sessions at once, with four per batch. These are ten new runs containing twenty new model sessions, not resumed sessions. No round-two run was retried or excluded. Ordinary failed searches for guessed file names remain part of their original reviews; they are not infrastructure failures.

The audit confirms all twenty session hashes, requested model/effort, clean worktrees, fresh-context spawn configuration, overlapping child lifetimes, and one assigned reference per child. All 409 execution commands use the allowed read operations. No review accessed an answer file, another run, project execution, or the network. As in round one, filesystem/network isolation is enforced by Codex's sandbox; read scope and the command allowlist are instructed and audited.

The [metrics](round2/metrics.json) include session and command evidence plus a finding-ID map to each numbered final report. Credentials and full account metadata are excluded. [Reproduction](REPRODUCE.md) uses the unchanged runner with a new work directory.

## Measured results

| Case | A confirmed | B confirmed | A minutes | B minutes | A total tokens | B total tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Mastodon #34489 | 2 | 1 | 2.08 | 2.48 | 267,753 | 1,284,178 |
| Mastodon #27511 | 5 | 7 | 2.64 | 3.17 | 524,096 | 1,913,929 |
| Planted violations | 6 | 5 | 1.09 | 1.91 | 106,064 | 613,346 |
| Small, better-auth-rb #135 | 0 | 0 | 0.69 | 1.20 | 139,431 | 823,526 |
| Medium, ports #67 | 2 | 2 | 1.35 | 2.00 | 299,541 | 1,110,856 |
| Total | 15 | 15 | 7.85 | 10.75 | 1,336,885 | 5,745,835 |

Counts represent distinct confirmed problems within each case, not numbered report items. Both variants' synthetic size claims remain conditional and are excluded. Times cover each whole review, including the B coordinator and children; totals sum durations rather than measure elapsed experiment time. Shared service contention can affect them.

| Token measure | A | B |
| --- | ---: | ---: |
| Input | 1,319,726 | 5,700,469 |
| Cached input, already included above | 1,043,072 | 5,066,624 |
| Output, including reasoning | 17,159 | 45,366 |
| Total | 1,336,885 | 5,745,835 |
| Input excluding cache hits, plus output | 293,813 | 679,211 |

Each session contributes its last cumulative usage once. Output already includes reasoning. These counts do not estimate billed cost; cache-hit rates and pricing are not controlled.

## Finding validation

A fresh-context validator, not given the first-round outcomes, checked every final finding against the pinned code. The main session independently checked the evidence, including B's two new instruction findings. Real-application validation remains static; no Mastodon or Ports runtime tests were run. No fully refuted finding was reported. The file-size claim remains conditional.

| Case | A report | B report | Confirmed finding IDs |
| --- | --- | --- | --- |
| Removed scope | [scope-A](round2/reports/scope-A.md) | [scope-B](round2/reports/scope-B.md) | A: S1, S2. B: S1 |
| Ownership | [ownership-A](round2/reports/ownership-A.md) | [ownership-B](round2/reports/ownership-B.md) | A: O1-O5. B: O1-O7 |
| Planted | [planted-A](round2/reports/planted-A.md) | [planted-B](round2/reports/planted-B.md) | A: P1-P6. B: P1-P5 |
| Small PR | [small-A](round2/reports/small-A.md) | [small-B](round2/reports/small-B.md) | None reported |
| Medium PR | [medium-A](round2/reports/medium-A.md) | [medium-B](round2/reports/medium-B.md) | Both: M1, M2 |

The [first report's code validation](REPORT.md#cases-and-validation) establishes the same pinned mechanisms for S1-S2, O1-O5, M1-M2, and the fixture. The second-round validator checked those mechanisms again rather than treating earlier agreement as evidence:

- S1 is the deleted `FeaturedTag.by_name` scope with its surviving ActivityPub caller. S2 is the new Tag-based API creating a nullable-name record that the string-based API misses, producing a duplicate-account/tag 422. Both variants find S1; only A finds S2.
- O1 is the ownerless event lookup leaking filename metadata. Both reports correctly acknowledge that CSV rows already filter by the current account. O2-O5 are individually unique foreign keys, the wrong notification association model, the undelegated `purged?` predicate, and the missing serialized relationship count. Both variants find all five.
- M1 is executable matching admitting an unrelated orphan to shutdown signals. M2 is using the host IPv6 default as a live socket setting. Both variants find both.
- P1-P3 are the wrong price with its changed test expectation, the silent unknown-mode fallback, and the unhandled cancelled status. P4 is the pass-through wrapper, P5 the unrelated gift-wrap feature, and P6 the narrative comment. Both variants find P1-P5; only A reports P6.

O6 and O7 are the two additional B findings. They are instruction-based structural findings, not independently demonstrated runtime bugs:

- **O6, shared deletion gains a domain-block-specific branch.** [DeleteAccountService calls the new recorder](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/services/delete_account_service.rb#L90), whose [guard](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/services/delete_account_service.rb#L274) is `return if relationship_severance_event.nil?`. [BlockDomainService](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/services/block_domain_service.rb#L43) is the only caller passing that option. The loaded rule explicitly says to keep feature checks out of shared paths. Moving the two recording loops immediately before that caller's deletion removes the option and guard from shared deletion without losing the recording step.
- **O7, following CSV encoding gains a second owner.** [The new controller](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/controllers/severed_relationships_controller.rb#L35) duplicates the headers and row encoding already in [Export](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/models/export.rb#L32), and duplicates its account-address helper. The loaded rule requires reusing existing helpers. Allowing Export to accept the scoped relationship collection retains one CSV-format owner while the controller handles HTTP delivery.

The narrative comment remains a clear miss in B. Both variants find four of the other pre-recorded instruction targets, so clear planted-target recall is A 5/5 and B 4/5. Both also find both known Mastodon targets. P7, the 990-to-1,008-line file, is conditional because the rule exempts generated or cohesive files. A reports P7 separately; B groups it with gift wrapping in planted-B #4. Only the confirmed gift-wrap part contributes to B's count.

## What changed between rounds

| Measure | Round 1 A | Round 1 B | Round 2 A | Round 2 B |
| --- | ---: | ---: | ---: | ---: |
| Confirmed problems per round | 15 | 13 | 15 | 15 |
| Known Mastodon targets found | 2/2 | 2/2 | 2/2 | 2/2 |
| Clear planted targets found | 5/5 | 4/5 | 5/5 | 4/5 |
| Total tokens | 1,411,624 | 6,079,943 | 1,336,885 | 5,745,835 |
| Tokens excluding cache-hit input | 295,848 | 673,095 | 293,813 | 679,211 |

B's two additional instruction findings change its total from 13 to 15; its original misses remain. A reports the same fifteen confirmed problems in both rounds. Across both rounds, each variant discovers fifteen distinct problems at least once, with thirteen shared and two unique to each variant. The combined union is seventeen. Repeated reports of the same problem are not additional distinct discoveries.

The two-round token sums are 2,748,509 for A and 11,825,778 for B, a 4.30 ratio. With cache-hit input excluded they are 589,661 and 1,352,306, a 2.29 ratio. The sample now contains two paired runs per case, still only five cases. It supports a consistent overhead difference and demonstrates variation in instruction findings; it does not establish a universal coverage advantage. The sequential workflow remains unchanged.
