---
name: review-changes
description: "Use when the user asks to review a change: uncommitted work, a commit, a branch, or a PR. Checks for bugs and for breaks of AGENTS.md and CLAUDE.md, and validates each finding. With `loop`, a fresh reviewer reviews in rounds while this session fixes."
---

# Review Changes

Review a change like the senior developer who will be paged when it breaks.

**The approval standard:** Approve a change when it definitely improves overall code health, even if it isn't perfect. Don't block a change because it isn't exactly how you would have written it.

## Reviewer

When this session wrote the change, start one new subagent with fresh context, through the environment's orchestrator when it has one, else the harness's own subagents:

- T3 Code: `delegate_task`, role `review`.
- Codex: `spawn_agent` with `fork_turns: "none"`.

Use the model the user names; if no route runs it, report the blocker. Unnamed: another vendor's model, else another model, else the session's.

Brief (the reviewer gets no history):

```
Review only. Do not edit, commit, push, comment on PRs, or start subagents. Run only read-only git and gh commands.
Repo: <abs path> Base: <sha> Intent: <intent> Out of scope: <scope> Checks: <results>
See: git diff <base> [-- <paths>]; git status --short (read untracked).
Follow the review-changes skill's Workflow through validation.
Reply:
VERDICT: APPROVE or CHANGES
S1 [Must fix|Should fix|Nice to have] <file>:<line> <claim>. Fix: <suggestion> (stable ids)
```

Do not edit scoped files while the review runs. Timeout, error, or no reply is not approval. Check each finding yourself, then report.

Any other change, review here.

## Workflow

1. Determine the review scope. See [Scope](#scope).
2. Gather the diff, the surrounding code, the original requirements, and the project instructions.
3. Review for [Bugs](#bugs) and [Instructions](#instructions).
4. Record findings with file references and evidence, as Must fix, Should fix or Nice to have, defined under [Report](#report). Zero findings is an acceptable outcome.
5. When several findings are one class of bug, report it once and list every location, so the fix covers all of them.
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

Audit the code this change adds or modifies for bugs and security vulnerabilities. Read outside the diff to trace effects, but report nothing about code the change leaves alone.

- **Broken behavior:** correctness, edge cases, error paths, performance, and mismatch with the intent. Simple changes often break something in another module, so trace callers and side effects.
- **New values:** when the change adds an enum value, status, or type, or widens what an input accepts, read every consumer, allowlist, and branch that handles it, including outside the diff.
- **Security:** injection, broken authentication or authorization, and exposed secrets or personal data, with a concrete way to exploit it.
- **Developer setup:** changes to how developers run or build the code: where secrets come from, environment variables, ports, or a new script they must run.
- **Feature gates:** anything meant to stay behind a feature flag or internal check that leaks past it.
- **Gate integrity:** a gate is anything that would have made this change fail: a test, threshold, timeout, lint rule, type check, CI job, or snapshot. For each one removed, relaxed, skipped, or bypassed, ask: does this silence the failure it was added for, or does a measurement or decision in this diff justify it? Also flag a test that cannot fail: it asserts its own setup, mirrors the implementation, or has no negative.

Skip what the change clearly means to break when its scope is tight, unless the author seems unaware of the impact or the change looks malicious. Skip what a linter, formatter, or type checker catches.

Finish the research before you report: never write "this is fine if the backend handles it" when you can read the backend.

For a PR with Must fix or Should fix findings, read its discussion with `gh` after your audit, so your eyes stay fresh. Include valid findings you missed and mark where they came from.

## Instructions

Audit the change for compliance with the instructions loaded for this project: the user's global instructions, and the `AGENTS.md` or `CLAUDE.md` files that share a file path with the changed file or its parents. Flag clear, unambiguous violations where you can quote the exact rule being broken. Do not flag issues mentioned in the instructions but explicitly silenced in the code (e.g., via a lint ignore comment).

Treat a broken rule as a presumptive blocker unless the author can justify it clearly. For a structural rule, name the restructuring that removes the problem, and prefer the one that removes moving pieces over one that spreads them around.

## Validate

Treat each finding as a hypothesis to confirm or refute.

- Every finding needs a concrete case: "this input or situation leads to this wrong result". For a broken rule, the case is the rule and the line that breaks it. No case, no finding.
- Re-read the lines and confirm: the caller exists, the value can really be empty, the code really is unused.
- Quote file:line and verbatim text. For a missing field, quote its class definition; for a nullable value, its initialization; for a race, both sides. If you cannot quote the motivating lines, the finding is unverified.
- For framework-generated symbols, read and quote what generates them: metaclass, descriptor, ORM Meta block, migration, decorator or schema. Missing literal names in the class body or grep results do not prove absence.
- Propose the smallest fix that works. Prefer fixes that delete code.
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

Order findings by leverage: correctness and security first, then structure, then the rest. State a real bug plainly and quantify when you can ("adds ~50ms per item"). If the author has full context and disagrees, defer.

## Loop

Runs when the user passes `loop` with the request: follow [`references/loop.md`](references/loop.md). Without it, the review is a single pass.
