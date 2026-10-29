What this change does: Rejects malformed and non-object verification payloads after atomic removal from secondary storage. Adds regression coverage for invalid payloads and successful consumption of a valid record.

Looks good. Ship.

Checked parsing, expiry, cache cleanup, existing storage formats, and instruction compliance. No findings; `git diff --check` passed.

Not checked: Tests and lint were prohibited by the read-only constraint. Upstream source comparison was unavailable because the local checkout is absent.
