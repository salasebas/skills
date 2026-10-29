# Run the review comparison

Use Codex CLI 0.165.0, Python 3.14, `uv`, and Git. Sign in to Codex with an account that can use `gpt-6.1-sol`. The runner copies `auth.json` into each temporary HOME with mode `0600`; keep the work directory private and do not commit it.

Run these commands from this repository. Keep the work directory outside the repository so reviewers cannot see the experiment's answers.

```bash
benchmark_dir=$(mktemp -d /tmp/review-changes-53.XXXXXX)
git clone --filter=blob:none --no-checkout https://github.com/mastodon/mastodon.git "$benchmark_dir/mastodon"
git -C "$benchmark_dir/mastodon" fetch origin pull/34489/head:refs/heads/case34489 pull/27511/head:refs/heads/case27511
git clone --filter=blob:none --no-checkout https://github.com/salasebas/better-auth-rb.git "$benchmark_dir/better-auth-rb"
git -C "$benchmark_dir/better-auth-rb" fetch origin 61fa967ebc5d35ad30241bc5c707d2321f8add8f
git clone --filter=blob:none --no-checkout https://github.com/salasebas/ports.git "$benchmark_dir/ports"
git -C "$benchmark_dir/ports" fetch origin 31b234c30d9aec825f09936bdd164f86fb12abc9
uv run --python 3.14 experiments/review-changes-53/run.py "$benchmark_dir"
```

The runner creates one worktree and HOME per case and variant, records the six planted cases before starting any review, and loads both sides of each diff before timing. It refuses to overwrite an existing run directory. Select cases with `--cases scope ownership`, or `--cases planted small medium`.

Codex retains its own read-only sandbox and restricted command network. When running this from another sandbox, the outer sandbox must allow access to Codex's private socket directory. The failed nested-sandbox pilots produced `app-server socket directory must be a user-owned directory with mode 0700`; they are excluded from the comparison.

Inspect each `report.md`, `result.json`, `events.jsonl`, and `home/.codex/sessions/` under the work directory. Regenerate the cumulative token summary with:

```bash
uv run --python 3.14 experiments/review-changes-53/run.py "$benchmark_dir" --summarize
```

Before scoring a run, verify that its diff was readable, its worktree stayed clean, and every session used `gpt-6.1-sol` with `high` effort. A must have one session and no spawn calls. B must have exactly two child sessions, fresh-context spawn calls, overlapping execution intervals, and one reference file per child. Inspect tool calls for violations of the read-only command instructions. `read_succeeded` alone does not establish these conditions.

Validate findings against the checked-out code. Score the five clear planted violations separately from the synthetic file-size case. Record each additional finding as confirmed, refuted, or not checked. Keep the report and a credential-free extract of session metadata and usage; raw HOME directories contain credentials and account metadata.

The command setup follows the official OpenAI documentation for [non-interactive execution](https://developers.openai.com/codex/noninteractive), [subagents](https://developers.openai.com/codex/multi-agent), and [configuration](https://developers.openai.com/codex/config-reference). The tested CLI's `codex exec --help` supplies `--ignore-user-config`, JSON events, and output-file options.
