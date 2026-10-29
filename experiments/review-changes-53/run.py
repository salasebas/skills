"""Run the paired, read-only review experiment from issue #53."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = "0f44728f67333468fa1dcba2b7e54b928c260825"
MODEL = "gpt-6.1-sol"


@dataclass(frozen=True)
class Case:
    name: str
    repository: str
    base: str
    head: str


CASES = (
    Case(
        "scope",
        "mastodon",
        "d4944a24676e9b9e9fe419cb7661d9b2c0c9d77f",
        "ba536ea867afa7f281648b0dd8d63e09d3d6cf54",
    ),
    Case(
        "ownership",
        "mastodon",
        "3211e960ac793b1b9431a7eea40b385272f1a2a6",
        "89d3c22a40eb2c09b353470175f057f1a3aa3553",
    ),
    Case(
        "small",
        "better-auth-rb",
        "f8721cec3bd9ed55cb68d10659f31c29173d5f68",
        "61fa967ebc5d35ad30241bc5c707d2321f8add8f",
    ),
    Case(
        "medium",
        "ports",
        "bbb785244600b719cb576a219477979b2358e2c2",
        "31b234c30d9aec825f09936bdd164f86fb12abc9",
    ),
)


def command(*args: str, cwd: Path | None = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def planted(work: Path) -> Case:
    repo = work / "planted"
    if repo.exists():
        return Case(
            "planted",
            "planted",
            command("git", "rev-parse", "HEAD^", cwd=repo),
            command("git", "rev-parse", "HEAD", cwd=repo),
        )
    repo.mkdir()
    command("git", "init", "-q", cwd=repo)
    command("git", "config", "user.email", "benchmark@example.invalid", cwd=repo)
    command("git", "config", "user.name", "Review benchmark", cwd=repo)
    write(
        repo / "AGENTS.md",
        command("git", "show", f"{CANDIDATE}:rules/AGENTS.md", cwd=ROOT) + "\n",
    )
    write(
        repo / "requirements.md",
        "# Order processing\n\nShipping costs 5 for standard and 15 for express. Unknown modes must be rejected.\nEvery supported status must appear in the dashboard. A new cancelled status is needed.\nKeep the existing shipping prices. Add a local pickup fee calculator.\n",
    )
    write(
        repo / "orders.py",
        'from enum import StrEnum\n\n\nclass Status(StrEnum):\n    PENDING = "pending"\n    PAID = "paid"\n\n\ndef shipping(mode: str) -> int:\n    match mode:\n        case "standard":\n            return 5\n        case "express":\n            return 15\n        case _:\n            raise ValueError(mode)\n\n\ndef dashboard(status: Status) -> str:\n    match status:\n        case Status.PENDING:\n            return "Awaiting payment"\n        case Status.PAID:\n            return "Ready to ship"\n    raise ValueError(status)\n',
    )
    write(
        repo / "test_orders.py",
        'import unittest\n\nfrom orders import shipping\n\n\nclass ShippingTest(unittest.TestCase):\n    def test_standard_price(self) -> None:\n        self.assertEqual(shipping("standard"), 5)\n',
    )
    operations = []
    for index in range(110):
        operations.append(
            f"def region_{index}_fee(subtotal: int, weight: int) -> int:\n    if subtotal < 0:\n        raise ValueError(subtotal)\n    if weight < 0:\n        raise ValueError(weight)\n    return subtotal * {index + 1} // 100 + weight\n\n\n\n"
        )
    write(repo / "fees.py", "".join(operations))
    command("git", "add", ".", cwd=repo)
    command("git", "commit", "-qm", "Order processing baseline", cwd=repo)
    base = command("git", "rev-parse", "HEAD", cwd=repo)
    orders = (
        (repo / "orders.py")
        .read_text()
        .replace('    PAID = "paid"', '    PAID = "paid"\n    CANCELLED = "cancelled"')
        .replace(
            "            return 5",
            "            # Return the standard shipping price.\n            return 7",
        )
        .replace("            raise ValueError(mode)", "            return 7")
    )
    write(
        repo / "orders.py",
        orders
        + "\n\ndef shipping_cost(mode: str) -> int:\n    return shipping(mode)\n",
    )
    write(
        repo / "test_orders.py",
        (repo / "test_orders.py").read_text().replace("), 5)", "), 7)"),
    )
    write(
        repo / "fees.py",
        (repo / "fees.py").read_text()
        + "def pickup_fee(subtotal: int, parcels: int) -> int:\n    if subtotal < 0:\n        raise ValueError(subtotal)\n    if parcels < 0:\n        raise ValueError(parcels)\n    if parcels == 0:\n        return 0\n    if subtotal >= 100:\n        return 0\n    return parcels * 2\n",
    )
    command("git", "add", ".", cwd=repo)
    command("git", "commit", "-qm", "Add cancelled orders and pickup fees", cwd=repo)
    with (repo / "fees.py").open("a") as fees:
        fees.write(
            "\n\ndef gift_wrap_fee(items: int) -> int:\n    if items < 0:\n        raise ValueError(items)\n    if items == 0:\n        return 0\n    return items * 3\n"
        )
    command("git", "add", "fees.py", cwd=repo)
    command("git", "commit", "--amend", "--no-edit", "-q", cwd=repo)
    truth = {
        "comment": "orders.py narrates the standard-price return; Comments rule.",
        "wrapper": "shipping_cost only forwards to shipping; direct-code rule.",
        "fallback": "unknown shipping mode silently returns 7 despite requirements; explicit-case rule.",
        "enum": "CANCELLED is added but dashboard rejects it; consumer-completeness rule.",
        "size": "fees.py grows from 990 to 1008 lines; about-1000 boundary, synthetic source caveat.",
        "test": "standard price changes 5 to 7 and expected value follows, against requirements; Tests rule.",
    }
    write(work / "planted-truth.json", json.dumps(truth, indent=2) + "\n")
    return Case(
        "planted", "planted", base, command("git", "rev-parse", "HEAD", cwd=repo)
    )


def prepare(work: Path, case: Case, variant: str) -> Path:
    run = work / "runs" / f"{case.name}-{variant}"
    if run.exists():
        raise FileExistsError(f"Refusing to overwrite {run}")
    home = run / "home"
    codex_home = home / ".codex"
    codex_home.mkdir(parents=True)
    auth = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
    shutil.copyfile(auth, codex_home / "auth.json")
    (codex_home / "auth.json").chmod(0o600)
    write(
        codex_home / "AGENTS.md",
        command("git", "show", f"{CANDIDATE}:rules/AGENTS.md", cwd=ROOT) + "\n",
    )
    skill = home / ".agents/skills/review-changes"
    skill.mkdir(parents=True)
    for relative in (
        "SKILL.md",
        "references/bugs.md",
        "references/instructions.md",
        "references/loop.md",
    ):
        write(
            skill / relative,
            command(
                "git", "show", f"{CANDIDATE}:skills/review-changes/{relative}", cwd=ROOT
            )
            + "\n",
        )
    if variant == "B":
        original = (skill / "SKILL.md").read_text()
        start = original.index("3. Review the change,")
        end = original.index("4. Record findings", start)
        replacement = '3. Start exactly two fresh-context subagents in parallel (`fork_turns: "none"`), using `gpt-6.1-sol` at `high` effort. Give both the same scope, base, head, project instructions, and this skill folder. One follows only `references/bugs.md`; the other follows only `references/instructions.md`. They review read-only, do not delegate further, and return findings with code evidence. Wait for both before continuing.\n'
        write(skill / "SKILL.md", original[:start] + replacement + original[end:])
    command(
        "git",
        "worktree",
        "add",
        "--detach",
        str(run / "repo"),
        case.head,
        cwd=work / case.repository,
    )
    command(
        "git", "diff", "--no-ext-diff", f"{case.base}...{case.head}", cwd=run / "repo"
    )
    command(
        "git",
        "--no-lazy-fetch",
        "diff",
        "--no-ext-diff",
        f"{case.base}...{case.head}",
        cwd=run / "repo",
    )
    return run


def run_case(work: Path, case: Case, variant: str) -> dict[str, object]:
    run = prepare(work, case, variant)
    home = run / "home"
    env = dict(os.environ, HOME=str(home), CODEX_HOME=str(home / ".codex"))
    instructions = f"Read-only benchmark. Read only the current repository and {home}/.agents/skills/review-changes, plus your loaded instructions. Use shell only for git read commands (diff, show, status, log, grep, rev-parse, ls-files), rg, fd, ls, head, cat, wc, and sed -n. Do not execute project code, tests, scripts, interpreters, network commands, web tools, or edits. Do not inspect other runs, parent directories, history outside this scope, benchmark answers, or PR discussions. Report any unavailable validation under Not checked."
    args = [
        "codex",
        "--no-daemon",
        "-a",
        "never",
        "-s",
        "read-only",
        "-c",
        'model_reasoning_effort="high"',
        "-c",
        'web_search="disabled"',
        "-c",
        "features.plugins=false",
        "-c",
        "features.remote_plugin=false",
        "-c",
        "features.apps=false",
        "-c",
        "features.memories=false",
        "-c",
        f"features.multi_agent={'true' if variant == 'B' else 'false'}",
        "-c",
        f"features.multi_agent_v2.enabled={'true' if variant == 'B' else 'false'}",
        "-c",
        f"agents.enabled={'true' if variant == 'B' else 'false'}",
        "-c",
        'agents.default_subagent_model="gpt-6.1-sol"',
        "-c",
        'agents.default_subagent_reasoning_effort="high"',
        "-c",
        "developer_instructions=" + json.dumps(instructions),
        "exec",
        "--ignore-user-config",
        "--skip-git-repo-check",
        "-m",
        MODEL,
        "--json",
        "-C",
        str(run / "repo"),
        "-o",
        str(run / "report.md"),
        f"Review the changes in HEAD against {case.base}. Use the review-changes skill.",
    ]
    write(
        run / "invocation.json",
        json.dumps(
            {"case": asdict(case), "variant": variant, "command": args}, indent=2
        )
        + "\n",
    )
    started = time.time()
    print(f"START {case.name}-{variant}", flush=True)
    with (
        (run / "events.jsonl").open("w") as output,
        (run / "stderr.log").open("w") as error,
    ):
        result = subprocess.run(
            args,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=error,
            timeout=2400,
            check=False,
        )
    events = [
        json.loads(line) for line in (run / "events.jsonl").read_text().splitlines()
    ]
    read_succeeded = any(
        event.get("item", {}).get("type") == "command_execution"
        and event["item"].get("exit_code") == 0
        for event in events
    )
    record = {
        "case": case.name,
        "variant": variant,
        "exit_code": result.returncode,
        "seconds": round(time.time() - started, 3),
        "status": command("git", "status", "--porcelain", cwd=run / "repo"),
        "read_succeeded": read_succeeded,
    }
    write(run / "result.json", json.dumps(record, indent=2) + "\n")
    print(f"DONE {case.name}-{variant} {record}", flush=True)
    return record


def summarize(work: Path) -> None:
    rows = []
    for run in sorted((work / "runs").iterdir()):
        if not (run / "result.json").exists():
            continue
        row = json.loads((run / "result.json").read_text())
        sessions = []
        usage = dict.fromkeys(
            (
                "input_tokens",
                "cached_input_tokens",
                "output_tokens",
                "reasoning_output_tokens",
                "total_tokens",
            ),
            0,
        )
        for rollout in sorted((run / "home/.codex/sessions").rglob("*.jsonl")):
            events = [json.loads(line) for line in rollout.read_text().splitlines()]
            meta = next(
                item["payload"] for item in events if item["type"] == "session_meta"
            )
            contexts = [
                item["payload"] for item in events if item["type"] == "turn_context"
            ]
            counts = [
                item["payload"]["info"]["total_token_usage"]
                for item in events
                if item["type"] == "event_msg"
                and item["payload"].get("type") == "token_count"
                and item["payload"].get("info")
            ]
            if counts:
                for key in usage:
                    usage[key] += counts[-1].get(key, 0)
            spawns = []
            calls = []
            for item in events:
                payload = item.get("payload", {})
                if item["type"] == "response_item" and payload.get("type") in (
                    "function_call",
                    "custom_tool_call",
                ):
                    call = {key: payload.get(key) for key in ("name", "namespace")}
                    call["arguments"] = payload.get("arguments", payload.get("input"))
                    call["timestamp"] = item["timestamp"]
                    calls.append(call)
                    if payload.get("name") == "spawn_agent":
                        spawns.append(json.loads(payload["arguments"]))
            sessions.append(
                {
                    "id": meta["id"],
                    "parent": meta.get("parent_thread_id"),
                    "source": meta.get("source"),
                    "agent_path": meta.get("agent_path", "/root"),
                    "first": events[0]["timestamp"],
                    "last": events[-1]["timestamp"],
                    "models": sorted({context["model"] for context in contexts}),
                    "efforts": sorted(
                        {context.get("effort", "") for context in contexts}
                    ),
                    "usage": counts[-1] if counts else {},
                    "spawns": spawns,
                    "calls": calls,
                    "sha256": hashlib.sha256(rollout.read_bytes()).hexdigest(),
                }
            )
        row["sessions"] = sessions
        row["usage"] = usage
        rows.append(row)
    write(work / "summary.json", json.dumps(rows, indent=2) + "\n")
    for row in rows:
        print(
            row["case"],
            row["variant"],
            row["seconds"],
            len(row["sessions"]),
            row["usage"],
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work", type=Path)
    parser.add_argument(
        "--cases",
        nargs="+",
        default=["scope", "ownership", "planted", "small", "medium"],
    )
    parser.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    work = args.work.resolve()
    if args.summarize:
        summarize(work)
        return
    cases = (*CASES, planted(work))
    tasks = [
        (case, variant)
        for case in cases
        if case.name in args.cases
        for variant in ("A", "B")
    ]
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(run_case, work, case, variant) for case, variant in tasks
        ]
        for future in futures:
            future.result()
    summarize(work)


if __name__ == "__main__":
    main()
