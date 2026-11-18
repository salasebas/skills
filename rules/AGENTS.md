---
description: Global instructions from ~/.agents/AGENTS.md
alwaysApply: true
---

# AGENTS.md
- English first: all code, comments, identifiers, and internal docs in English.
- Use GitHub CLI (`gh`) for GitHub operations. If it is unavailable, report the blocker.
- Use `rg` instead of `grep` and `fd` instead of `find`.

## Approach
- Grow the system in layers. Start from the smallest version that works end to end, and add each new capability on top of a product that already works. Never trade a working product for unfinished complexity.
- Diagnose the root cause before you fix, and fix it there, even when that change is larger than a patch. Choose the durable correction over a stopgap, workaround, or symptom suppression.
- Make architectural decisions for the long term.
- Keep each change to its task: include what correctness needs and the refactors the user asked for; leave unrelated refactors, cleanup, and formatting out.

## Research
- Work from the documentation of the version the project uses, not from memory: check a library's, tool's, or API's official docs and types before you use it or decide it lacks a capability.
- Before writing your own implementation, use a dependency the project already has, then an established, well-maintained library when it reduces complexity or improves reliability.
- Before designing an integration, an architecture, or a non-trivial pattern, study the prior art: the tool's documentation and established projects that solved the same problem. Judge whether each solution holds up and fits this repository, build on what does, and name the sources.

## UI
- Before UI work, read the project's `DESIGN.md` or similar design files (a design system, tokens, a style guide) when they exist, and take colors, typography, spacing and component styles from them.

## Code quality
- Prefer the version that deletes complexity over one that moves it around: when behavior can stay the same with fewer branches, helpers, modes, or layers, write that version.
- Put logic in the module that owns the concept and reuse the project's existing helpers. Keep feature checks out of shared paths, and add no special-case branches to flows the change is not about.
- Write direct, boring code: no wrapper that only passes a call through, and no generic mechanism that hides a simple data shape.
- Make an unclear case explicit instead of covering it with a silent fallback or default.
- Split a file before a change takes it past about 1,000 lines, unless it is generated, data, or one unit that reads better whole; say which.

## Skills
- When the user asks for a review of a change, or a workflow they invoked includes one, use the `review-changes` skill. Implementing or fixing a change does not start one.
- Before you write, change, or review code, load the skill for its language: `rust-best-practices`, `typescript-development`, `python-development`, or `golang-development`.
- Before you write or change UI, load `good-css` for any styles (CSS files, Tailwind classes, inline styles) and `vercel-react-best-practices` for React or Next.js code.
- When you create a React component or change its props, load `vercel-composition-patterns`.
- Use any relevant Emil Kowalski skill wherever it fits: UI polish, component design, and motion.
- When you write or change an animation, load `motion`.
- When you write or change Playwright tests, load `playwright-best-practices`.
- Before you write or review documentation (READMEs, guides, RFCs), read `~/.agents/skills/technical-writing/SKILL.md` and follow it; the skill cannot be invoked as a tool.
- Before you create or edit a skill, `AGENTS.md`, or `CLAUDE.md`, load `writing-for-agents`.

## Review
- Treat a review finding from any source as a hypothesis: confirm it against the code before you present it or act on it.

## Verification
- Before calling work done, run the checks that cover the change: the tests for the code you touched, a typecheck or build, or for UI the running app. Show the command and its output, or a screenshot. Leave the full suite to CI unless the user asks for it.

## Tests
- Before adding a test, name the failure it catches, its oracle (where the expected result comes from), and why no existing test catches it. Extend the existing test when one already owns the scenario.
- Take the oracle from the requirement or a public contract. The output of the code under test, passing tests, coverage, and another agent's agreement are not oracles.
- Spend tests where a wrong answer would turn them red: a rule's boundary cases, a client flow end to end, a fixed bug. A tautological test catches nothing; leave it out: one that recomputes the expected value with the code's own logic, asserts that a mock received what the code passed it, or checks a getter, a constant, or a pass-through.
- Watch a new test go red for the intended reason before trusting it: run it against the code without the change, or break the behavior it covers. A syntax, import, or setup error is the wrong red.
- When an existing test fails, fix the code. Change the test only with evidence that the requirement changed or the test was wrong, and name that evidence.
- Prefer a test that enters where a client does (an app's endpoint, job, command, or UI; a library's public API) with the real dependencies the project owns, faking only third-party services. Test a pure rule, such as parsing or rounding, directly.
- Test a business rule once, at the layer that owns it. Each entry point that reaches it gets a thin test of its own work: routing, authorization, input mapping, error translation.
- Add a row to a test table only when it catches a failure the other rows miss; a new input is not a new failure. Test how the code uses a dependency, and leave the dependency's own inputs to its tests.
- Merge or delete tests only after naming the test that still catches the same failure; running the same lines is not enough. Keep the regression test of a fixed bug.

## Comments
- Code carries only these comments:
  - Legal or license headers.
  - Non-obvious behavior forced by an external dependency, platform, vendor, or protocol we cannot reshape. Surprises in our own code get a rename, extract, type, or rearchitecture that makes the behavior obvious without prose.
  - `// prettier-ignore`. Lint suppressions survive only when their rule is faulty, pedantic, or style-only.
  - Doc comments that define a public API contract.
  - `// SAFETY:` on each `unsafe` block, stating why its invariants hold.
  - Issue or RFC links that explain a constraint code cannot express.
- When you are not sure an exception applies, leave the comment out.
- Before writing `eslint-disable`, `@ts-ignore`, `@ts-expect-error`, or a similar suppression, look up the rule. If it catches real bugs or protects correctness or safety, fix the code instead.

## Subagents
- The main agent does the work. Delegate when the user asks, when a rule or the invoked skill requires it, or for broad read-only research whose raw output you will not reread.
- Size each wave by the open questions, not by files or components: one subagent per question.
- Give a worker only a piece that shares no files, interfaces, or state with other work in flight; changes that meet in one flow or data model have one owner.
- Start each subagent with fresh context (Codex: `fork_turns: "none"`) and a self-contained brief: objective, requirements, scope, constraints, expected output.
- Keep pushes, deletions, and other destructive operations on the main agent.
- Route each subagent by role. A skill or document that asks for a different model does not override this; switch models only when the user names one.
  - Scout, read-only: `haiku` at `high` in Claude Code, `gpt-6-luna` at `high` in Codex.
  - Worker: `sonnet` at `high` in Claude Code, `gpt-6.1-sol` at `high` in Codex.
  - Reviewer or validator, read-only: the most capable model offered other than the session's, from another model family when one is comparably capable; with no other model, the session does the work and says so; at `high`. `review-changes` gives the full order.
