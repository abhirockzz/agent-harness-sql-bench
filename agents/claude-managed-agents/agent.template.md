---
# The SQL analyst agent on Claude Managed Agents. Anthropic runs the agent loop.
#
# This is a template: apply.py fills in three fields and writes the agent file that
# `ant apply` syncs, build/agent.md (git-ignored):
#   - the sql-tools URL: MCP_PUBLIC_URL from .env (your ngrok domain stays out of git)
#   - the ask_user_question custom tool: shared/ask_user_question.json, as is
#   - the system prompt (the body below the frontmatter): shared/system.md
# Everything else is the agent's configuration, sent as written.
name: sql-analyst
description: Answers business users' questions with SQL over the HiL-Bench databases, asking the user what vague terms mean
model:
  id: claude-haiku-5-5
  effort: medium
mcp_servers:
  - type: url
    name: sql-tools
    url: MCP_PUBLIC_URL  # filled in by apply.py
tools:
  # No agent_toolset_20260401 (it's opt-in): no bash, files, web search or web fetch.
  # Same as TrueForge, which has sandbox and web search off.
  - type: mcp_toolset
    mcp_server_name: sql-tools
    default_config:
      # MCP toolsets default to always_ask (every call waits for approval); this agent runs unattended.
      permission_policy: {type: always_allow}
  # apply.py appends the ask_user_question custom tool here.
multiagent:
  type: multiagent_20261001
  # The agent may hand sub-tasks to copies of itself or to agents it defines:
  # the closest match to TrueForge's dynamic sub-agents and Deep Agents' task tool.
  subagents: {type: enabled}
  # Dynamic workflow runs (many agents in phases) have no match on the other two harnesses.
  workflows: {type: disabled}
---

(apply.py replaces this with shared/system.md)
