---
name: review-changes
description: Review a change — staged or uncommitted work, a commit, a branch diff, or a PR — along two lenses (bugs, structure), with findings validated before they are reported. Use for "review this", "code review", "review my PR". `loop` fixes and re-reviews until no findings remain.
---

# Review Changes

Review a change like the senior developer who will be paged when it breaks.

**The approval standard:** Approve a change when it definitely improves overall code health, even if it isn't perfect. Perfect code doesn't exist — the goal is continuous improvement. Don't block a change because it isn't exactly how you would have written it. If it improves the codebase and follows the project's conventions, approve it.

## Workflow

1. Determine the review scope from the user request, PR, current branch, or relevant changed files. See [Scope](#scope).
2. Gather the diff and any file/context excerpts needed to evaluate the change without guessing, plus the original requirements and the project instructions.
3. Review the change, following each reference file in turn:
   - [`references/bugs.md`](references/bugs.md): bugs, breakages, security, devex regressions, feature-flag leaks, and other branch-audit risks.
   - [`references/structure.md`](references/structure.md): maintainability, structure, file-size growth, spaghetti, abstractions, and codebase-health risks.
4. Record findings with file references and evidence, grouped as Must fix, Should fix or Nice to have as defined under [Report](#report). Require a concrete failure scenario, location, impact, and evidence. Zero findings is an acceptable outcome.
5. Deduplicate the findings.
6. Validate every finding. See [Validate](#validate).
7. Report. See [Report](#report).

The review is read-only: it lists findings, changes no code. [Loop](#loop) is the one mode that edits.

## Scope

Review what the user names: uncommitted or staged changes, a branch, a PR link, or files. Nothing named: the uncommitted changes, or the last commit if there are none.

- **Staged:** `git diff --cached`
- **Uncommitted:** `git diff HEAD`, plus the untracked files from `git status --short`
- **A commit:** `git show <sha>`
- **A branch, or a diff against a base:** `git diff <base>...HEAD` (three-dot, so the comparison is against the merge-base)
- **A PR:** `gh pr diff <number>`, with `gh pr view <number>` for the description

Read the surrounding code at the revision under review. When that revision is checked out, read the files on disk. Otherwise stay on the current branch and read from the revision: `git show <ref>:<path>` and `git grep <pattern> <ref>`, after `git fetch origin pull/<number>/head` for a PR.

Confirm the diff is non-empty before reviewing.

## Validate

Treat each finding as a hypothesis to confirm or refute, not an instruction to modify code.

- Every finding needs a concrete case: "this input or situation leads to this wrong result". No case, no finding.
- For a structure finding, the concrete case is the exact code and the named restructuring that removes it.
- Re-read the lines and confirm: the caller exists, the value can really be empty, the code really is unused.
- **Quote the specific code line:** file:line and verbatim text. For a missing field, quote its class definition; for a nullable value, its initialization; for a race, both sides.
- For framework-generated symbols, read and quote their generating metaclass, descriptor, ORM Meta block, migration, decorator or schema. Missing literal names in the class body or grep results do not prove absence.
- **If you cannot quote the motivating line(s), the finding is unverified.**
- Propose the smallest fix that works. Prefer fixes that delete code. Never add layers, frameworks or config the problem does not need.
- No style taste, no "consider", no vague worries.

Validation is done when every finding is confirmed, refuted and dropped, or named under `Not checked`.

## Report

Very simple language: short sentences, everyday words. Explain a technical term the first time you use it. The reader may never have seen this code.

Start with `What this change does:` in two or three sentences.

Then the findings in three groups, skip empty groups:
- **Must fix:** bug, security, data loss, breaks at the expected load.
- **Should fix:** risky code without a test, real slowness, duplication, a function that mixes jobs, code that should not exist.
- **Nice to have:** small speed-ups, shorter forms.

Number findings across all groups, so the user can say "fix 2 and 5".
Every finding has all four parts, each one or two short sentences:

2. **Orders land on the wrong day** (`billing/close_day.py:L40-52`)
   - **What this is:** At midnight this job closes the day and bills all orders of that day.
   - **Problem:** It takes "today" from the server clock, which runs in UTC. An order placed
     at 00:30 in Berlin is billed on the day before.
   - **Fix:** Compute the day once in the shop's time zone:
     `datetime.now(ZoneInfo("Europe/Berlin")).date()`. One line, nothing else changes.
   - **If we skip it:** Late orders show the wrong date, and accounting fixes them by hand.

End with:
- `Verdict: Ship.` or `Verdict: fix 1 and 3 first.`
- `Not checked:` one line, if something mattered and you could not check it.

Nothing found: `What this change does:`, then `Looks good. Ship.` and one line
on what you checked.

**Lead with what matters.** Order findings by leverage: correctness and security first, then structural regressions and missed simplifications, then everything else. Don't bury a real issue under cosmetic nits — a few high-conviction comments beat a long list. If you have one structural problem and ten nits, the structural problem *is* the review.

### Honesty in Review

When reviewing code — whether written by you, another agent, or a human:

- **Don't rubber-stamp.** "LGTM" without evidence of review helps no one.
- **Don't soften real issues.** "This might be a minor concern" when it's a bug that will hit production is dishonest.
- **Quantify problems when possible.** "This N+1 query will add ~50ms per item in the list" is better than "this could be slow."
- **Push back on approaches with clear problems.** Sycophancy is a failure mode in reviews. If the implementation has issues, say so directly and propose alternatives.
- **Accept override gracefully.** If the author has full context and disagrees, defer to their judgment. Comment on code, not people — reframe personal critiques to focus on the code itself.

## Loop

Runs when the user passes `loop` with the request: follow [`references/loop.md`](references/loop.md). Without it, the review is a single pass.
