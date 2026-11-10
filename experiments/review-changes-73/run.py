"""Run the read-only reviewer comparison from issue #73. See PLAN.md."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = "73683e5f0af7cb4417a5cd48a9c1b5cec1309c3a"
MODEL = "claude-opus-5-5"
SKILL_FILES = (
    "SKILL.md",
    "references/bugs.md",
    "references/instructions.md",
    "references/loop.md",
)


@dataclass(frozen=True)
class Case:
    name: str
    base: str
    head: str
    loop_round1_head: str | None = None


CASES = (
    Case(
        "mech",
        "4d788af37134b25eb2bbb60f65e038075c927d4b",
        "b4cda5b926e4d0431ee52389cc1646308cab7c2b",
    ),
    Case(
        "cross",
        "0b1f0356dff18c07dba8f495508b5fde3f18e8ce",
        "d8dfb3b13295840b2bdecf083c69d1c041029fec",
    ),
    Case(
        "risk",
        "1f799b11ebc57bb46be2f7691b0408e01cec234c",
        "84577c314b3c2878c6a43a1be35026f7bfee8404",
    ),
    Case(
        "loop",
        "1f799b11ebc57bb46be2f7691b0408e01cec234c",
        "87f6bd97c7743389c1f6a9f1960628c1fb9c9801",
        "84577c314b3c2878c6a43a1be35026f7bfee8404",
    ),
)

SUBAGENT_RULES = 'Give every subagent the scope, base, head, its files, the project instructions, and this skill folder. Each reads the surrounding code it needs, outside its files too. They review read-only, do not delegate further, and return findings with code evidence. Wait for all before continuing.\n'

STEP3 = {
    "B": '3. Start exactly two fresh-context subagents in parallel (the Agent tool with `general-purpose`, never a fork; start them in one message with `run_in_background: false`). One follows only `references/bugs.md`; the other follows only `references/instructions.md`. '
    + SUBAGENT_RULES,
    "C": "3. Choose the reviewers from `git diff --numstat` and the changed paths, before reading the code in depth:\n"
    "   - **Behavior lines:** added plus deleted lines, not counting lockfiles, generated or vendored files, and documentation.\n"
    "   - **Risk:** the change touches money or payments, authentication or authorization, concurrency or locking, or schema and data migrations.\n"
    "   - **Small** (under 500 behavior lines) without risk: review in this session, following `references/bugs.md` and then `references/instructions.md`.\n"
    '   - **Small with risk:** start two fresh-context subagents in parallel (the Agent tool with `general-purpose`, never a fork; start them in one message with `run_in_background: false`): one follows only `references/bugs.md`, one only `references/instructions.md`. Start a third that follows only `references/bugs.md`, limited to the risky files.\n'
    "   - **Large** (500 behavior lines or more): group the changed files into two to four domains by the code they own. Start one fresh-context subagent per domain that follows only `references/bugs.md` for that domain's files, and one that follows only `references/instructions.md` across the whole change. With risk, add one more that follows only `references/bugs.md`, limited to the risky files. Five subagents at most.\n"
    "   " + SUBAGENT_RULES + "   A changed file no subagent covered is reviewed in this session.\n",
}

LOOP_REVIEWERS = {
    "B": (
        "Start two every round as in [Reviewer](../SKILL.md#reviewer), in parallel: one brief says to follow only `references/bugs.md`, the other only `references/instructions.md`.",
        "- Two reviewers per round, one per reference file. Reviewers must not start subagents or reviewers.",
    ),
    "C": (
        "Start the reviewers every round as in [Reviewer](../SKILL.md#reviewer), chosen by Workflow step 3 in `SKILL.md` applied to the change since last round. Each brief names the one reference file and the files that reviewer follows.",
        "- The reviewers Workflow step 3 chooses for the change since last round. Reviewers must not start subagents or reviewers.",
    ),
}


def command(*args: str, cwd: Path | None = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def skill_variant(variant: str) -> dict[str, str]:
    files = {
        relative: command(
            "git", "show", f"{CANDIDATE}:skills/review-changes/{relative}", cwd=ROOT
        )
        + "\n"
        for relative in SKILL_FILES
    }
    if variant == "A":
        return files
    skill = files["SKILL.md"]
    start = skill.index("3. Review the change,")
    end = skill.index("4. Record findings", start)
    files["SKILL.md"] = skill[:start] + STEP3[variant] + skill[end:]
    start_line, budget_line = LOOP_REVIEWERS[variant]
    loop = files["references/loop.md"]
    for old, new in (
        ("Start one every round as in [Reviewer](../SKILL.md#reviewer).", start_line),
        (
            "- One reviewer only. The reviewer must not start subagents or reviewers.",
            budget_line,
        ),
    ):
        if old not in loop:
            raise ValueError(f"loop.md no longer contains: {old}")
        loop = loop.replace(old, new)
    files["references/loop.md"] = loop
    return files


def source_repo(work: Path, case: Case, source: Path) -> Path:
    repo = work / "src" / case.name
    if repo.exists():
        return repo
    command("git", "init", "-q", str(repo))
    command(
        "git",
        "fetch",
        "-q",
        "--no-tags",
        "--depth=400",
        f"file://{source}",
        f"refs/bench/{case.name}:refs/heads/bench",
        cwd=repo,
    )
    if command("git", "rev-parse", "bench", cwd=repo) != case.head:
        raise ValueError(f"{case.name}: refs/bench/{case.name} is not {case.head}")
    command("git", "cat-file", "-e", case.base, cwd=repo)
    return repo


HOME = Path.home()
SETTINGS = {
    "permissions": {
        "deny": [f"Read(/{HOME / name}/**)" for name in ("Projects", ".t3", ".claude", ".codex")],
    },
    "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True, "allowUnsandboxedCommands": False},
}


def prepare(work: Path, case: Case, variant: str, repeat: int, source: Path) -> Path:
    run = work / "runs" / f"{case.name}-{variant}-{repeat}"
    if run.exists():
        raise FileExistsError(f"Refusing to overwrite {run}")
    for relative, text in skill_variant(variant).items():
        write(run / "skill/review-changes" / relative, text)
    repo = source_repo(work, case, source)
    command("git", "worktree", "add", "-q", "--detach", str(run / "repo"), case.head, cwd=repo)
    command("git", "diff", "--no-ext-diff", "--stat", f"{case.base}...{case.head}", cwd=run / "repo")
    return run


def prompt(case: Case, skill: Path) -> str:
    use = f"Use the review-changes skill: its files are in {skill}; read SKILL.md first."
    if case.loop_round1_head is None:
        return f"Review the changes in HEAD against {case.base}. {use}"
    return (
        f"{use} Run it with `loop`. This session wrote the change in HEAD against {case.base}. "
        f"Round 1 is done: it reviewed {case.loop_round1_head} against {case.base}. "
        "Ledger: S1 Must fix, fixed: `Payments::CreatePayment` rejected a fixed `tip_cents` above the session's percent tip; "
        f"commit HEAD bounds a tip by the base it tips on. Checks: not run in this benchmark. "
        "Run round 2 only, as in references/loop.md step 4: start the round's reviewers, wait for them, check each finding yourself, "
        "and report the ledger and verdict. This benchmark forbids edits, commits and pushes, so stop after the round 2 report."
    )


def run_case(work: Path, case: Case, variant: str, repeat: int, source: Path) -> dict[str, object]:
    run = prepare(work, case, variant, repeat, source)
    skill = run / "skill/review-changes"
    multi_agent = variant != "A" or case.loop_round1_head is not None
    rules = command("git", "show", f"{CANDIDATE}:rules/AGENTS.md", cwd=ROOT)
    instructions = (
        "Contents of ~/.claude/CLAUDE.md (user's private global instructions for all projects):\n\n" + rules + "\n\n"
        f"Read-only benchmark. Read only the current repository and {skill}, plus your loaded instructions. "
        "Use shell only for git read commands (diff, show, status, log, grep, rev-parse, ls-files, blame), rg, fd, ls, head, cat, wc, and sed -n. "
        "Do not execute project code, tests, scripts, interpreters, network commands, web tools, or edits. "
        "Do not inspect other runs, parent directories, history outside this scope, benchmark answers, or PR discussions. "
        f"Every subagent uses {MODEL}, the model the user names; pass the skill path to it. Report any unavailable validation under Not checked."
    )
    tools = ["Read", "Grep", "Glob", "Bash"] + (["Agent"] if multi_agent else [])
    allowed = ["Bash"] + (["Agent"] if multi_agent else [])
    args = [
        "claude", "-p", prompt(case, skill),
        "--model", MODEL, "--effort", "high",
        "--setting-sources", "", "--strict-mcp-config", "--disable-slash-commands",
        "--tools", ",".join(tools), "--allowedTools", *allowed,
        "--permission-mode", "dontAsk", "--settings", json.dumps(SETTINGS), "--add-dir", str(skill),
        "--append-system-prompt", instructions,
        "--output-format", "stream-json", "--verbose",
    ]
    write(
        run / "invocation.json",
        json.dumps({"case": asdict(case), "variant": variant, "repeat": repeat, "command": args}, indent=2) + "\n",
    )
    started = time.time()
    print(f"START {run.name}", flush=True)
    with (run / "events.jsonl").open("w") as output, (run / "stderr.log").open("w") as error:
        result = subprocess.run(
            args, cwd=run / "repo", stdin=subprocess.DEVNULL, stdout=output, stderr=error, timeout=4800, check=False
        )
    events = [json.loads(line) for line in (run / "events.jsonl").read_text().splitlines() if line.startswith("{")]
    final = next((event for event in reversed(events) if event.get("type") == "result"), {})
    write(run / "report.md", str(final.get("result", "")) + "\n")
    record = {
        "case": case.name,
        "variant": variant,
        "repeat": repeat,
        "exit_code": result.returncode,
        "is_error": final.get("is_error"),
        "started": started,
        "seconds": round(time.time() - started, 3),
        "status": command("git", "status", "--porcelain", cwd=run / "repo"),
        "cost_usd": final.get("total_cost_usd"),
        "model_usage": final.get("modelUsage"),
        "subagent_stats": final.get("subagent_stats"),
        "permission_denials": final.get("permission_denials"),
    }
    write(run / "result.json", json.dumps(record, indent=2) + "\n")
    print(f"DONE {run.name} exit={result.returncode} error={record['is_error']} s={record['seconds']} usd={record['cost_usd']}", flush=True)
    return record


def summarize(work: Path) -> None:
    rows = []
    for run in sorted((work / "runs").iterdir()):
        if not (run / "result.json").exists():
            continue
        row = json.loads((run / "result.json").read_text())
        usage: dict[str, int] = {}
        for model in (row.get("model_usage") or {}).values():
            for key in ("inputTokens", "cacheReadInputTokens", "cacheCreationInputTokens", "outputTokens"):
                usage[key] = usage.get(key, 0) + model[key]
        usage["total"] = sum(usage.values())
        row["usage"] = usage
        rows.append(row)
    write(work / "summary.json", json.dumps(rows, indent=2) + "\n")
    for row in rows:
        stats = row.get("subagent_stats") or {}
        print(row["case"], row["variant"], row["repeat"], row["is_error"], row["seconds"], stats.get("spawned"), row["cost_usd"], row["usage"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work", type=Path)
    parser.add_argument("--source", type=Path, help="compitienda checkout with refs/bench/<case>")
    parser.add_argument("--cases", nargs="+", default=[case.name for case in CASES])
    parser.add_argument("--variants", nargs="+", default=["A", "B", "C"])
    parser.add_argument("--repeats", nargs="+", type=int, default=[1, 2])
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    work = args.work.resolve()
    if args.summarize:
        summarize(work)
        return
    tasks = [
        (case, variant, repeat)
        for repeat in args.repeats
        for case in CASES
        if case.name in args.cases
        for variant in args.variants
    ]
    for case in {case for case, _, _ in tasks}:
        source_repo(work, case, args.source.resolve())
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(run_case, work, case, variant, repeat, args.source.resolve())
            for case, variant, repeat in tasks
        ]
        for future in futures:
            future.result()
    summarize(work)


if __name__ == "__main__":
    main()
