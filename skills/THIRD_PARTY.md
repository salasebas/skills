# Third-party skills

These skills are copies of other people's work, kept here so they stay available. Their attribution lives in this file, not in the skill files.

| Skill | Copied from | Commit | Licence | Changes |
| --- | --- | --- | --- | --- |
| `no-comments` | [`cursor/plugins`](https://github.com/cursor/plugins) `pstack/skills/no-comments` and `pstack/agents/comment-sicko.md` | `e8d856f0273b`, `99559f2f5204` | MIT | The agent's text moves to `references/comment-sicko.md` and a fresh-context subagent receives it. Calls to pstack's `how`, `why` and `architect` skills and its principle skills become plain instructions |
| `file-pr` | [`t3dotgg/tstack`](https://github.com/t3dotgg/tstack) `skills/file-pr` | `1085050f3bae` | MIT | The description paragraph and its examples become a pointer to the `pr` skill |
| `python-development` | [`sammcj/agentic-coding`](https://github.com/sammcj/agentic-coding) `Skills/python-development` | `2f25cede7b08` | Apache-2.0 | None |
| `rust-development` | `sammcj/agentic-coding` `Skills/rust-development` | `2f25cede7b08` | Apache-2.0 | None |
| `typescript-development` | `sammcj/agentic-coding` `Skills/typescript-development` | `2f25cede7b08` | Apache-2.0 | Adds the `pnpm` line |
| `typescript-development`, the Types table and `references/patterns.md` | [`cursor/plugins`](https://github.com/cursor/plugins) `pstack/skills/typescript-best-practices` | `23e4138daa01` | MIT | Drops the pointers to pstack's principle skills, which are not installed here |
| `golang-development` | `sammcj/agentic-coding` `Skills/golang-development` | `2f25cede7b08` | Apache-2.0 | Drops the line that copies a golangci config from the author's machine |

The licence texts are in [`LICENSES/Apache-2.0.txt`](../LICENSES/Apache-2.0.txt) and [`LICENSES/MIT-pstack.txt`](../LICENSES/MIT-pstack.txt).

`review-changes` is assembled from several skills. Its sources are in [`review-changes/SOURCES.md`](./review-changes/SOURCES.md).
