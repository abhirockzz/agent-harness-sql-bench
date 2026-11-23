"""Run every task through an agent, several trials each.

    uv run benchmark/run.py trueforge
    uv run benchmark/run.py trueforge --trials 1
    uv run benchmark/run.py trueforge --trials 1 --task 18-financial
    uv run benchmark/run.py all

Each agent is reached through its adapter, benchmark/adapters/<name>.py. One run is
one (agent, trial, task) cell; finished cells are skipped, so a stopped run resumes.
Answers go to results/<agent>/t<trial>/<task>.md, metrics to results/matrix.jsonl.

The runner creates the simulated user (human.py) for each run and hands it to the
adapter, which calls human.ask() whenever its harness pauses to ask the user. So the
user is the same for every harness, and its questions and answers are recorded here.

What an adapter's run(question, human) returns, a dict with:
- answer: the agent's final reply
- tokens: {input, output, cache_read, cache_write}, where input is the total, with
  cache reads and writes inside it (aggregate.py prices the uncached part separately)
- tool_calls: tools the harness ran, not counting ask_user_question
and, where the harness reports them: model, max_call_input (largest prompt of one
model call), session_id, harness_version, runtime_s (billed running time),
features (e.g. pauses, subagent calls, compactions) and cost_usd (cross-check only).
"""
import argparse
import importlib
import json
import pathlib
import subprocess
import sys
import time

from common import DATASET, MATRIX, RESULTS, ROOT, SETTINGS, read_jsonl, tasks
from human import Human

BENCH = SETTINGS["benchmark"]
ADAPTERS = sorted(p.stem for p in (ROOT / "benchmark" / "adapters").glob("*.py") if p.stem != "__init__")


def git_commit():
    """The repo version a run used, so results can be tied back to the code."""
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "."], cwd=ROOT,
                               capture_output=True, text=True).stdout.strip()
        return sha + ("-dirty" if dirty else "")
    except Exception:
        return None


def done_cells():
    return {(r["agent"], r["trial"], r["task"]) for r in read_jsonl(MATRIX) if r["status"] == "ok"}


def run_cell(agent, trial, task, commit):
    """Run one task, retrying on timeout, crash or empty answer. Appends one line to matrix.jsonl."""
    out = RESULTS / f".cell_{agent}_t{trial}_{task}.json"
    label = f"[{agent} t{trial} {task}]"

    for attempt in range(1, BENCH["max_attempts"] + 1):
        out.unlink(missing_ok=True)
        t0 = time.time()
        try:
            # A separate process per run, so a hung or crashed agent can be killed
            # without stopping the benchmark.
            subprocess.run([sys.executable, __file__, "_one", agent, task, str(out)], cwd=ROOT,
                           timeout=BENCH["task_timeout_s"])
        except subprocess.TimeoutExpired:
            print(f"  {label} timeout, attempt {attempt}", flush=True)
            continue
        latency = round(time.time() - t0, 1)
        if not out.exists():
            print(f"  {label} crashed, attempt {attempt}", flush=True)
            time.sleep(5 * attempt)
            continue
        res = json.loads(out.read_text())
        out.unlink()
        if not res.get("answer", "").strip():
            print(f"  {label} empty answer, attempt {attempt}", flush=True)
            time.sleep(5 * attempt)
            continue

        answer_dir = RESULTS / agent / f"t{trial}"
        answer_dir.mkdir(parents=True, exist_ok=True)
        (answer_dir / f"{task}.md").write_text(res["answer"])
        row = {"agent": agent, "trial": trial, "task": task, "status": "ok",
               # The model the harness reports it ran, else the one settings.toml names (for
               # TrueForge, sync_agent.py check confirms the server agent uses it).
               "model": res.get("model") or SETTINGS["agent"]["model"],
               "max_call_input": res.get("max_call_input"),
               "latency_s": latency, "tool_calls": res["tool_calls"], "tokens": res["tokens"],
               "answer_chars": len(res["answer"]), "session_id": res.get("session_id"),
               "harness_version": res.get("harness_version"), "git_commit": commit,
               "runtime_s": res.get("runtime_s"),   # billed running time, if the harness charges for it
               "features": res.get("features"),     # harness features that fired, if the adapter reports them
               "human": res["human"],               # questions asked, blockers resolved, matcher tokens
               "cost_usd": res.get("cost_usd")}   # harness-reported cost, cross-check only
        with open(MATRIX, "a") as f:
            f.write(json.dumps(row) + "\n")
        h = row["human"]
        print(f"  {label} ok  {latency}s  tools={row['tool_calls']}  "
              f"asked={h['questions']}  resolved={len(h['blockers_resolved'])}/{h['n_blockers']}", flush=True)
        return

    with open(MATRIX, "a") as f:
        f.write(json.dumps({"agent": agent, "trial": trial, "task": task, "status": "failed",
                            "git_commit": commit}) + "\n")
    print(f"  {label} FAILED after {BENCH['max_attempts']} attempts", flush=True)


def run_agent(agent, trials, only=None):
    done = done_cells()
    commit = git_commit()
    for trial in range(1, trials + 1):
        for task in [only] if only else tasks():
            if (agent, trial, task) in done:
                print(f"skip {agent} t{trial} {task}", flush=True)
                continue
            run_cell(agent, trial, task, commit)


def run_one(agent, task, out):
    """Worker for one cell: call the adapter and write its result as JSON."""
    question = (DATASET / task / "prompt.txt").read_text().strip()
    human = Human(task)
    result = importlib.import_module(f"adapters.{agent}").run(question, human)
    result["human"] = human.metrics()
    pathlib.Path(out).write_text(json.dumps(result))


def main():
    if sys.argv[1:2] == ["_one"]:
        run_one(*sys.argv[2:5])
        return

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("agent", choices=[*ADAPTERS, "all"])
    parser.add_argument("--trials", type=int, default=BENCH["trials"])
    parser.add_argument("--task", choices=tasks(), help="run this task only")
    args = parser.parse_args()

    agents = ADAPTERS if args.agent == "all" else [args.agent]
    for agent in agents:
        # Load each adapter once up front, so a setup error (e.g. a missing agent
        # definition) stops here instead of being retried on every task.
        importlib.import_module(f"adapters.{agent}")
    RESULTS.mkdir(exist_ok=True)
    for agent in agents:
        run_agent(agent, args.trials, args.task)


if __name__ == "__main__":
    main()
