"""Paths and settings shared by the benchmark scripts."""
import json
import os
import pathlib
import tomllib

from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

SETTINGS = tomllib.loads((ROOT / "settings.toml").read_text())
DATASET = ROOT / "benchmark" / "dataset"
DATA = ROOT / "data"                   # task databases and business notes (benchmark/prepare.py)
# RESULTS_DIR in the environment sends a run elsewhere (e.g. a smoke test), so results/ stays clean.
RESULTS = ROOT / os.environ.get("RESULTS_DIR", "results")
MATRIX = RESULTS / "matrix.jsonl"      # one line per run: tokens, latency, tool calls, questions
GRADES = RESULTS / "grades.jsonl"      # one line per graded answer: PASS / FAIL


def mcp_servers():
    """MCP server name -> URL, from settings.toml. MCP_PUBLIC_URL in .env replaces the
    sql-tools URL with a public one (the ngrok tunnel; see README), for every harness."""
    servers = dict(SETTINGS["agent"]["mcp_servers"])
    if os.environ.get("MCP_PUBLIC_URL"):
        servers["sql-tools"] = os.environ["MCP_PUBLIC_URL"]
    return servers


def tasks():
    """Every task folder that has a prompt and an answer key."""
    return sorted(p.name for p in DATASET.iterdir()
                  if (p / "prompt.txt").exists() and (p / "ground_truth.sql").exists())


def task_info(task):
    """task.json: the HiL-Bench task number and which database it runs on."""
    return json.loads((DATASET / task / "task.json").read_text())


def read_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
