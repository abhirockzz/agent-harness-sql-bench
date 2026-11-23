"""Write the Claude Managed Agents agent file from its template, then sync it with `ant apply`.

    uv run agents/claude-managed-agents/apply.py --dry-run    # show the plan, change nothing
    uv run agents/claude-managed-agents/apply.py              # apply (asks y/n in a terminal)
    uv run agents/claude-managed-agents/apply.py --yes        # apply without asking

`ant apply` sends files as written; it doesn't fill in environment variables. So the
agent's committed file is a template (agent.template.md), and this script writes the
real one to build/agent.md (git-ignored) with:
  - the sql-tools URL: MCP_PUBLIC_URL from .env, so your ngrok domain stays out of git
  - the ask_user_question custom tool: shared/ask_user_question.json, the same tool
    TrueForge has built in and Deep Agents gets as a stub
  - the system prompt: shared/system.md
It checks the model and effort against settings.toml, then runs
`ant apply build/agent.md environment.yaml` with any arguments you pass. ant reads
ANTHROPIC_API_KEY from this script's environment, which includes .env.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "benchmark"))
from common import SETTINGS  # noqa: E402  (also loads .env)

TEMPLATE = HERE / "agent.template.md"
BUILT = HERE / "build" / "agent.md"
ENVIRONMENT = HERE / "environment.yaml"


def render():
    """The agent file's text: the template with the URL, ask tool and system prompt filled in."""
    url = os.environ.get("MCP_PUBLIC_URL", "")
    if not url.startswith("https://"):
        # Anthropic's cloud can't reach localhost.
        sys.exit("Set MCP_PUBLIC_URL in .env to the tunnel's public URL first (see the README, section 1)")

    _, frontmatter, _ = TEMPLATE.read_text().split("---\n", 2)
    agent = yaml.safe_load(frontmatter)
    settings = SETTINGS["agent"]

    problems = []
    if agent["model"]["id"] != settings["model"]:
        problems.append(f"model is {agent['model']['id']!r}, settings say {settings['model']!r}")
    if agent["model"]["effort"] != settings["reasoning_effort"]:
        problems.append(f"effort is {agent['model']['effort']!r}, settings say {settings['reasoning_effort']!r}")
    if problems:
        sys.exit("agent.template.md differs from settings.toml: " + "; ".join(problems))

    (server,) = [s for s in agent["mcp_servers"] if s["name"] == "sql-tools"]
    server["url"] = url

    ask = json.loads((ROOT / "shared" / "ask_user_question.json").read_text())
    agent["tools"].append({"type": "custom", "name": ask["name"],
                           "description": ask["description"], "input_schema": ask["input_schema"]})

    system = (ROOT / settings["system_prompt"]).read_text().strip()
    header = "# Written by apply.py from agent.template.md. Don't edit; edit the template.\n"
    return f"---\n{header}{yaml.safe_dump(agent, sort_keys=False, allow_unicode=True, width=1000)}---\n\n{system}\n"


def main():
    BUILT.parent.mkdir(exist_ok=True)
    BUILT.write_text(render())
    print(f"wrote {BUILT.relative_to(ROOT)}", flush=True)
    # Run from the folder that holds claude-lock.json, with paths relative to it.
    cmd = ["ant", "apply", *sys.argv[1:], str(BUILT.relative_to(ROOT)), str(ENVIRONMENT.relative_to(ROOT))]
    sys.exit(subprocess.run(cmd, cwd=ROOT).returncode)


if __name__ == "__main__":
    main()
