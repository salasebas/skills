---
name: review-changes
description: "Use when the user asks to review a change: uncommitted work, a commit, a branch, or a PR. Checks for bugs and for breaks of AGENTS.md and CLAUDE.md, and validates each finding. With `loop`, a fresh reviewer reviews in rounds while this session fixes."
---

# Review Changes

Review a change like the senior developer who will be paged when it breaks.

**The approval standard:** Approve a change when it definitely improves overall code health, even if it isn't perfect. Don't block a change because it isn't exactly how you would have written it.

## Reviewer

Use a reviewer when this session wrote the change, and in every round of [Loop](#loop). Start one new subagent with fresh context, through the environment's orchestrator when it has one, else the harness's own subagents:

- T3 Code: `delegate_task`, role `review`.
- Codex: `spawn_agent` with `fork_turns: "none"`.

Use the model the user names; if no route runs it, report the blocker. Unnamed: another vendor's model, else another model, else the session's.

State intent and out-of-scope in 1-2 sentences, run covering checks, and note missing or failing ones in the brief (the reviewer gets no history):

```
Review only. Do not edit, commit, push, comment on PRs, or start subagents. Run only read-only git and gh commands.
Repo: <abs path> Base: <sha> Intent: <intent> Out of scope: <scope> Checks: <results>
See: git diff <base> [-- <paths>]; git status --short (read untracked).
Follow the review-changes skill's Workflow through validation.
Reply:
VERDICT: APPROVE or CHANGES
S1 [Must fix|Should fix|Nice to have] <file>:<line> <claim>. Fix: <suggestion> (stable ids)
```

Do not edit scoped files while the review runs. Wait for the notice; do not poll or start a second reviewer. Timeout, error, or no reply is not approval. Check each finding yourself, then report.

Any other change, review here.

## Workflow

1. Determine the review scope from the user request, PR, current branch, or relevant changed files. See [Scope](#scope).
2. Gather the diff and any file/context excerpts needed to evaluate the change without guessing, plus the original requirements and the project instructions.
3. Review for [Bugs](#bugs) and [Instructions](#instructions).
4. Record findings with file references and evidence, grouped as Must fix, Should fix or Nice to have as defined under [Report](#report). Zero findings is an acceptable outcome.
5. Deduplicate the findings. When several findings are one class of bug, report it once and list every location, so the fix covers all of them.
6. [Validate](#validate) every finding.
7. [Report](#report).

The review changes no code and runs only read-only git and gh commands. [Loop](#loop) is the one mode that edits.

## Scope

Review what the user names: uncommitted or staged changes, a branch, a PR link, or files. Nothing named: the uncommitted changes, or the last commit if there are none.

- **Staged:** `git diff --cached`
- **Uncommitted:** `git diff HEAD`, plus the untracked files from `git status --short`
- **A commit:** `git show <sha>`
- **A branch, or a diff against a base:** `git diff <base>...HEAD` (three-dot, so the comparison is against the merge-base)
- **A PR:** `gh pr diff <number>`, with `gh pr view <number>` for the description

Read the surrounding code at the revision under review. When that revision is checked out, read the files on disk. Otherwise stay on the current branch and read from the revision: `git show <ref>:<path>` and `git grep <pattern> <ref>`, after `git fetch origin pull/<number>/head` for a PR.

Confirm the diff is non-empty before reviewing.

## Bugs

Audit the change extremely thoroughly for bugs, changes that break existing features/functionality, and security vulnerabilities.

Focus on changes in the diff. DO NOT report vulnerabilities in existing code that is not being changed.

Often simple code changes in one place have subtle interactions that break functionality elsewhere. You MUST be extremely thorough in tracing through possible side effects of the changes.

Correctness, edge cases and error paths, security, performance, and the tests: do they exercise behavior, and would they fail if the change regressed?

Flag code, tests, or guards the intent does not need. Do not flag issues that a linter will catch.

When the change touches user input, authentication, permissions, secrets, or file or command execution, also follow [`references/security.md`](references/security.md).

### Enum & Value Completeness
When the diff introduces a new enum value, status string, tier name, or type constant, or loosens what an input accepts (a new MIME type, extension or flag, or a widened validator/parser/guard):
- **Trace it through every consumer.** Read (don't just grep — READ) each file that switches on, filters by, or displays that value. If any consumer doesn't handle the new value, flag it.
- **Loosened acceptance breaks unchanged consumers.** Grep every consumer of the same field and confirm each handles the newly accepted shape; the broken code is usually outside the diff.

### Breaking Devex Guidelines
It can be easy to break developers' ability to run / build the code locally. Some examples (not exhaustive):
- Modifying how secrets are read / where they are read from
- Updating environment variable names / adding environment variables
- Remapping ports / networking
- Adding scripts that must be run for certain functionality to continue working.

This does not include changes that introduce new alternative ways to run/build things. Adding dependencies with package managers does not count as a devex breaking change, unless it requires the user to do some very new thing that is not part of their normal development workflow.

### Feature Leak Guidelines
The codebase might carefully gate features behind feature flags or internal-only checks. You MUST NOT allow any features that are meant to be behind a feature gate leak.

### Gate Integrity
A gate is anything that would have made this change fail: a test, an assertion, a threshold, a timeout, a lint rule, a type check, a CI job, a snapshot.
- Read every hunk in the diff where a test is removed or disabled, a snapshot changed without its owning test, a placeholder is committed, the code sniffs the environment, a suppression pragma is added, a gate is bypassed, a gate value is relaxed, or an exception is swallowed. Ask the one question: **does this relaxation silence the failure it was added for, or is it justified by a measurement or decision visible in this diff?**
- A hunk with no gate semantics, or one justified by a visible measurement or decision, is not a finding.
- Read also for a mock, fixture or static read presented as the proof a claim needs, and for a test that cannot fail: asserts its own setup, mirrors the implementation, or has no negative.

### Intended Breakage Guidelines
If you identify a high risk finding, but the intent of the change is to introduce that finding – e.g. break some functionality, remove a feature flag, remove a safeguard – AND the scope of the change is well constrained, you SHOULD NOT waste the author's time by reporting the issue to them. However, if you believe it is likely that they are not aware of the full implications of their change, or you are worried that the change is actually malicious, you should still report the finding.

### Over-reporting Guidelines
If you report issues as Must fix when they are not in fact meaningful issues, devs will lose trust in you and stop listening to you over time.

### Before you report
- NEVER present issues with unfinished research. E.g. Never say something like, "The client has issue X, but if handled in the backend then this is ok." if you have access to the backend code and can check for yourself.
- IF the change is a PR/MR and you have Must fix or Should fix findings, check its discussion using gh/glab cli for comments from other reviewers. If they found issues you missed, evaluate them to determine if they are valid and include them in your report. Flag the findings in your report that came from the discussion.
- You MUST wait to check the PR/MR discussion until AFTER you have performed your audit. This way you have fresh eyes while you review.

## Instructions

Audit the change for compliance with the instructions loaded for this project: the user's global instructions, and the `AGENTS.md` or `CLAUDE.md` files that share a file path with the changed file or its parents. Flag clear, unambiguous violations where you can quote the exact rule being broken. Do not flag issues mentioned in the instructions but explicitly silenced in the code (e.g., via a lint ignore comment).

When you flag a structural problem, propose the move — not just the problem. Prefer the remedy that removes moving pieces over one that spreads the same complexity around.

Treat a broken rule as a presumptive blocker unless the author can justify it clearly.

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

**Lead with what matters.** Order findings by leverage: correctness and security first, then structural regressions and missed simplifications, then everything else. Don't bury a real issue under cosmetic nits — a few high-conviction comments beat a long list.

- **Don't soften real issues.** "This might be a minor concern" when it's a bug that will hit production is dishonest.
- **Quantify problems when possible.** "This N+1 query will add ~50ms per item in the list" is better than "this could be slow."
- **Accept override gracefully.** If the author has full context and disagrees, defer to their judgment.

### Post to GitHub

Only when the user asks to post the review on the PR, and from the session, not the reviewer. After validation, post one review with a comment on the line of each finding:

```bash
gh api repos/<owner>/<repo>/pulls/<number>/reviews --input review.json
```

`review.json` holds `commit_id` (the PR's head SHA), `event` set to `COMMENT`, `body`, and `comments`, each with `path`, `line`, `side` set to `RIGHT`, and `body`.

- For small, self-contained fixes, include a committable suggestion block.
- Never post a committable suggestion UNLESS committing the suggestion fixes the issue entirely.
- Only post ONE comment per unique issue.

## Loop

Runs when the user passes `loop` with the request: follow [`references/loop.md`](references/loop.md). Without it, the review is a single pass.
