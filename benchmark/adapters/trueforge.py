"""Benchmark adapter for TrueForge.

The agent lives on the TrueForge server (agents/trueforge/agent.json, synced with
sync_agent.py). This adapter reaches it by name with the TrueForge Python SDK: one
fresh session per question, one turn.

When the agent calls its built-in ask_user_question tool, the turn emits
tool.response_required and pauses. The adapter answers each pending question with
the simulated user (human.ask) as user.tool_response events on the same turn, then
reads on from where it stopped. Pattern from TrueForge's docs, "Use an agent" § Agent questions:
https://github.com/truefoundry/trueforge/blob/main/docs/api/use-agent.mdx
"""
import json
import os
import time

import httpx
from trueforge_sdk import TrueForge
from trueforge_sdk.events import is_event_delta, merge_event_delta

from common import ROOT

AGENT_FILE = ROOT / "agents" / "trueforge" / "agent.json"
if not AGENT_FILE.exists():
    raise SystemExit("agents/trueforge/agent.json not found: build the agent and export it, or import it (see README)")
AGENT_NAME = json.loads(AGENT_FILE.read_text())["name"]
BASE_URL = os.environ.get("TRUEFORGE_BASE_URL", "http://localhost:8790")
TIMEOUT_S = 600
MAX_PAUSES = 30  # safety cap: HiL-Bench answers at most 2 questions per blocker, 3-5 blockers per task


def text_of(content):
    """Message content is either a string or a list of content parts."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(getattr(part, "text", None) or "" for part in content)
    return ""


def server_version():
    try:
        return httpx.get(f"{BASE_URL}/healthz", timeout=5).json().get("version")
    except Exception:
        return None


class Turn:
    """What the adapter has seen of one turn so far, across the first stream and every resume."""

    def __init__(self):
        self.events = {}         # event id -> full event (deltas merged in), to look up tool calls
        self.turn_id = None
        self.last_event_id = None
        self.pending = []        # tool.response_required events not answered yet
        self.tool_calls = 0

    def read(self, stream):
        """Read until the turn pauses ("paused"), ends (its state) or the stream closes (None)."""
        for event in stream:
            self.last_event_id = event.id
            if is_event_delta(event):
                base = self.events.get(event.id)
                if base is not None:
                    merge_event_delta(base, event)
            else:
                self.events[event.id] = event
            if event.type == "turn.created":
                self.turn_id = event.turn_id
            elif event.type == "tool.response":
                # Counts every tool the harness ran, subagents' included.
                self.tool_calls += 1
            elif event.type == "tool.response_required":
                self.pending.append(event)
            elif event.type == "tool.approval_required":
                raise RuntimeError("turn waiting for a tool approval; the agent should have no approval gates")
            elif event.type == "mcp.auth_required":
                raise RuntimeError("turn waiting for MCP sign-in; sql-tools needs no auth")
            elif event.type == "turn.update" and event.state.status == "paused":
                return "paused"
            elif event.type == "turn.done":
                return event.state
        return None

    def answers(self, human):
        """One user.tool_response per pending ask_user_question call, answered by the simulated user."""
        responses = []
        for pending in self.pending:
            for ref in pending.tool_calls:
                msg = self.events.get(ref.source_event_id)
                call = next((tc for tc in (getattr(msg, "tool_calls", None) or []) if tc.id == ref.id), None)
                if call is None or call.tool_info.type != "truefoundry-system" or call.tool_info.name != "ask_user_question":
                    name = call and f"{call.tool_info.type}/{call.tool_info.name}"
                    raise RuntimeError(f"turn waiting on a tool other than ask_user_question: {name}")
                args = json.loads(call.function.arguments or "{}")
                reply = human.ask(args.get("question", ""), args.get("options"))
                responses.append({"type": "user.tool_response", "thread_id": pending.thread_id,
                                  "tool_call_id": ref.id, "content": reply})
        self.pending = []
        return responses


def run(question, human):
    """Ask the agent one question. Returns the result run.py expects (see its docstring)."""
    client = TrueForge(base_url=BASE_URL, timeout=TIMEOUT_S)
    session = client.sessions.create(agent={"name": AGENT_NAME}).data
    turn = Turn()
    deadline = time.time() + TIMEOUT_S

    with client.sessions.create_turn_stream(
        session_id=session.id,
        input=[{"type": "user.message", "content": question}],
    ) as stream:
        result = turn.read(stream)

    pauses = 0
    # None: the stream closed early; "paused": the agent asked the user. Either way, read on.
    while (result is None or result == "paused") and time.time() < deadline:
        if turn.turn_id is None:
            raise RuntimeError("stream closed before the turn was created")
        with client.sessions.subscribe_to_turn(session_id=session.id, turn_id=turn.turn_id,
                                               after_event_id=turn.last_event_id,
                                               request_options={"timeout": TIMEOUT_S}) as resume:
            if result == "paused":
                pauses += 1
                if pauses > MAX_PAUSES:
                    raise RuntimeError(f"turn paused more than {MAX_PAUSES} times")
                client.sessions.create_turn_events(session_id=session.id, turn_id=turn.turn_id,
                                                   events=turn.answers(human))
            # A closed stream doesn't end the turn (it keeps running on the server), so
            # subscribing again from the last event seen is enough.
            result = turn.read(resume)

    if result is None or result == "paused":
        raise RuntimeError("turn did not finish")
    state = result
    if state.status != "done":
        detail = getattr(state, "message", None) or getattr(state, "reason", "")
        raise RuntimeError(f"turn ended with status {state.status}: {detail}")

    m = state.metrics
    # Largest prompt of any single model call (Haiku 5.5 bills a call over 100k
    # prompt tokens at a higher rate). The live stream doesn't carry per-call usage;
    # the turn's saved events do.
    max_call_input = 0
    for item in client.sessions.list_turn_events(session_id=session.id, turn_id=turn.turn_id):
        event = getattr(item, "event", item)
        if event.type == "model.message" and event.usage:
            max_call_input = max(max_call_input, event.usage.input_tokens)
    return {
        "answer": text_of(state.output.content if state.output else None),
        # TrueForge reports input as the total, with cache reads and writes inside it.
        "tokens": {
            "input": (m and m.total_input_tokens) or 0,
            "output": (m and m.total_output_tokens) or 0,
            "cache_read": (m and m.total_cache_read_tokens) or 0,
            "cache_write": (m and m.total_cache_write_tokens) or 0,
        },
        "tool_calls": turn.tool_calls,
        "max_call_input": max_call_input or None,
        "session_id": session.id,
        "harness_version": f"trueforge {server_version()}",
        "features": {"pauses": pauses},
        # Only set when the model endpoint reports a cost (a gateway); empty on a direct provider.
        "cost_usd": m.total_cost_in_usd if m else None,
    }
