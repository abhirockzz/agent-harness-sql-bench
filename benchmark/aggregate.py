"""Join run metrics with grades into one row per agent.

    uv run benchmark/aggregate.py

Solved is the mean number of tasks passed per trial. Cost is worked out from token
counts times the rates in settings.toml, then averaged per run. Every adapter reports
input tokens as the total, with cache reads and writes inside it (see run.py),
so the uncached part is input - cache_read - cache_write.
The simulated user's cost (its matcher model's tokens) is shown in its own column,
not in $/run. "asked" is questions per run; "resolved" is the share of each task's
blockers that the agent's questions resolved.
Also writes results/summary.csv: passes per (agent, task).
"""
import csv
from collections import defaultdict

from common import GRADES, MATRIX, RESULTS, SETTINGS, read_jsonl


def rates(row):
    """Rates for the model the run used."""
    return SETTINGS["rates"][row["model"]]


def run_cost(row):
    tokens, r = row["tokens"], rates(row)
    cached = tokens["cache_read"] + tokens["cache_write"]
    uncached = max(0, tokens["input"] - cached)
    token_cost = (uncached * r["in"] + tokens["output"] * r["out"]
                  + tokens["cache_read"] * r["cache_read"] + tokens["cache_write"] * r["cache_write"]) / 1e6
    # Billed running time, only for harnesses that charge it (Claude Managed Agents).
    runtime_cost = (row.get("runtime_s") or 0) / 3600 * SETTINGS["rates"]["session_runtime"]["per_hour"]
    return token_cost + runtime_cost


def human_cost(row):
    h = row["human"]
    r = SETTINGS["rates"][h["model"]]
    return (h["tokens"]["input"] * r["in"] + h["tokens"]["output"] * r["out"]) / 1e6


def long_context(row):
    """True if one model call's prompt went over the model's long-context threshold,
    which these list rates don't cover (so the run's cost is understated)."""
    limit = rates(row).get("long_context_above")
    return bool(limit and (row.get("max_call_input") or 0) > limit)


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def main():
    rows = read_jsonl(MATRIX)
    ok = {(r["agent"], r["trial"], r["task"]): r for r in rows if r["status"] == "ok"}
    verdicts = {(g["agent"], g["trial"], g["task"]): g["verdict"] for g in read_jsonl(GRADES)}
    agents = sorted({r["agent"] for r in rows})
    tasks = sorted({r["task"] for r in rows})

    # Every attempted trial starts at 0 passes, so a trial where every run failed
    # still counts in the mean instead of quietly dropping out.
    solved = defaultdict(dict)
    for r in rows:
        solved[r["agent"]].setdefault(r["trial"], 0)
    for (agent, trial, _), v in verdicts.items():
        if v == "PASS" and trial in solved[agent]:
            solved[agent][trial] += 1

    per_agent = defaultdict(lambda: defaultdict(list))
    passes = defaultdict(lambda: defaultdict(list))
    for (agent, trial, task), r in ok.items():
        passes[agent][task].append(verdicts.get((agent, trial, task), "UNGRADED"))
        per_agent[agent]["cost"].append(run_cost(r))
        per_agent[agent]["tokens"].append(r["tokens"]["input"] + r["tokens"]["output"])
        per_agent[agent]["tools"].append(r["tool_calls"])
        per_agent[agent]["latency"].append(r["latency_s"])
        h = r["human"]
        per_agent[agent]["asked"].append(h["questions"])
        per_agent[agent]["resolved"].append(len(h["blockers_resolved"]) / h["n_blockers"])
        per_agent[agent]["human"].append(human_cost(r))

    with open(RESULTS / "summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["agent", "task", "trials", "passes"])
        for agent in agents:
            for task in tasks:
                vs = passes[agent].get(task, [])
                w.writerow([agent, task, len(vs), vs.count("PASS")])

    header = (f"{'agent':22} {'trials':>6} {'solved/' + str(len(tasks)):>9} {'$/run':>8} {'tokens':>8} {'tools':>6} "
              f"{'lat_s':>6} {'asked':>6} {'resolved':>8} {'human$':>8}")
    print("\n" + header)
    print("-" * len(header))
    for agent in agents:
        m = per_agent[agent]
        print(f"{agent:22} {len(solved[agent]):>6} {mean(list(solved[agent].values())):>9.1f} "
              f"{'$' + format(mean(m['cost']), '.4f'):>8} {mean(m['tokens']) / 1e6:>7.2f}M "
              f"{mean(m['tools']):>6.1f} {mean(m['latency']):>6.0f} {mean(m['asked']):>6.1f} "
              f"{mean(m['resolved']):>8.0%} {'$' + format(mean(m['human']), '.4f'):>8}")
    models = sorted({r["model"] for r in ok.values()})
    if len(models) > 1:
        print(f"\nwarning: results mix models {models}; keep one model per results folder")
    matchers = sorted({r["human"]["matcher"] for r in ok.values()})
    print(f"\nsimulated user: {', '.join(matchers)} matcher")
    if len(matchers) > 1:
        print("warning: results mix simulated-user matchers; keep one per results folder")
    long_runs = [k for k, r in ok.items() if long_context(r)]
    if long_runs:
        print(f"\nwarning: {len(long_runs)} run(s) had a model call over the long-context threshold; "
              f"their cost is understated: {long_runs}")
    ungraded = sum(v == "UNGRADED" for a in passes.values() for vs in a.values() for v in vs)
    if ungraded:
        print(f"\n{ungraded} answer(s) not graded yet: run grade.py first")
    print(f"\nwrote {(RESULTS / 'summary.csv').relative_to(RESULTS.parent)}")


if __name__ == "__main__":
    main()
