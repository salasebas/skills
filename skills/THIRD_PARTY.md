# Third-party skills

These skills are copies of other people's work, kept here so they stay available. Their attribution lives in this file, not in the skill files.

| Skill | Copied from | Commit | Licence | Changes |
| --- | --- | --- | --- | --- |
| `no-comments` | [`cursor/plugins`](https://github.com/cursor/plugins) `pstack/skills/no-comments` and `pstack/agents/comment-sicko.md` | `e8d856f0273b`, `99559f2f5204` | MIT | The agent's text moves to `references/comment-sicko.md` and a fresh-context subagent receives it. Calls to pstack's `how`, `why` and `architect` skills and its principle skills become plain instructions |
| `file-pr` | [`t3dotgg/tstack`](https://github.com/t3dotgg/tstack) `skills/file-pr` | `1085050f3bae` | MIT | The description paragraph and its examples become a pointer to the `pr` skill, the pointer to `leaving-pr-comments`, which is not installed, is gone, and the description records the alternatives ruled out |
| `full-send`, `full-stop` | `t3dotgg/tstack` `skills/full-send`, `skills/full-stop` | `1085050f3bae` | MIT | Full send's feedback step runs `review-changes` with `loop` where upstream runs `sol-loop`. Full stop no longer triggers on a closing "Full stop." used as emphasis. Full send asks before merging a high-risk change |
| `implement`, `implement-spec`, `spec-review` | [`mattpocock/skills`](https://github.com/mattpocock/skills) `skills/engineering/implement`, `implement-spec`, `code-review` | `a496f5513d4a` | MIT | `code-review` is renamed `spec-review`, with a description that fires only from these two skills or for a check against a ticket or spec. `implement` drops the full test suite at the end, which runs in CI |
| `python-development` | [`sammcj/agentic-coding`](https://github.com/sammcj/agentic-coding) `Skills/python-development` | `2f25cede7b08` | Apache-2.0 | None |
| `rust-best-practices` | [`morganlinton/BeautifulRust`](https://github.com/morganlinton/BeautifulRust) `skills/rust-best-practices`, and the checklist from `skills/rust-review` | `b9718436d77e` | MIT | The repository's conventions and design records win over the skill. Bevy material, the evals, the comment rules (`rules/AGENTS.md` owns them), the final checklist, and the pointer to BeautifulRust's lint files are gone. `--all-features` applies only to additive features. A crate-wide error enum is allowed. `Default` is left out of choices that have no safe default. Concurrency, unsafe, and performance rules move to `references/`. `rust-review`'s checklist becomes `references/review.md`, without its report format, which `review-changes` owns |
| `typescript-development` | `sammcj/agentic-coding` `Skills/typescript-development` | `2f25cede7b08` | Apache-2.0 | Adds the `pnpm` line |
| `typescript-development`, the Types table and `references/patterns.md` | [`cursor/plugins`](https://github.com/cursor/plugins) `pstack/skills/typescript-best-practices` | `23e4138daa01` | MIT | Drops the pointers to pstack's principle skills, which are not installed here |
| `golang-development` | `sammcj/agentic-coding` `Skills/golang-development` | `2f25cede7b08` | Apache-2.0 | Drops the line that copies a golangci config from the author's machine |

Each copy's description is rewritten to say when to use the skill and what it does.

The licence texts are in [`LICENSES/Apache-2.0.txt`](../LICENSES/Apache-2.0.txt), [`LICENSES/MIT-pstack.txt`](../LICENSES/MIT-pstack.txt), and [`LICENSES/MIT-beautifulrust.txt`](../LICENSES/MIT-beautifulrust.txt).

`review-changes` is assembled from several skills. Its sources are in [`review-changes/SOURCES.md`](./review-changes/SOURCES.md).
