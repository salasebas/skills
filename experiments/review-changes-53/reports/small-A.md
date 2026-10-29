What this change does: Rejects malformed and non-object verification payloads after atomic deletion from secondary storage. Adds regression coverage while preserving lookup behavior.

Looks good. Ship.

Checked parsing, date normalization, identifier fallback, cleanup, callers, and project instructions. No confirmed findings; `git diff --check` passed.

Not checked: Tests and lint were prohibited by the read-only constraints. Upstream source comparison was unavailable because the checkout is absent.
