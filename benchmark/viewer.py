"""Write one static HTML page that shows a results folder: results/index.html.

    uv run benchmark/viewer.py
    RESULTS_DIR=published-results uv run benchmark/viewer.py

Run it after grade.py. The page has the summary per harness, a task x harness grid of
passes, and for each run: the questions the agent asked, the simulated user's answers
and the gap each one matched, the graded SQL, the verdict and the agent's final reply.
No server and nothing to install: open the file in a browser.
"""
import html
import json
import sqlite3
import statistics

from aggregate import human_cost, mean, run_cost
from common import DATA, DATASET, GRADES, MATRIX, RESULTS, SETTINGS, read_jsonl, task_info

NAMES = {"trueforge": "TrueForge", "deepagents": "Deep Agents", "claude_managed_agents": "Claude Managed Agents"}
OUT = RESULTS / "index.html"
HUB = "https://hub.harborframework.com"
DATASET_URL = f"{HUB}/datasets/scale-ai/hil-bench-sql-ask-human"
# What each database holds, in one line (from its table descriptions and contents), and
# our own rough difficulty label for its task (HiL-Bench has none).
ABOUT = {
    "financial": ("easy", "A Czech bank: clients, accounts, cards, loans and 1M transactions (1993–1998), by district"),
    "thrombosis_prediction": ("easy", "A hospital's patients with collagen diseases: patient records, 14k lab results, and antibody exams with thrombosis outcomes"),
    "california_schools": ("medium", "California public schools: school directory, enrolment and free-meal counts, and SAT scores"),
    "codebase_community": ("easy", "A Stack Exchange Q&A site on statistics (2009–2014): users, posts, comments, votes and badges"),
    "formula_1": ("medium", "Formula 1, 1950–2017: drivers, teams, circuits, races, results, standings and lap times"),
}

CSS = """
:root { --bg:#fff; --fg:#1d1d1f; --muted:#6e6e73; --line:#e3e3e8; --card:#f6f6f8;
        --pass:#1a7f37; --pass-bg:#dafbe1; --fail:#b42318; --fail-bg:#fee4e2; --code:#f2f2f5; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#161618; --fg:#ececf0; --muted:#9a9aa2; --line:#2e2e33; --card:#1f1f23;
          --pass:#4ac26b; --pass-bg:#12321c; --fail:#ff7b72; --fail-bg:#3d1714; --code:#232328; }
}
* { box-sizing: border-box; }
body { margin: 0 auto; max-width: 1100px; padding: 24px 16px 64px; background: var(--bg); color: var(--fg);
       font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
h1 { font-size: 1.6rem; margin: 0 0 4px; } h2 { margin-top: 40px; border-bottom: 1px solid var(--line); padding-bottom: 6px; }
h3 { margin: 20px 0 8px; } .muted { color: var(--muted); }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-variant-numeric: tabular-nums; }
th, td { border-bottom: 1px solid var(--line); padding: 6px 8px; text-align: left; vertical-align: top; }
th { font-weight: 600; } .wrap { overflow-x: auto; }
.badge { display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 12px; font-weight: 600;
         text-decoration: none; margin-right: 4px; }
.PASS { color: var(--pass); background: var(--pass-bg); } .FAIL, .UNGRADED { color: var(--fail); background: var(--fail-bg); }
details { background: var(--card); border: 1px solid var(--line); border-radius: 8px; margin: 8px 0; padding: 8px 12px; }
summary { cursor: pointer; } pre { background: var(--code); padding: 10px; border-radius: 6px; overflow-x: auto;
       white-space: pre-wrap; word-break: break-word; font-size: 13px; }
.facts { display: flex; flex-wrap: wrap; gap: 6px 18px; margin: 4px 0 10px; }
.facts span b { font-weight: 600; } 
.q { border-left: 3px solid var(--line); padding: 2px 0 2px 10px; margin: 8px 0; }
"""


def esc(x):
    return html.escape(str(x if x is not None else ""))


def pre(text):
    return f"<pre>{esc(text)}</pre>"


def load():
    rows = [r for r in read_jsonl(MATRIX) if r["status"] == "ok"]
    grades = {(g["agent"], g["trial"], g["task"]): g for g in read_jsonl(GRADES)}
    return rows, grades


