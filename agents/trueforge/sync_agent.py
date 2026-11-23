"""Copy the TrueForge agent between the server and agent.json.

TrueForge's UI (0.185.1) has no export or import for agents, so this uses the Python SDK.

    uv run agents/trueforge/sync_agent.py export sql-analyst
        server -> agent.json (the agent you built in the UI, by name)
    uv run agents/trueforge/sync_agent.py import
        agent.json -> server (creates the agent, or updates it if the name exists).
        Also registers the MCP servers in settings.toml as connectors (the UI's
        Settings -> Connectors), since the agent attaches them by name
    uv run agents/trueforge/sync_agent.py check
        compare agent.json with settings.toml

All three then check agent.json against the shared settings in settings.toml.
"""
import argparse
import json
import os
import pathlib
import sys

from trueforge_sdk import RemoteMcpServerManifest, TrueForge

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parents[1]
DEFINITION = HERE / "agent.json"
sys.path.insert(0, str(ROOT / "benchmark"))
from common import SETTINGS, mcp_servers  # noqa: E402  (also loads .env)


def client():
    return TrueForge(base_url=os.environ.get("TRUEFORGE_BASE_URL", "http://localhost:8790"))


def find_agent(tf, name):
    """agents.get takes the agent's id, so look the name up first (the filter is a substring match)."""
    return next((a for a in tf.agents.list(agent_name=name) if a.name == name), None)


def export(name):
    tf = client()
    agent = find_agent(tf, name)
    if agent is None:
        sys.exit(f"no agent named {name!r} on the server")
    agent = tf.agents.get(agent_id=agent.id).data
    definition = {
        "name": agent.name,
        "description": agent.description,
        "manifest": agent.manifest.dict(exclude_none=True),
    }
    DEFINITION.write_text(json.dumps(definition, indent=2) + "\n")
    print(f"wrote {DEFINITION.relative_to(ROOT)} from agent {agent.name} ({agent.id})")


def import_():
    definition = json.loads(DEFINITION.read_text())
    tf = client()
    for name, url in mcp_servers().items():
        tf.settings.mcp_servers.create_or_update(manifest=RemoteMcpServerManifest(
            name=name, url=url, description="Read-only SQL access to the task databases, plus a search over their business notes"))
        print(f"registered MCP server {name} at {url}")
    existing = find_agent(tf, definition["name"])
    if existing is None:
        agent = tf.agents.create(name=definition["name"], description=definition["description"],
                                 manifest=definition["manifest"]).data
        print(f"created agent {agent.name} ({agent.id})")
    else:
        agent = tf.agents.update(agent_id=existing.id, description=definition["description"],
                                 manifest=definition["manifest"]).data
        print(f"updated agent {agent.name} ({agent.id}) to match agent.json")


def check():
    """Print where agent.json differs from settings.toml. Returns True if it matches."""
    settings = SETTINGS["agent"]
    manifest = json.loads(DEFINITION.read_text())["manifest"]
    problems = []

    # TrueForge names models <provider>/<model>, with dots turned into dashes.
    want_model = f"{settings['provider']}/" + settings["model"].replace(".", "-")
    model = manifest.get("model", {})
    if model.get("name") != want_model:
        problems.append(f"model is {model.get('name')!r}, settings say {want_model!r}")
    effort = (model.get("params") or {}).get("reasoning_effort")
    if effort != settings["reasoning_effort"]:
        problems.append(f"reasoning effort is {effort!r}, settings say {settings['reasoning_effort']!r}")

    # The use case depends on the agent asking the user (the built-in ask_user_question tool).
    if not (manifest.get("config", {}).get("ask_user_questions") or {}).get("enabled", True):
        problems.append("ask user questions is off; turn it on")

    want_prompt = (ROOT / settings["system_prompt"]).read_text().strip()
    if (manifest.get("instructions") or "").strip() != want_prompt:
        problems.append(f"instructions differ from {settings['system_prompt']}")

    servers = {s["name"]: s for s in manifest.get("mcp_servers", [])}
    for name in settings["mcp_servers"]:
        server = servers.get(name)
        if server is None:
            problems.append(f"MCP server {name!r} is not attached")
            continue
        enabled = server.get("enable_tools", ["@all"])
        if not server.get("preload"):
            # Other harnesses send every tool schema up front; TrueForge defaults to discovering them.
            problems.append(f"{name}: preload is off")
        # @write / @destructive (TrueForge's default) only gate tools the server labels that
        # way; a run that does pause stops with a clear error. @all or a named enabled tool
        # would pause every run, so only those count.
        approval = server.get("require_approval_for_tools", [])
        gated = [t for t in approval if t == "@all" or t in enabled]
        if gated:
            problems.append(f"{name}: tools need approval {gated}; the benchmark runs unattended")
    for name in servers.keys() - settings["mcp_servers"].keys():
        problems.append(f"extra MCP server {name!r} not in settings")

    for p in problems:
        print(f"  mismatch: {p}")
    print("agent.json matches settings.toml" if not problems else f"{len(problems)} mismatch(es) with settings.toml")
    return not problems


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("export").add_argument("name", help="agent name on the server")
    sub.add_parser("import")
    sub.add_parser("check")
    args = parser.parse_args()

    if args.cmd == "export":
        export(args.name)
    elif args.cmd == "import":
        import_()
    ok = check()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
