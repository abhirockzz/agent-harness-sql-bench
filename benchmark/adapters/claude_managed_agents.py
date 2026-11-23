"""Benchmark adapter for Claude Managed Agents.

Anthropic runs the agent loop. The agent and its environment are defined in
agents/claude-managed-agents/ and created with apply.py (which runs `ant apply` and
records their IDs in claude-lock.json). This adapter reaches the agent by that ID with
the Anthropic Python SDK: one fresh session per question.

ask_user_question is a custom tool: Anthropic doesn't run it, the client does. When the
agent calls it, the stream emits agent.custom_tool_use and the session goes idle with
stop_reason requires_action. The adapter answers each call with the simulated user
(human.ask) as a user.custom_tool_result, and the session runs on. Pattern from the
Claude Managed Agents docs, "Session event stream" § Answer tool calls that pause the session:
https://platform.claude.com/docs/en/managed-agents/events-and-streaming
The result may be sent as soon as the tool-use event arrives, so the requires_action
idle that follows needs no action.
"""
import importlib.metadata
import json

import anthropic

from common import ROOT

LOCK_FILE = ROOT / "claude-lock.json"
AGENT_KEY = "./agents/claude-managed-agents/build/agent.md"
ENV_KEY = "./agents/claude-managed-agents/environment.yaml"
ASK_TOOL = json.loads((ROOT / "shared" / "ask_user_question.json").read_text())["name"]
# Hard cap on a session's list cost, in US cents, as a guard against a runaway run
# (under 1 cent per run expected). At the cap the session pauses with budget_reached.
BUDGET_CENTS = "10"
MAX_PAUSES = 30  # safety cap, as in the other adapters
# Tools the harness runs. agent.custom_tool_use (the ask tool) isn't one: the client
# answers it, and Deep Agents doesn't count it either.
TOOL_USE_EVENTS = ("agent.tool_use", "agent.mcp_tool_use")


def lock_ids():
    if not LOCK_FILE.exists():
        raise SystemExit("claude-lock.json not found: create the agent with "
                         "agents/claude-managed-agents/apply.py (see README)")
    resources = json.loads(LOCK_FILE.read_text())["resources"]
    try:
        return resources[AGENT_KEY]["id"], resources[ENV_KEY]["id"]
    except KeyError as e:
        raise SystemExit(f"claude-lock.json has no entry for {e}: run agents/claude-managed-agents/apply.py (see README)")


AGENT_ID, ENV_ID = lock_ids()


def text_of(content):
    return "\n".join(getattr(block, "text", None) or "" for block in content or [])


def thread_stats(client, session_id):
    """Tool calls, model calls and compactions across every thread of the session.

    The session stream shows the primary thread in full but only a condensed view of
    subagent threads (start, end, messages; not their tool or model calls), so each
    thread's own event list is read after the turn.
    """
    stats = {"tool_calls": 0, "max_call_input": 0, "compactions": 0, "subagent_threads": 0,
             "max_tool_result_chars": 0}
    for thread in client.beta.sessions.threads.list(session_id):
        if thread.parent_thread_id:
            stats["subagent_threads"] += 1
        for event in client.beta.sessions.threads.events.list(thread.id, session_id=session_id):
            if event.type in TOOL_USE_EVENTS:
                stats["tool_calls"] += 1
            elif event.type == "span.model_request_end":
                u = event.model_usage
                # Per-call usage counts uncached input only, like the session totals.
                prompt = u.input_tokens + u.cache_read_input_tokens + u.cache_creation_input_tokens
                stats["max_call_input"] = max(stats["max_call_input"], prompt)
            elif event.type == "agent.thread_context_compacted":
                stats["compactions"] += 1
            elif event.type in ("agent.mcp_tool_result", "agent.tool_result"):
                # Outputs over 100,000 characters are moved to a sandbox file; this agent
                # has no file tools to read it back.
                stats["max_tool_result_chars"] = max(stats["max_tool_result_chars"],
                                                     len(text_of(event.content)))
    return stats


