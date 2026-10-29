What this change does: Rejects malformed and non-object JSON when consuming verification values from secondary storage. Adds regression coverage for rejection, deletion, and successful consumption.

Looks good. Ship. No confirmed bug or instruction findings.

Checked parsing, storage writers, callers, and regression coverage. `git diff --check` passed.

Not checked: Tests and lint were prohibited by the read-only constraints. Upstream parity could not be checked because the source checkout is absent.
