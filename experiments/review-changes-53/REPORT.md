# One review session versus two reviewers

Keep the candidate's one-session workflow. In this comparison, two reviewers added no confirmed finding and omitted two that the one-session review reported. They used 4.31 times the total tokens. This is one paired run per case, not evidence that one session always wins.

This experiment answers [issue #53](https://github.com/salasebas/skills/issues/53) on [PR #52](https://github.com/salasebas/skills/pull/52). It ran on 2026-10-29 against candidate `0f44728f67333468fa1dcba2b7e54b928c260825`, using Codex CLI 0.165.0 and `gpt-6.1-sol` with `high` effort throughout.

## Results

Both variants found both known Mastodon defects. A reported all five clear planted violations; B reported four. A also found a cross-API featured-tag regression that B omitted. All other additional findings agreed.

| Case | A confirmed findings | B confirmed findings | A minutes | B minutes | A total tokens | B total tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Mastodon #34489 | 2 | 1 | 2.29 | 2.39 | 292,150 | 1,298,688 |
| Mastodon #27511 | 5 | 5 | 2.67 | 2.64 | 570,899 | 2,023,754 |
| Planted violations | 6 | 5 | 1.01 | 1.49 | 103,735 | 659,246 |
| Small, better-auth-rb #135 | 0 | 0 | 0.57 | 1.08 | 124,065 | 636,610 |
| Medium, ports #67 | 2 | 2 | 1.63 | 2.13 | 320,775 | 1,461,645 |
| Total | 15 | 13 | 8.18 | 9.72 | 1,411,624 | 6,079,943 |

Counts represent distinct confirmed problems, not numbered report items. For example, planted-A groups the wrapper, unrelated feature, and narrative comment into one item. The synthetic size finding is excluded from confirmed counts. The two missed problems are observations from these runs, not an estimate of recall on other changes.

Times cover each review from CLI launch to exit, including its coordinator and children. The total is the sum of review durations, not elapsed experiment time. Two harness batches ran concurrently, with up to eight root sessions at once; timings can reflect service contention.

Token totals sum each session's last cumulative usage once, including all B children. Input includes cache hits; output already includes reasoning tokens. Reasoning is not added again.

| Token measure | A | B | B / A |
| --- | ---: | ---: | ---: |
| Input | 1,392,516 | 6,037,266 | 4.34 |
| Cached input, included above | 1,115,776 | 5,406,848 | 4.85 |
| Output, including reasoning | 19,108 | 42,677 | 2.23 |
| Input excluding cache hits, plus output | 295,848 | 673,095 | 2.28 |

These are usage counts, not a price estimate. Cache hit rates differ, so the 4.31 total-token ratio does not imply a 4.31 billing ratio. Setup, infrastructure pilots, and the independent validators are excluded from the paired-run measurements.

## What was held constant

A uses the candidate skill unchanged and follows `bugs.md`, then `instructions.md` in one session. B changes only Workflow step 3 to start two fresh-context reviewers in parallel, one per reference, then leaves the coordinator's validation and reporting steps unchanged. B's replacement also fixes the requested model and effort and prevents recursive delegation.

Every root has its own HOME and detached worktree. The HOME contains the pinned global rules, the skill variant, and authentication needed by the harness. Plugins, apps, memories, and web search are disabled. Codex also exposes four built-in system-skill descriptions equally to both variants; they were not used. Existing project `AGENTS.md` and `CLAUDE.md` files remain available in each checkout.

The prompt is identical apart from the base hash:

> Review the changes in HEAD against &lt;base&gt;. Use the review-changes skill.

Both variants receive the same developer instruction restricting reads to the current checkout, the skill, and loaded instructions. Commands are limited to read-only Git operations, `rg`, `fd`, `ls`, `head`, `cat`, `wc`, and `sed -n`. Tests, interpreters, network commands, edits, other runs, answer files, and PR discussions are excluded. The filesystem and command network are sandboxed; the command allowlist and read scope are instructions, verified afterwards rather than enforced as a separate shell parser.

The transcript audit checked all 415 execution commands. They use only the allowed read operations; no project code, test, web request, edit, answer file, or other run was accessed. All ten worktrees remained clean. All twenty sessions record the requested model and `high` effort. Each A has one session and no spawn calls. Each B has exactly two children, both spawned with `fork_turns: "none"`, overlapping lifetimes, and only its assigned reviewer reference loaded by each child. The coordinator re-reads code to validate their findings.

The credential-free [metrics](metrics.json) retain session IDs, parentage, model, effort, timestamps, cumulative usage, spawn configuration, command traces, and hashes of the original rollout files. The [reports](reports/) preserve final answers; temporary source links were converted to pinned GitHub links or local fixture links. Credentials and full rollout metadata are not included.

## Cases and validation

A separate fresh-context validator checked every reported problem against the pinned code. The main session then checked the evidence. These checks used code and primary sources; the Mastodon and Ports applications were not built or run. No final finding was refuted, but A's file-size finding remains conditional and is excluded from confirmed counts.

### The removed scope, Mastodon #34489

Base `d4944a24676e9b9e9fe419cb7661d9b2c0c9d77f`, head `ba536ea867afa7f281648b0dd8d63e09d3d6cf54`. The diff has 15 files, +195/-50.

Both [A](reports/scope-A.md) and [B](reports/scope-B.md) found the known defect. The head removes `FeaturedTag.by_name`, while [the ActivityPub removal handler](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/lib/activitypub/activity/remove.rb#L34) still calls it. [Issue #34886](https://github.com/mastodon/mastodon/issues/34886) records the resulting `NoMethodError`; [repair #34887](https://github.com/mastodon/mastodon/pull/34887) restores the scope and adds coverage.

A's additional finding is confirmed. [The service](https://github.com/mastodon/mastodon/blob/ba536ea867afa7f281648b0dd8d63e09d3d6cf54/app/services/create_featured_tag_service.rb#L11) looks up `Tag` inputs by association and string inputs by `name`. Creating through `/api/v1/tags/foo/feature` leaves the nullable featured-tag name unset. A later legacy create with `name=foo` misses that row, resolves the same tag, and fails account/tag uniqueness with HTTP 422. No model callback populates the name on the first path. B does not report this problem.

### The ownerless lookup, Mastodon #27511

Base `3211e960ac793b1b9431a7eea40b385272f1a2a6`, head `89d3c22a40eb2c09b353470175f057f1a3aa3553`. The diff has 39 files. The supplied base is the merge-base, even though GitHub's current PR base SHA differs.

Both [A](reports/ownership-A.md) and [B](reports/ownership-B.md) correctly limit the known security finding to metadata. [The controller](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/controllers/severed_relationships_controller.rb#L31) loads any event ID, then puts its target and date in download filenames. CSV rows already filter by `local_account: current_account`, so another account's relationship-row disclosure is not established at this head. [The repair](https://github.com/mastodon/mastodon/commit/0f79e2918858415835b61a88090147a27dd319f0) adds the owner scope and foreign-owner 404 tests; [the official advisory](https://github.com/mastodon/mastodon/security/advisories/GHSA-ww85-x9cp-5v24) records the missing ownership validation.

The four additional findings are confirmed in both reports:

- [The migration](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/db/migrate/20240320140159_create_account_relationship_severance_events.rb#L6) uniquely indexes each foreign key separately. A second recipient of one event, or an account's second event, violates those indexes.
- [The notification association](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/models/notification.rb#L92) loads `RelationshipSeveranceEvent` by `activity_id`, while the worker receives an `AccountRelationshipSeveranceEvent` ID. Independent sequences can produce missing or unrelated notification metadata.
- [The history view](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/views/severed_relationships/index.html.haml#L20) calls `purged?`. The account-event model delegates only `purged`; its actual table has no `purged` column to generate the predicate. A populated page raises.
- [The serializer](https://github.com/mastodon/mastodon/blob/89d3c22a40eb2c09b353470175f057f1a3aa3553/app/serializers/rest/account_relationship_severance_event_serializer.rb#L4) omits the stored `relationships_count`, while the card reads that field with default zero. Correcting the association still leaves this independent defect.

### Planted instructions

The runner creates the fixture and [records its expected violations](planted-truth.json) before starting any review. The [requirements](fixture/requirements.md) predate the bad change. [A](reports/planted-A.md) and [B](reports/planted-B.md) receive neither the truth file nor hints about expected answers.

| Recorded violation | A final report | B final report | Validation |
| --- | --- | --- | --- |
| Narrative return comment | Found | Missed | `orders.py:13` fits no permitted comment category |
| Pass-through wrapper | Found | Found | `shipping_cost` only returns `shipping(mode)` |
| Silent default | Found | Found | Unknown modes return 7 instead of raising |
| Unhandled enum value | Found | Found | `dashboard(Status.CANCELLED)` raises |
| Test expectation edited to pass | Found | Found | Price and assertion change 5 to 7 against requirements |
| File grows past about 1,000 lines | Reported | Considered by child, omitted from final | Conditional; excluded from hard recall and confirmed counts |

Both also report the unrelated `gift_wrap_fee` addition, a confirmed scope violation. It was not one of the five clear pre-recorded targets. This makes six distinct confirmed problems for A and five for B.

`fixture/fees.py` is generated experiment input, growing from 990 to 1,008 lines. The candidate rule expressly exempts generated files and cohesive units. The fixture does not identify an exception to its reviewers, but its construction prevents treating this as an unequivocal failure. B's instructions child explicitly discusses the size concern and drops it as a blocker; its final report also omits the narrative comment, which neither child reported.

Independent runtime checks of the fixture produced:

```text
HEAD^ standard price equals required 5: True
HEAD^ unknown mode rejected: True
HEAD standard price equals required 5: False
HEAD unknown mode rejected: False
HEAD cancelled appears in dashboard: False
Current weakened test suite: Ran 1 test ... OK
```

### Real small and medium changes

The small case is [better-auth-rb #135](https://github.com/salasebas/better-auth-rb/pull/135), base `f8721cec3bd9ed55cb68d10659f31c29173d5f68`, head `61fa967ebc5d35ad30241bc5c707d2321f8add8f`, two files, +58/-1. Both [A](reports/small-A.md) and [B](reports/small-B.md) return no findings. That agreement is not proof that the change has no defects. Both disclose that runtime checks and the absent upstream source checkout were not checked.

The medium case is [ports #67](https://github.com/salasebas/ports/pull/67), base `bbb785244600b719cb576a219477979b2358e2c2`, head `31b234c30d9aec825f09936bdd164f86fb12abc9`, seven files, +299/-131. Both [A](reports/medium-A.md) and [B](reports/medium-B.md) report the same two confirmed problems:

- [The new shutdown heuristic](https://github.com/salasebas/ports/blob/31b234c30d9aec825f09936bdd164f86fb12abc9/src-tauri/src/ports/control.rs#L277) admits new orphans based on executable, shared process group, session, and user. An unrelated same-interpreter worker whose parent exits during shutdown meets those conditions without being a descendant. The following loop signals every admitted target.
- [The Linux socket scan](https://github.com/salasebas/ports/blob/31b234c30d9aec825f09936bdd164f86fb12abc9/src-tauri/src/ports/sockets.rs#L44) treats the host's `bindv6only` default as every socket's actual setting. A dual-stack socket overriding a default of 1 loses its valid IPv4 LAN link. [The kernel documentation](https://docs.kernel.org/networking/ip-sysctl.html#proc-sys-net-ipv6-variables) defines this sysctl as the default socket-option value, not a per-socket observation.

## Limits and decision

The stopped pilots are not data points. Nested sandbox permissions initially blocked shell reads; partial-clone objects then blocked some diffs. The ten scored runs started in new directories after fixing socket access and loading the diff objects. All findings were validated statically; only the small synthetic fixture received runtime checks.

The requested model replaces the issue's earlier OpenCode free-model suggestion. The shell allowlist is instructed and audited, not enforced by a custom command broker. Known public regressions can be familiar to the model, and neither model familiarity nor server-side cache state is controlled. There is one run per variant per case, no randomized repeat study, and the ambiguous file-size probe does not establish strict size-rule recall. The experiment does not exercise `loop`, second-pass anchoring, or a session reviewing code it wrote.

For this candidate, the measured benefit of two reviewers does not justify changing the default. Keep Workflow step 3 sequential and keep fresh review of self-authored changes and later loop passes as separate rules. [Reproduction instructions](REPRODUCE.md) retain the pinned setup for a larger comparison if later evidence warrants one.
