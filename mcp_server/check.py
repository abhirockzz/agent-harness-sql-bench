"""Call every tool on the running MCP server once per task database, as an agent would.

    uv run mcp_server/server.py      # in another terminal
    uv run mcp_server/check.py

Also runs each task's ground-truth SQL through execute_sql.
"""
import asyncio
import sys
from pathlib import Path

from fastmcp import Client

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmark"))
from common import DATASET, mcp_servers, task_info, tasks  # noqa: E402

# The local URL, or the public one when MCP_PUBLIC_URL is set (checks the tunnel too).
URL = mcp_servers()["sql-tools"]


def text(result):
    return "\n".join(getattr(c, "text", "") for c in result.content)


async def main():
    async with Client(URL) as client:
        tools = await client.list_tools()
        print("server:", URL)
        print("tools:", ", ".join(t.name for t in tools))
        for task in tasks():
            db = task_info(task)["database"]
            tables = (await client.call_tool("get_database_info", {"database_name": db})).data
            table = next(iter(tables))
            info = (await client.call_tool("get_table_info", {"database_name": db, "table_name": table})).data
            col = await client.call_tool("get_column_info",
                                         {"database_name": db, "table_name": table, "column_name": info["columns"][0]})
            notes = text(await client.call_tool("get_business_info",
                                                {"database_name": db, "search_string": "how is this term defined"}))
            sql = (DATASET / task / "ground_truth.sql").read_text()
            rows = text(await client.call_tool("execute_sql", {"database_name": db, "query": sql}))
            print(f"\n== {task}: {len(tables)} tables; {table}: {len(info['columns'])} columns; "
                  f"{info['columns'][0]}: {col.data}")
            print(f"   notes: {notes.splitlines()[0][:100]}  ({len(notes.splitlines())} returned)")
            print(f"   ground truth: {rows[:160]!r}")
        bad = text(await client.call_tool("execute_sql", {"database_name": "nope", "query": "SELECT 1"}))
        write = text(await client.call_tool("execute_sql", {"database_name": task_info(tasks()[0])["database"],
                                                            "query": "DELETE FROM loan"}))
        print(f"\nunknown database: {bad}\nwrite attempt: {write}")


if __name__ == "__main__":
    asyncio.run(main())
