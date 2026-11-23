"""SQL analytics agent on Deep Agents.

Deep Agents is a library, so the agent is this code: build_agent() connects to the
MCP server, sets up the model and returns the agent. Model, system prompt and MCP
server come from settings.toml; the Anthropic key from .env.

Asking the user: Deep Agents has no built-in ask-user tool, so the agent gets a
stub tool, ask_user_question, with TrueForge's tool name, description and schema
(shared/ask_user_question.json). interrupt_on pauses the run on every call to it,
and the caller answers with a "respond" decision, which the agent receives as the
tool's result; the stub itself never runs. Pattern from the Deep Agents and
LangChain human-in-the-loop docs. Pausing needs a checkpointer.

Try it with one question (you answer in the terminal):

    uv run agents/deepagents/agent.py benchmark/dataset/18-financial/prompt.txt
"""
import asyncio
import json
import pathlib
import sys
import uuid
import warnings

from deepagents import create_deep_agent
from langchain_anthropic import ChatAnthropic
from langchain_core._api import LangChainBetaWarning
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

# langchain.mcp is in beta and warns on import; we use it knowingly.
warnings.filterwarnings("ignore", category=LangChainBetaWarning)
from langchain.mcp import MCPAdapter  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmark"))
from common import SETTINGS as ALL_SETTINGS, mcp_servers  # noqa: E402  (also loads .env)
SETTINGS = ALL_SETTINGS["agent"]
ASK_TOOL = json.loads((ROOT / "shared" / "ask_user_question.json").read_text())


def _not_run(**kwargs):
    # Never called: the interrupt answers in its place. Same text as TrueForge's server-side handler.
    return "This tool requires client-side execution and cannot be run server-side."


ask_user_question = StructuredTool.from_function(
    func=_not_run,
    name=ASK_TOOL["name"],
    description=ASK_TOOL["description"],
    args_schema=ASK_TOOL["input_schema"],
)


async def build_agent():
    tools = []
    for url in mcp_servers().values():
        async with MCPAdapter(url) as adapter:
            # The tools keep their own connection, so they work after this block exits.
            tools += await adapter.list_tools()

    # Native Anthropic client. reasoning_effort is sent as output_config.effort.
    # Prompt caching needs nothing here: create_deep_agent adds Anthropic's
    # prompt-caching middleware itself (main agent and subagents).
    model = ChatAnthropic(
        model=SETTINGS["model"],
        reasoning_effort=SETTINGS["reasoning_effort"],
        timeout=180,
        max_retries=5,
    )
    return create_deep_agent(
        model=model,
        tools=[*tools, ask_user_question],
        system_prompt=(ROOT / SETTINGS["system_prompt"]).read_text(),
        # Every ask pauses the run; the only allowed answer is the user's reply.
        interrupt_on={ASK_TOOL["name"]: {"allowed_decisions": ["respond"]}},
        checkpointer=MemorySaver(),
    )


async def main(prompt_file):
    agent = await build_agent()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    step = {"messages": [{"role": "user", "content": pathlib.Path(prompt_file).read_text()}]}
    while True:
        result = await agent.ainvoke(step, config=config)
        if not result.get("__interrupt__"):
            break
        decisions = []
        for action in result["__interrupt__"][0].value["action_requests"]:
            print(f"\nAgent asks: {action['args'].get('question')}\nOptions: {action['args'].get('options')}")
            decisions.append({"type": "respond", "message": input("Your answer: ")})
        step = Command(resume={"decisions": decisions})
    print(result["messages"][-1].text)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