def summary_table(rows, grades, agents):
    out = ["<div class=wrap><table><tr><th>Harness</th><th>Pass</th><th>Avg cost per run</th>"
           "<th>Cost per pass</th><th>Avg tokens</th><th>Avg tool calls</th><th>Median latency</th>"
           "<th>Questions per run</th><th>Gaps answered</th><th>Simulated user per run</th></tr>"]
    for agent in agents:
        rs = [r for r in rows if r["agent"] == agent]
        passes = sum(grades.get((agent, r["trial"], r["task"]), {}).get("verdict") == "PASS" for r in rs)
        cost = sum(run_cost(r) for r in rs)
        gaps = sum(len(r["human"]["blockers_resolved"]) for r in rs)
        n_gaps = sum(r["human"]["n_blockers"] for r in rs)
        out.append(
            f"<tr><td>{esc(NAMES.get(agent, agent))}</td><td>{passes}/{len(rs)}</td>"
            f"<td>${cost / len(rs):.4f}</td><td>{'$%.4f' % (cost / passes) if passes else '–'}</td>"
            f"<td>{mean([r['tokens']['input'] + r['tokens']['output'] for r in rs]) / 1000:.0f}k</td>"
            f"<td>{mean([r['tool_calls'] for r in rs]):.1f}</td>"
            f"<td>{statistics.median(r['latency_s'] for r in rs):.0f}s</td>"
            f"<td>{mean([r['human']['questions'] for r in rs]):.1f}</td><td>{gaps}/{n_gaps}</td>"
            f"<td>${mean([human_cost(r) for r in rs]):.4f}</td></tr>")
    out.append("</table></div>")
    return "".join(out)


def run_id(agent, trial, task):
    return f"run-{agent}-t{trial}-{task}"


def grid(rows, grades, agents, tasks):
    out = ["<div class=wrap><table><tr><th>Task</th>"
           + "".join(f"<th>{esc(NAMES.get(a, a))}</th>" for a in agents) + "</tr>"]
    for task in tasks:
        out.append(f"<tr><td><a href='#task-{esc(task)}'>{esc(task)}</a></td>")
        for agent in agents:
            cells = []
            for r in sorted((r for r in rows if r["agent"] == agent and r["task"] == task), key=lambda r: r["trial"]):
                v = grades.get((agent, r["trial"], task), {}).get("verdict", "UNGRADED")
                cells.append(f"<a class='badge {v}' href='#{run_id(agent, r['trial'], task)}'>t{r['trial']} {v}</a>")
            out.append(f"<td>{''.join(cells) or '–'}</td>")
        out.append("</tr>")
    out.append("</table></div><p class=muted>Click a cell to open that run.</p>")
    return "".join(out)


def database_facts(database):
    """Tables and size of a task's database (data/<database>/), or None if it isn't extracted."""
    files = list((DATA / database).glob("*.sqlite"))
    if not files:
        return None
    with sqlite3.connect(f"file:{files[0]}?mode=ro", uri=True) as db:
        tables = [t for (t,) in db.execute("select name from sqlite_master where type='table'")
                  if not t.startswith("sqlite_")]
    return len(tables), files[0].stat().st_size / 1e6


def task_section(task, rows, grades, agents):
    info = task_info(task)
    database = info["database"]
    blockers = json.loads((DATASET / task / "blockers.json").read_text())["blockers"]
    level, about = ABOUT.get(database, ("", ""))
    answer_rows = len((DATASET / task / "golden_output.csv").read_text().strip().splitlines()) - 1
    db = database_facts(database)
    facts = [f"<b>Database</b> <code>{esc(database)}</code>"
             + (f" ({db[0]} tables, {db[1]:.0f} MB)" if db else ""),
             f"<b>Difficulty</b> {esc(level)}" if level else "",
             f"<b>Gaps</b> {len(blockers)}",
             f"<b>Answer</b> {answer_rows} row{'s' if answer_rows != 1 else ''}",
             f"<b>Source</b> <a href='{HUB}/tasks/scale-ai/hil-bench-sql_{int(info['hil_bench_task'])}-ask_human'>"
             f"HiL-Bench task #{esc(info['hil_bench_task'])}</a>"]
    out = [f"<h2 id='task-{esc(task)}'>{esc(task)}</h2>",
           f"<p>{esc(about)}</p>" if about else "",
           "<div class='facts muted'>" + "".join(f"<span>{f}</span>" for f in facts if f) + "</div>",
           pre((DATASET / task / "prompt.txt").read_text().strip()),
           "<details><summary>Gaps and their answers, and the answer key</summary><table>"
           "<tr><th>Gap</th><th>What's missing</th><th>The user's answer</th></tr>"]
    for b in blockers:
        out.append(f"<tr><td><code>{esc(b['id'])}</code></td><td>{esc(b['description'])}</td>"
                   f"<td>{esc(b['resolution'])}</td></tr>")
    out.append("</table><h3>Ground-truth SQL</h3>" + pre((DATASET / task / "ground_truth.sql").read_text().strip())
               + "<h3>Golden output</h3>" + pre((DATASET / task / "golden_output.csv").read_text().strip())
               + "</details>")
    for agent in agents:
        for r in sorted((r for r in rows if r["agent"] == agent and r["task"] == task), key=lambda r: r["trial"]):
            out.append(run_details(r, grades.get((agent, r["trial"], task), {})))
    return "".join(out)


