---
name: file-pr
description: Use when the user asks to open or file a PR. Checks for an existing one, writes a title that says why, takes the body from the pr skill, and opens a real PR.
---

# File PR

Before filing, check whether a PR for this branch already exists. Check the
staged diff before committing. Before opening or updating the PR, inspect the
full branch diff with `git diff <base>...HEAD` against the target branch,
including earlier commits. Include the changes needed to deliver or maintain
the requested result.

Keep scratch scripts, traces, and one-off migration parity checks local.
Record their results and reproduction steps in the PR evidence. If a parity
check finds an uncovered failure that can recur after the migration, commit a
focused regression that asserts the supported contract directly.

PR titles usually become commit messages, so follow the repository's title
conventions. Look at recently merged PRs and Git history for examples. Prefer a
concise, human-readable title that explains why the change matters:

BAD

> ❌ perf(server): negotiate permessage-deflate on the websocket

GOOD

> ✅ perf(server): cut websocket frame size by 70%+ with gzipping

Write the description with the `pr` skill. If you weighed more than one viable
approach, add a short `## Alternatives` section: what you rejected and why.

Before submission, check the title, description, quotes, and attachments for
secrets and private details.

Open a real PR rather than a draft so review bots run. If `gh pr create` fails
because the GraphQL rate limit is used up, open it through REST with
`gh api repos/<owner>/<repo>/pulls -f title=... -f head=... -f base=... -F body=@<file>`. If the user also asked
to babysit it, continue with the `babysit-pr` skill.

Do not post a follow-up PR comment unless it serves the user's request.
