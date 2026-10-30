# Loop

Use a reviewer to review your code in a loop.

Make the most minimal possible changes to appease the reviewer. Be careful
of scope creep and don't be scared to push back.

## Budget

- Default: 3 rounds total. Round 1 is full. Later rounds check only
  changed code and open findings.
- Extend to 5 only for security, permissions, auth, data loss, or
  state/concurrency, while a Must fix or Should fix stays open with evidence. Or when
  the user asks.
- Stop early if a round returns only Nice to have findings. Declined findings and comment,
  doc, or format-only fixes need no new round.
- One reviewer only. The reviewer must not start subagents or reviewers.
- Keep a ledger: id, severity, outcome. Never guess it.

## 1. Scope

Find the scope as in [Scope](../SKILL.md#scope). Use one diff command all rounds. State intent and out-of-scope in 1-2
sentences. Run covering checks. Do not send code this change breaks. Note
missing or pre-failing checks in the brief.

## 2. Start the reviewer

Start one new subagent with fresh context every round, through the environment's orchestrator when it has one, else the harness's own subagents:

- T3 Code: `delegate_task`, role `review`.
- Codex: `spawn_agent` with `fork_turns: "none"`.

Use the model the user names; if no route runs it, report the blocker. Unnamed: another vendor's model, else another model, else the session's.

Do not edit scoped files while review runs. Wait for the notice. Do not
poll or start a second reviewer. Timeout, error, or no reply is not
approval.

Round 1 brief (the reviewer gets no history):

```
Review only. Do not edit, commit, push, comment on PRs, start subagents, or run project code, tests, or network commands.
Repo: <abs path> Base: <sha> Intent: <intent> Out of scope: <scope> Checks: <results>
See: git diff <base> [-- <paths>]; git status --short (read untracked).
Follow the review-changes skill's Workflow through validation.
Reply:
VERDICT: APPROVE or CHANGES
S1 [Must fix|Should fix|Nice to have] <file>:<line> <claim>. Fix: <suggestion> (stable ids)
```

## 3. Answer findings

Check each finding and severity yourself. Another path, rare case, or
small cost is Nice to have, whatever label it came with.

- Agree: smallest fix. Prefer delete or narrow over new lock, cache,
  helper, or option. Fix the case that happened. Add one focused test
  that fails without the fix, if intent needs it.
- Disagree: say why, with evidence (file:line, test, output).
- Out of scope or Nice to have: decline in one line. List as follow-up.

Update the ledger. Re-run checks and `git diff --shortstat <base>`. If
review grew the diff, cut first. Do not agree just to end the loop.

## 4. Next round

Start one only if budget remains and a Must fix or Should fix is open, behavior code
changed, or approval does not cover the current behavior diff. Send the round 1 brief,
the ledger (`fixed:` / `disagree:` / `declined:` + evidence), the same base
diff, and the change since last round. Tell the reviewer: open ids and changed code only.
Mark each old id `resolved` or `still open: <reason>`.

## 5. Stop and ship

Agreed: APPROVE on the current behavior diff, no Must fix or Should fix open,
no concern of your own. Stuck: an item stays disputed after two replies,
or budget ends. Show both sides in 2-3 lines each. The user decides.
Budget end is not approval.

Do not push during the loop. Push after agreement only if the user asked
to push, ship, or update the PR. If you push to a PR, add above the model
blurb:

`Reviewed with review-changes loop: <N> rounds with <model>. Verdict: approved`.

Report: rounds, model, what the reviewer changed, diff size before/after, fixed and
declined findings with reasons, pushed or not. Fixes made after the last round have not been reviewed: say so, and never present them as reviewed.
