"""Grade answers the way HiL-Bench does: run the agent's SQL and the ground-truth SQL, compare rows.

    uv run benchmark/grade.py            # grade every answer in results/ not graded yet
    uv run benchmark/grade.py --check    # each task's ground_truth.sql must score PASS

The agent's SQL is the last ```sql block in its final reply. Both queries run on the
task's database; the rows are compared with HiL-Bench's own code (hil_verify.py):
row order and column names ignored, duplicate rows collapsed, extra columns allowed,
numbers rounded to 0.01. One line per answer goes to results/grades.jsonl.
"""
import argparse
import json
import re

from common import DATA, DATASET, GRADES, RESULTS, read_jsonl, task_info, tasks
from hil_verify import compare_pandas_outputs, execute_sql, parse_golden_output


def extract_sql(answer):
    """The last ```sql block; failing that, the last ``` block of any kind."""
    blocks = re.findall(r"```sql\s*\n(.*?)```", answer, re.DOTALL | re.IGNORECASE)
    if not blocks:
        blocks = re.findall(r"```[a-z]*\s*\n(.*?)```", answer, re.DOTALL)
    return blocks[-1].strip() if blocks else None


def grade_sql(task, sql):
    """Returns (verdict, error). PASS only if the SQL runs and its rows match the ground truth's."""
    db = DATA / task_info(task)["database"] / "database.sqlite"
    gt_err, gt_df = execute_sql(str(db), (DATASET / task / "ground_truth.sql").read_text().strip())
    if gt_df is None:
        raise RuntimeError(f"{task}: ground truth failed to run: {gt_err}")
    if not sql:
        return "FAIL", "no SQL block in the answer"
    err, df = execute_sql(str(db), sql)
    if df is None:
        return "FAIL", err
    return ("PASS", None) if compare_pandas_outputs(gt_df, df) else ("FAIL", "rows differ from ground truth")


def check():
    """Every ground truth must pass against itself and match its golden_output.csv."""
    ok = True
    for task in tasks():
        sql = (DATASET / task / "ground_truth.sql").read_text().strip()
        verdict, err = grade_sql(task, sql)
        db = DATA / task_info(task)["database"] / "database.sqlite"
        _, gt_df = execute_sql(str(db), sql)
        golden = parse_golden_output((DATASET / task / "golden_output.csv").read_text())
        golden_ok = compare_pandas_outputs(golden, gt_df)
        print(f"{task}: {verdict}, golden output {'matches' if golden_ok else 'DIFFERS'}")
        ok &= verdict == "PASS" and golden_ok
    return ok


def grade_results():
    graded = {(g["agent"], g["trial"], g["task"]) for g in read_jsonl(GRADES)}
    known = set(tasks())
    with open(GRADES, "a") as f:
        for path in sorted(RESULTS.glob("*/t*/*.md")):
            agent, trial, task = path.parts[-3], int(path.parts[-2][1:]), path.stem
            if task not in known or (agent, trial, task) in graded:
                continue
            sql = extract_sql(path.read_text())
            verdict, err = grade_sql(task, sql)
            f.write(json.dumps({"agent": agent, "trial": trial, "task": task, "verdict": verdict,
                                "error": err, "sql": sql}) + "\n")
            print(f"{agent} t{trial} {task}: {verdict}" + (f" ({err})" if err else ""))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="grade each task's ground truth instead")
    args = parser.parse_args()
    if args.check:
        raise SystemExit(0 if check() else 1)
    grade_results()


if __name__ == "__main__":
    main()
