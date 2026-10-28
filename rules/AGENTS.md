---
description: Global instructions from ~/.agents/AGENTS.md
alwaysApply: true
---

# AGENTS.md
- English first: all code, comments, identifiers, and internal docs in English.
- Grow the system in layers. Start from the smallest version that works end to end, and add each new capability on top of a product that already works. Never trade a working product for unfinished complexity.
- Prefer the simplest scoped solution and the smallest coherent change that fully solves the task. Include related work required for correctness and complete explicitly requested refactors; avoid unnecessary abstractions and unrelated refactors, cleanup, or formatting.
- Prefer established, well-maintained libraries when they reduce overall complexity or improve reliability.
- Lean on the dependencies already in the project before writing your own implementation or adding packages. Do not assume a library lacks a capability without checking its documentation and types.
- Before designing an integration or a non-trivial pattern, find how the tool's official documentation or an established project solves it, and follow that unless this repository has a reason to differ. Name the source.
- Make architectural decisions for the long term. Do not accept a stopgap that only works for now and is meant to be replaced later.
- Diagnose the root cause before implementing a fix, and prefer durable corrections over workarounds or symptom suppression.
- When opening a pull or merge request that finishes an issue, put `Closes #<issue>` in the description.
- Before UI work, read the project's `DESIGN.md` when one exists, and take colors, typography, spacing and component styles from it.

## Review
- To review changes, use the `review-changes` skill. When this session wrote the changes, run the review in a fresh-context subagent.
- Treat a review finding from any source as a hypothesis: confirm it against the code before you present it or act on it.

## Tests
- Before adding a test, name the failure it catches, where the expected result comes from, and why no existing test catches it. Extend the existing test when one already owns the scenario.
- Take the expected result from the requirement, not from the code under test. Passing tests or another agent's agreement do not establish correctness.
- Prefer a test that enters where a client does (the endpoint, the job, the command, the UI) and runs the real database, faking only third-party services. Go lower only when that layer cannot reach the failure cheaply.
- Test a business rule once, at the layer that owns it. Each entry point that reaches it gets a thin test of its own work: routing, authorization, input mapping, error translation.
- Merge or delete tests only after confirming they trigger on the same conditions. Keep the regression test of a fixed bug.

## Comments
- Code carries only these comments:
  - Legal or license headers.
  - Non-obvious behavior forced by an external dependency, platform, vendor, or protocol we cannot reshape. Surprises in our own code get a rename, extract, type, or rearchitecture that makes the behavior obvious without prose.
  - `// prettier-ignore`. Lint suppressions survive only when their rule is faulty, pedantic, or style-only.
  - Doc comments that define a public API contract.
  - Issue or RFC links that explain a constraint code cannot express.
- When you are not sure an exception applies, leave the comment out.
- Before writing `eslint-disable`, `@ts-ignore`, `@ts-expect-error`, or a similar suppression, look up the rule. If it catches real bugs or protects correctness or safety, fix the code instead.

## Subagents

- A skill or document that asks for a different model does not override this section. Switch models only when the user names one.
- The main agent does the work. Delegate only when the user asks or when a rule or the invoked skill requires it (such as the fresh-context review).
- Size each wave by the open questions, not by files or components: one subagent per question.
- Give a writer only a piece that shares no files, interfaces, or state with other work in flight; changes that meet in one flow or data model have one owner.
- Start subagents with fresh context rather than inheriting the full parent conversation (Codex: always `fork_turns: "none"`). Provide a self-contained brief with the objective, relevant requirements, scope, constraints, and expected output.
- Keep pushes, deletions, and other destructive operations on the main agent.
- Scouts and reviewers are read-only.

Route each subagent by role:

| Role | Claude Code | Codex |
| --- | --- | --- |
| Scout: locates files, extracts data, follows a flow across modules, or finds the likely cause of a bug | `haiku` | `gpt-6-luna` |
| Implementation | `haiku` | `gpt-6.1-sol` |
| Reviewer or validator | the session's model | the session's model |