def answer_ask(client, session_id, event, human):
    """Answer one ask_user_question call with the simulated user."""
    if event.name != ASK_TOOL:
        raise RuntimeError(f"agent called a custom tool other than {ASK_TOOL}: {event.name}")
    args = event.input or {}
    reply = human.ask(args.get("question", ""), args.get("options"))
    client.beta.sessions.events.send(session_id, events=[{
        "type": "user.custom_tool_result",
        "custom_tool_use_id": event.id,
        "content": [{"type": "text", "text": reply}],
    }])


def run(question, human):
    """Ask the agent one question; human answers its questions. Returns the result run.py expects."""
    client = anthropic.Anthropic()
    session = client.beta.sessions.create(
        agent=AGENT_ID,  # latest version
        environment_id=ENV_ID,
        title="harness-bench-sql",
        budget={"type": "limit", "max_list_cost": {"amount": BUDGET_CENTS, "currency": "USD"}},
    )

    answer, errors, stop, pauses, answered = "", [], None, 0, set()
    # Open the stream before sending the message: it only delivers events from then on.
    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(session.id, events=[
            {"type": "user.message", "content": [{"type": "text", "text": question}]}])
        for event in stream:
            if event.type == "agent.message":
                # The last message of the turn is the answer; earlier ones are notes
                # between tool calls.
                answer = text_of(event.content) or answer
            elif event.type == "agent.custom_tool_use":
                # Also arrives for a subagent's call (cross-posted, session_thread_id set).
                pauses += 1
                if pauses > MAX_PAUSES:
                    raise RuntimeError(f"session {session.id} asked more than {MAX_PAUSES} questions")
                answer_ask(client, session.id, event, human)
                answered.add(event.id)
            elif event.type == "session.error":
                # Retried errors (e.g. a dropped MCP connection) may recover; keep them for the message.
                errors.append(f"{event.error.type}: {event.error.message}")
            elif event.type == "session.status_idle":
                if event.stop_reason.type == "requires_action":
                    # Waiting on calls we've already answered: the session resumes on its own.
                    # Anything else (e.g. a tool approval) would wait forever, so stop.
                    unknown = set(event.stop_reason.event_ids) - answered
                    if unknown:
                        raise RuntimeError(f"session {session.id} waits on events the adapter "
                                           f"doesn't answer: {sorted(unknown)}")
                    continue
                stop = event.stop_reason.type
                break
            elif event.type == "session.status_terminated":
                stop = "terminated"
                break

    if stop != "end_turn":
        # budget_reached: hit BUDGET_CENTS; retries_exhausted / refusal / terminated: failed.
        raise RuntimeError(f"session {session.id} stopped with {stop}; errors: {errors or 'none'}")

    # Totals are final once the session is idle.
    session = client.beta.sessions.retrieve(session.id)
    u = session.usage
    cache_write = ((u.cache_creation.ephemeral_5m_input_tokens or 0)
                   + (u.cache_creation.ephemeral_1h_input_tokens or 0)) if u.cache_creation else 0
    stats = thread_stats(client, session.id)
    return {
        "answer": answer,
        "tokens": {
            # The session reports uncached input only; run.py's result wants the total.
            "input": (u.input_tokens or 0) + (u.cache_read_input_tokens or 0) + cache_write,
            "output": u.output_tokens or 0,
            "cache_read": u.cache_read_input_tokens or 0,
            "cache_write": cache_write,
        },
        "tool_calls": stats["tool_calls"],
        "max_call_input": stats["max_call_input"] or None,
        "session_id": session.id,
        "model": session.agent.model.id,
        "harness_version": (f"claude-managed-agents agent v{session.agent.version}, "
                            f"anthropic {importlib.metadata.version('anthropic')}"),
        # Session running time, billed per session-hour on top of tokens.
        "runtime_s": u.active_seconds,
        # Anthropic's own list-price figure, rounded to whole cents: a cross-check only.
        "cost_usd": int(u.list_cost.amount) / 100 if u.list_cost else None,
        "features": {"pauses": pauses}
                    | {k: stats[k] for k in ("compactions", "subagent_threads", "max_tool_result_chars")}
                    | {"recovered_errors": len(errors)},
    }
