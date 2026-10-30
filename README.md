# Skills

My setup for coding agents: the global rules, the skills I keep, and the skills I install from other people.

## Skills kept here

| Skill | What it does |
| --- | --- |
| [`review-changes`](./skills/review-changes/SKILL.md) | Reviews a change for bugs and for compliance with your `AGENTS.md` and `CLAUDE.md`, and validates every finding before reporting it. `loop` has a reviewer subagent, on another model when one is available, review in rounds while the session fixes. |
| [`file-pr`](./skills/file-pr/SKILL.md) | Opens a PR: checks for an existing one, a title that says why the change matters, the body from `pr`, and no drafts. From [`t3dotgg/tstack`](https://github.com/t3dotgg/tstack). |
| [`full-send`](./skills/full-send/SKILL.md), [`full-stop`](./skills/full-stop/SKILL.md) | Say "full send" or "full stop" and the agent takes the change to a PR alone: proof, `review-changes` loop, `file-pr`, `babysit-pr`. Full send merges when the PR is ready; full stop leaves it for you. From [`t3dotgg/tstack`](https://github.com/t3dotgg/tstack). |
| [`python-development`](./skills/python-development/SKILL.md) | Conventions for Python projects: `uv`, type hints, PEP 723 scripts. |
| [`typescript-development`](./skills/typescript-development/SKILL.md) | Conventions for TypeScript and JavaScript projects: strict mode, `pnpm`, and rules for modelling types. |
| [`rust-development`](./skills/rust-development/SKILL.md) | Conventions for Rust projects: workspaces, crate features, public APIs. |
| [`golang-development`](./skills/golang-development/SKILL.md) | Conventions for Go projects, with a testing reference. |
| [`no-comments`](./skills/no-comments/SKILL.md) | Removes comments from a diff with a fresh-context subagent and fixes the code the comments were excusing. Runs when you type `/no-comments`. |

The language skills load only in a project that uses that language. They are copies of sammcj's skills, and the TypeScript one adds pstack's type rules; [`skills/THIRD_PARTY.md`](./skills/THIRD_PARTY.md) has the attribution.

`review-changes` is assembled from other review skills. [`SOURCES.md`](./skills/review-changes/SOURCES.md) records where each part came from, why the skill is shaped the way it is, and how to update it.

### Install

One skill, or all of them:

```bash
npx skills add salasebas/skills -g -s review-changes
```

```bash
npx skills add salasebas/skills -g -s review-changes -s file-pr -s full-send -s full-stop -s python-development -s typescript-development -s rust-development -s golang-development -s no-comments
```

## Global rules

[`rules/AGENTS.md`](./rules/AGENTS.md) holds the instructions every session loads. Each harness reads it from a different place:

| Harness | Where the file goes |
| --- | --- |
| Codex, Grok | `~/.agents/AGENTS.md` |
| Claude Code | `~/.claude/CLAUDE.md`, a symlink to `~/.agents/AGENTS.md` |
| Cursor | `~/.cursor/rules/agents.mdc`, a symlink to `~/.agents/AGENTS.md`. The frontmatter at the top of the file is for Cursor. |

The Comments section is the list of allowed comments from pstack's Comment Sicko ([`comment-sicko.md`](./skills/no-comments/references/comment-sicko.md)), without the persona or the review flow. It stops comments from being written; `/no-comments` removes the ones that got through.

## Skills installed from other people

These are not copied here. Install any of them with `npx skills add <source> -g -s <skill>`.

| Source | Skills |
| --- | --- |
| [`mattpocock/skills`](https://github.com/mattpocock/skills) | `ask-matt`, `code-review`, `codebase-design`, `diagnosing-bugs`, `domain-modeling`, `grill-me`, `grill-with-docs`, `grilling`, `handoff`, `implement`, `implement-spec`, `improve-codebase-architecture`, `pr`, `research`, `retro`, `setup-matt-pocock-skills`, `tdd`, `teach`, `to-spec`, `to-tickets`, `triage`, `wait-what`, `wayfinder`, `writing-for-agents` |
| [`emilkowalski/skills`](https://github.com/emilkowalski/skills) | `animation-performance`, `animation-vocabulary`, `emil-design-eng`, `improve-animations`, `mobile-native`, `pick-ui-library`, `review-animations` |
| [`sammcj/agentic-coding`](https://github.com/sammcj/agentic-coding) | `shell-scripting`, `writing-documentation-with-diataxis` |
| [`cursor/plugins`](https://github.com/cursor/plugins), `pstack` | `technical-writing`, `unslop` |
| `cursor/plugins`, `cursor-team-kit` | `deslop` |
| [`vercel-labs/agent-skills`](https://github.com/vercel-labs/agent-skills) | `vercel-composition-patterns`, `vercel-react-best-practices`, `web-design-guidelines` |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | `code-simplification` |
| [`vojtaholik/good-css`](https://github.com/vojtaholik/good-css) | `good-css` |
| [`motiondivision/ai-kit`](https://github.com/motiondivision/ai-kit) | `motion` |
| [`vercel-labs/agent-browser`](https://github.com/vercel-labs/agent-browser) | `agent-browser` |
| [`currents-dev/playwright-best-practices-skill`](https://github.com/currents-dev/playwright-best-practices-skill) | `playwright-best-practices` |
| [`vercel-labs/skills`](https://github.com/vercel-labs/skills) | `find-skills` |
| [`t3dotgg/tstack`](https://github.com/t3dotgg/tstack) | `babysit-pr`, `council`, `modernize` |

For the two `cursor/plugins` rows the source is the folder URL, for example `https://github.com/cursor/plugins/tree/main/pstack`.

`animate-expo`, also from `emilkowalski/skills`, is installed per project in Expo projects: `npx skills add emilkowalski/skills -s animate-expo`.

[`sources.json`](./sources.json) records the folder hash of each copy I last installed, so a rename or removal upstream shows up. It is not a backup of the skill text.

## Links

Things I come back to. None of them is installed by this repo.

| Link | What it is |
| --- | --- |
| [`google-labs-code/design.md`](https://github.com/google-labs-code/design.md) | The `DESIGN.md` format: design tokens in YAML front matter, the reasoning in prose. `npx @google/design.md lint DESIGN.md` validates the file. |
| [`VoltAgent/awesome-design-md`](https://github.com/VoltAgent/awesome-design-md) | `DESIGN.md` files modelled on the design systems of well-known brands, to copy and adjust. |
| [vercel.com/design.md](https://vercel.com/design.md) | Vercel's own `DESIGN.md`, as a worked example. |

## Licence

[MIT](./LICENSE). `review-changes` includes text from other MIT-licensed skills, named in its [`SOURCES.md`](./skills/review-changes/SOURCES.md). The skills in [`skills/THIRD_PARTY.md`](./skills/THIRD_PARTY.md) keep their own licence.
