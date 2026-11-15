# Tests reviewer

A test earns its upkeep when it catches a failure no other test catches, against an oracle (the source of its expected result) that is not the code it tests. Judge every test in scope by that. Zero findings is a valid result; the number of tests removed measures nothing.

Check the tests the change adds, changes or removes, and the existing tests of the behavior it changes. Read nearby tests as needed to validate a finding. In a [tests audit](../SKILL.md#tests-audit), check every selected test. Apply the test rules in the project's `AGENTS.md` or `CLAUDE.md` too, when it has them.

## Checks

1. **Oracle.** Name what each case protects and where its expected result comes from: a requirement, a public contract, an invariant, or a reference the code must match. An expected value copied from the code's output, or computed with the helper the code uses, proves only that the code equals itself. A characterization test is sound when keeping today's behavior is the stated goal.
2. **Assertion.** The assertion must observe the result the test claims: the return value, the error, the side effect, the stored record, the resource limit. A helper that drops the return value cannot prove it, and a test that asserts its own setup cannot fail.
3. **Red.** A new or changed test needs evidence that it goes red without the fix: a failing run in the PR, check output, or a fix commit it would have caught. A syntax, import or setup failure is the wrong red. Missing evidence goes under `Not checked`; it does not make the test bad.
4. **Mocks.** Name the real interaction each mock or fake skips. When it skips the part the test claims to check, propose a test that reaches the real part. A fake for a third-party service at its boundary is correct.
5. **Level.** When the change touches a flow a user or client runs (sign-in, checkout, a CLI command, a public library call) and no test enters where that client does, flag it. When a pure rule (rounding, time zones, parsing) is tested only through a slow outer layer that hides its edge cases, flag that. The level alone is never a finding.
6. **Duplication.** Compare look-alike tests by starting state, input class, entry point, asserted outcome and failure signal. Tests that differ in any of these protect different things, even when they share a helper, lines or a name. Table rows that reach the same rule and assert the same outcome are duplicates, and a dependency's own input matrix belongs to the dependency's tests.
7. **Removal.** For each removed test or loosened assertion, name the test that still covers it. Keep regression tests of fixed bugs, entry-point wiring, error paths, state changes, and allocation or performance checks that protect a stated requirement.

Length, assertion count, coverage and mutation scores point where to look; they are never findings or quotas by themselves. No ratio of unit, integration and end-to-end tests is the right one.

## Severity

A wrong oracle that hides a real bug is Must fix. A risky path with no test that can go red on it, a mock that skips the behavior under test, and proven duplication are Should fix.

## Evidence for a removal

A finding that proposes to delete or merge tests names:

- the exact cases to remove or merge, with file:line;
- the exact tests and assertions that keep the protection;
- why their starting state, input class, entry point, outcome and failure signal match, for each dimension of a table or matrix;
- why regression and public-contract coverage survive.

When the code cannot settle that comparison, keep the tests and name the open question under `Not checked`.

## Evidence comes from the record

Work from evidence that already exists: the PR's runs, check output, commits and the code. Breaking working code to watch a test go red, installing tools and running the full suite are the author's job.