def run_details(r, grade):
    agent, trial, task = r["agent"], r["trial"], r["task"]
    v = grade.get("verdict", "UNGRADED")
    h = r["human"]
    head = (f"<span class='badge {v}'>{v}</span> <b>{esc(NAMES.get(agent, agent))}</b> trial {trial} "
            f"<span class=muted>· {h['questions']} questions · {len(h['blockers_resolved'])}/{h['n_blockers']} gaps answered "
            f"· {r['tool_calls']} tool calls · {r['latency_s']:.0f}s · ${run_cost(r):.4f}</span>")
    out = [f"<details id='{run_id(agent, trial, task)}'><summary>{head}</summary>"]
    if grade.get("error"):
        out.append(f"<p><b>Grader:</b> {esc(grade['error'])}</p>")
    out.append("<h3>Questions</h3>" if h["log"] else "<p>No questions asked.</p>")
    for i, q in enumerate(h["log"], 1):
        matched = f"<code>{esc(q['blocker'])}</code>" if q.get("blocker") else "<b>no gap (refused)</b>"
        options = f"<div class=muted>Options: {esc(' | '.join(q['options']))}</div>" if q.get("options") else ""
        out.append(f"<div class=q><div><b>Q{i}.</b> {esc(q['question'])}</div>{options}"
                   f"<div><b>Answer</b> (matched {matched}): {esc(q['response'])}</div></div>")
    out.append("<h3>Graded SQL</h3>" + (pre(grade["sql"]) if grade.get("sql") else "<p>None found in the reply.</p>"))
    answer = RESULTS / agent / f"t{trial}" / f"{task}.md"
    out.append("<h3>Final reply</h3>" + pre(answer.read_text() if answer.exists() else "(missing)"))
    session = f"Session {esc(r['session_id'])} · " if r.get("session_id") else ""
    out.append(f"<p class=muted>{session}{esc(r.get('harness_version'))} · "
               f"features {esc(json.dumps(r.get('features')))}</p></details>")
    return "".join(out)


def main():
    rows, grades = load()
    agents = sorted({r["agent"] for r in rows}, key=lambda a: list(NAMES).index(a) if a in NAMES else 99)
    tasks = sorted({r["task"] for r in rows})
    matchers = sorted({r["human"]["matcher"] for r in rows})
    # The model each run's simulated user actually used, read from the results.
    human_models = sorted({r["human"]["model"] for r in rows})
    trials = max(r["trial"] for r in rows)
    agent_cfg, human_cfg = SETTINGS["agent"], SETTINGS["human"]
    body = ["<h1>SQL analytics agent: results</h1>",
            f"<p>The same SQL analytics agent on {len(agents)} agent harnesses, {len(tasks)} tasks from "
            f"<a href='{DATASET_URL}'>Scale AI's HiL-Bench SQL</a>, {trials} trial{'s' if trials != 1 else ''} each. Every question "
            f"uses business terms the database doesn't define (the gaps), so the agent has to ask the "
            f"user before writing its query. A simulated business user answers, and a run passes when "
            f"its final SQL returns the same rows as the answer key.</p>",
            f"<div class='facts muted'><span><b>Agent</b> <code>{esc(agent_cfg['model'])}</code>, effort "
            f"{esc(agent_cfg['reasoning_effort'])}, same prompt, tools and ask-user tool on every harness</span>"
            f"<span><b>Simulated user</b> an LLM (<code>{esc(', '.join(human_models))}</code>) standing in for the "
            f"business user. It holds the task's answer to each gap and replies with it when a question is "
            f"about one gap (at most {human_cfg['max_answers_per_blocker']} times per gap); anything else gets "
            f"\"irrelevant question\". Same user on every harness ({esc(', '.join(matchers))} mode, "
            f"<code>benchmark/human.py</code>, ported from HiL-Bench)</span></div>",
            "<h2>Summary</h2>", summary_table(rows, grades, agents),
            "<p class=muted>Cost: agent tokens at list price (plus session runtime on Claude Managed Agents). "
            "The simulated user's cost is shown apart.</p>",
            "<h2>Passes per task</h2>", grid(rows, grades, agents, tasks)]
    body += [task_section(t, rows, grades, agents) for t in tasks]
    OUT.write_text(f"<!doctype html><html lang=en><head><meta charset=utf-8>"
                   f"<meta name=viewport content='width=device-width, initial-scale=1'>"
                   f"<title>Harness results</title><style>{CSS}</style></head><body>{''.join(body)}</body></html>")
    print(f"wrote {OUT.relative_to(RESULTS.parent)}")


if __name__ == "__main__":
    main()
