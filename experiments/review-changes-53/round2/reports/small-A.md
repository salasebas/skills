What this change does: Rejects malformed JSON and non-object payloads when consuming verification records from secondary storage. Adds regression coverage for rejection, deletion, and successful consumption.

Looks good. Ship.

Checked parsing, expiry handling, atomic removal, hashed identifiers, callers, and project instructions. `git diff --check` passed. No confirmed findings.

Not checked: Tests and lint were prohibited by the read-only constraints; upstream parity sources were unavailable locally.
