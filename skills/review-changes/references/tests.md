# Tests reviewer

Check that each test earns its upkeep: it catches a failure the other tests miss, and its expected result comes from somewhere other than the code it tests. The goal is useful coverage with little maintenance, not more tests or fewer. Zero findings is a valid result, and the number of tests removed is not a measure of the review.

This file stands on its own. When the project's `AGENTS.md` or `CLAUDE.md` has its own test rules, check the tests against those too. [`bugs.md`](bugs.md) also looks at tests that cannot fail and at removed gates; report a problem both files find once.

## What to check

Check the tests the change adds, changes or removes, and the existing tests of the behavior it changes. Read nearby tests as needed to validate a finding, but do not audit unrelated suites. In a [tests audit](../SKILL.md#tests-audit), check every selected test.

1. **What it protects.** Name the behavior or past bug each case guards, and where its expected result comes from: a requirement, a public contract, an invariant, or a named reference the code must match. A test whose expected value was copied from the code's output, or computed with the same helper the code uses, only proves the code equals itself. A characterization test is fine when keeping today's behavior is the stated goal.
2. **What the assertion sees.** Confirm the assertion observes the result the test claims: the return value, the error, the side effect, the stored record, the resource limit. A helper that drops the return value cannot prove that value's contract. A test that asserts its own setup, or has no way to fail, protects nothing.
3. **Proof that it fails.** For a new or changed test, look for evidence that it fails without the fix: a red run in the PR, check output, or a fix commit it would have caught. A failure from syntax, imports or setup is not that evidence. Missing evidence goes under `Not checked`; it does not prove the test is bad.
4. **Mocks.** Name the real interaction a mock or fake skips. A test that mocks the part it claims to check verifies nothing, so propose a test that reaches the real part. A fake for a third-party service at its boundary is not a finding.
5. **The level.** When the change touches a flow that a user or client runs (sign-in, checkout, a CLI command, a public library call) and no test enters where that client does, flag it: tests of the parts cannot show the wiring, routing or input mapping works. When a pure rule (rounding, time zones, parsing) is tested only through a slow outer layer that hides its edge cases, flag that too. Do not flag a test only for its level.
6. **Duplication.** Compare tests that look alike by precondition, asserted outcome and failure signal: starting state, storage path, boundary input, entry point. The same helper, the same covered lines, or similar names do not make tests duplicates. Table rows that reach the same rule and assert the same outcome add nothing, and a dependency's own input matrix belongs to the dependency.
7. **Removed or weakened tests.** For each removed test or loosened assertion, name the test that still covers it. Keep the regression test of a fixed bug, entry-point wiring, error paths, state changes, and allocation or performance checks that protect a stated requirement.

Test length, assertion count, coverage and mutation scores show where to look. They are never findings or quotas by themselves. There is no correct ratio of unit, integration and end-to-end tests.

## Severity

A wrong expected value that hides a real bug is Must fix. A risky path with no test that can fail on it, a mock that skips the behavior under test, and proven duplication are Should fix.

## Evidence for a removal

A finding that proposes to delete or merge tests also names:

- the exact cases to remove or merge, with file:line;
- the exact tests and assertions that keep the protection;
- why their preconditions, outcomes and failure signals match, for each dimension of a table or matrix;
- why regression and public-contract coverage survive.

Without that comparison it is not a finding. If the code cannot settle it, keep the tests and name the question under `Not checked`.

## Stay read-only

Do not break working code to watch a test fail, install tools, or run the full suite to complete this checklist. Proving that a test fails is the author's job.
