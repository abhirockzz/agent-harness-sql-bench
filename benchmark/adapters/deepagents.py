"""Benchmark adapter for Deep Agents.

Deep Agents is a library, so there is no server to call by name: the adapter
imports build_agent() from agents/deepagents/agent.py and runs the agent here.

When the agent calls ask_user_question, the run stops with an interrupt. The
adapter answers each pending call with the simulated user (human.ask) as a
"respond" decision and resumes on the same thread, until the run ends without one.
Pattern from the Deep Agents human-in-the-loop docs, § Handle interrupts:
https://docs.langchain.com/oss/python/deepagents/human-in-the-loop
"""
import asyncio
import importlib.metadata
import sys
import uuid

from langchain_core.callbacks import BaseCallbackHandler, UsageMetadataCallbackHandler
from langgraph.types import Command

from common import ROOT

sys.path.insert(0, str(ROOT))
from agents.deepagents.agent import ASK_TOOL, build_agent  # noqa: E402

MAX_PAUSES = 30  # safety cap, as in the TrueForge adapter


class RunStats(BaseCallbackHandler):
    """Counts every tool the agent runs, subagents' included (like TrueForge's count),
    and keeps the largest prompt of any single model call (Haiku 5.5 bills a call over
    100k prompt tokens at a higher rate). ask_user_question never runs, so it isn't counted."""

    def __init__(self):
        self.tool_calls = 0
        self.subagent_calls = 0
        self.max_call_input = 0

    def on_tool_start(self, serialized, *args, **kwargs):
        self.tool_calls += 1
        if (serialized or {}).get("name") == "task":  # Deep Agents' subagent tool
            self.subagent_calls += 1

    def on_llm_end(self, response, **kwargs):
        for gens in response.generations:
            for g in gens:
                usage = getattr(getattr(g, "message", None), "usage_metadata", None) or {}
                self.max_call_input = max(self.max_call_input, usage.get("input_tokens", 0))


def cache_writes(details):
    """Cache-write tokens from LangChain's input_token_details.

    When Anthropic splits writes by cache lifetime, langchain-anthropic puts them in
    ephemeral_5m_input_tokens / ephemeral_1h_input_tokens and sets cache_creation to 0
    (so they aren't counted twice). Read the split first, cache_creation otherwise.
    """
    split = (details.get("ephemeral_5m_input_tokens") or 0) + (details.get("ephemeral_1h_input_tokens") or 0)
    return split or details.get("cache_creation") or 0


def decisions_for(interrupt, human):
    """One "respond" decision per pending ask_user_question call, in order."""
    decisions = []
    for action in interrupt.value["action_requests"]:
        if action["name"] != ASK_TOOL["name"]:
            raise RuntimeError(f"run paused on a tool other than {ASK_TOOL['name']}: {action['name']}")
        args = action.get("args") or {}
        decisions.append({"type": "respond", "message": human.ask(args.get("question", ""), args.get("options"))})
    return {"decisions": decisions}


async def ask(question, human):
    agent = await build_agent()
    # Callbacks see every model call and tool run, including inside subagents,
    # which the final message list doesn't. They add up across resumes.
    usage, stats = UsageMetadataCallbackHandler(), RunStats()
    # Resuming needs the same thread id.
    config = {"configurable": {"thread_id": str(uuid.uuid4())}, "callbacks": [usage, stats]}

    step = {"messages": [{"role": "user", "content": question}]}
    pauses = 0
    while True:
        result = await agent.ainvoke(step, config=config)
        interrupts = result.get("__interrupt__")
        if not interrupts:
            break
        pauses += 1
        if pauses > MAX_PAUSES:
            raise RuntimeError(f"run paused more than {MAX_PAUSES} times")
        if len(interrupts) == 1:
            step = Command(resume=decisions_for(interrupts[0], human))
        else:
            # Several pending at once (e.g. parallel subagents): answer each by its id.
            step = Command(resume={i.id: decisions_for(i, human) for i in interrupts})

    tokens = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    for u in usage.usage_metadata.values():
        details = u.get("input_token_details") or {}
        # LangChain reports input as the total, with cached tokens inside it.
        tokens["input"] += u.get("input_tokens", 0)
        tokens["output"] += u.get("output_tokens", 0)
        tokens["cache_read"] += details.get("cache_read", 0) or 0
        tokens["cache_write"] += cache_writes(details)

    return {
        "answer": result["messages"][-1].text,
        "tokens": tokens,
        "tool_calls": stats.tool_calls,
        "max_call_input": stats.max_call_input,
        # Runs in-process, so there's no harness session; an id keeps rows distinct.
        "session_id": f"deepagents-{config['configurable']['thread_id'][:8]}",
        "harness_version": f"deepagents {importlib.metadata.version('deepagents')}",
        "features": {"pauses": pauses, "subagent_calls": stats.subagent_calls},
        "cost_usd": None,
    }


def run(question, human):
    return asyncio.run(ask(question, human))
