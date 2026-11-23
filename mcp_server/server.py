"""MCP server with HiL-Bench's SQL tools and business-notes search, for every task database.

    uv run mcp_server/server.py          # http://localhost:8800/mcp

Adapted from HiL-Bench's sql_server.py and business_info_server.py (in the task
images under /opt/hil-bench/). Their servers run one per task container, for one
database; this one serves every database in data/, so every tool takes the
database name. Tool names, descriptions and outputs are theirs, except:
- execute_sql also takes database_name
- no submit_sql: the agent ends its reply with the final SQL, and grade.py runs it
- business notes are searched with the same embedding model (all-MiniLM-L6-v2),
  but through Chroma's default ONNX build instead of sentence-transformers (no torch)
- queries time out after 120 seconds (settings.toml [mcp]) instead of 1,200
- queries may only read: statements such as ATTACH or VACUUM INTO, which can create
  files even on a read-only connection, are refused (the server is reachable through the tunnel)
"""
import json
import sqlite3
import sys
import time
from pathlib import Path

import chromadb
import pandas as pd
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from fastmcp import FastMCP

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmark"))
from common import DATA, SETTINGS  # noqa: E402

MAX_ROWS = SETTINGS["mcp"]["max_rows"]
QUERY_TIMEOUT_S = SETTINGS["mcp"]["query_timeout_s"]
N_RESULTS = 5  # business notes returned per search, as in HiL-Bench

mcp = FastMCP("sql-tools")


# Reading tables, functions, recursive CTEs and PRAGMAs is allowed; everything else is refused.
READ_ONLY = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION,
             sqlite3.SQLITE_RECURSIVE, sqlite3.SQLITE_PRAGMA}


def read_only(action, *_):
    return sqlite3.SQLITE_OK if action in READ_ONLY else sqlite3.SQLITE_DENY


def database_dir(database_name):
    path = DATA / database_name
    return path if (path / "database.sqlite").exists() else None


def descriptions(database_name):
    path = database_dir(database_name)
    return path / "database_description" if path else None


@mcp.tool()
def get_database_info(database_name: str) -> dict | str:
    """Retrieves information about a given database in dictionary form. Dictionary keys are table names, dictionary values are their descriptions. If the database doesn't exist, returns an error message."""
    try:
        df = pd.read_csv(descriptions(database_name) / "table_descriptions.csv")
        return dict(zip(df["table_name"], df["table_description"]))
    except (FileNotFoundError, TypeError):
        return f"Error: database {database_name} doesn't exist"


@mcp.tool()
def get_table_info(database_name: str, table_name: str) -> dict | str:
    """Retrieves information about a given table in dictionary form. Includes its description and a list of its columns. If the table doesn't exist, returns an error message."""
    error_msg = f"Error: table {table_name} in database {database_name} doesn't exist"
    folder = descriptions(database_name)
    if folder is None:
        return error_msg
    table_lowered = table_name.lower()
    try:
        df = pd.read_csv(folder / "table_descriptions.csv")
        df_slice = df[df["table_name"] == table_name]
        if len(df_slice) == 0:
            df_slice = df[df["table_name"] == table_lowered]
        info = {"description": df_slice.iloc[0]["table_description"]}
        columns = pd.read_csv(folder / f"{table_lowered}.csv")
    except (FileNotFoundError, IndexError):
        return error_msg
    info["columns"] = columns["original_column_name"].tolist()
    return info


@mcp.tool()
def get_column_info(database_name: str, table_name: str, column_name: str) -> dict | str:
    """Retrieves information about a given column in dictionary form. Includes its description and data type. If the column doesn't exist, returns an error message."""
    error_msg = f"Error: column {column_name} in table {table_name} in database {database_name} doesn't exist"
    folder = descriptions(database_name)
    if folder is None:
        return error_msg
    try:
        df = pd.read_csv(folder / f"{table_name.lower()}.csv")
        df_slice = df[df["original_column_name"] == column_name]
        if len(df_slice) == 0:
            df_slice = df[df["original_column_name"] == column_name.lower()]
        row = df_slice.iloc[0]
    except (FileNotFoundError, IndexError):
        return error_msg
    # pandas reads empty cells as NaN, which isn't valid JSON.
    data_type = row.get("data_format", "")
    return {"description": row["combined_description"], "data_type": "" if pd.isna(data_type) else data_type}


@mcp.tool()
def execute_sql(database_name: str, query: str) -> str:
    """Executes a SQL query against the database and returns the result if query execution is successful, else returns the execution error string. If the result is too large, only the first 200 rows are returned."""
    path = database_dir(database_name)
    if path is None:
        return f"Error: database {database_name} doesn't exist"
    try:
        # Read-only, as in HiL-Bench. A progress handler stops queries that run too long.
        with sqlite3.connect(f"file:{path / 'database.sqlite'}?mode=ro", uri=True) as conn:
            start = time.time()
            conn.set_progress_handler(lambda: time.time() - start > QUERY_TIMEOUT_S, 1000)
            conn.set_authorizer(read_only)
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                if cursor.description is None:
                    return "Error: non-SELECT query"
                columns = [d[0] for d in cursor.description]
                df = pd.DataFrame(cursor.fetchall(), columns=columns)
            except sqlite3.DatabaseError as e:
                message = str(e).lower()
                if "interrupted" in message:
                    return f"Error: query timed out after {QUERY_TIMEOUT_S:g} seconds"
                if any(s in message for s in ("readonly database", "not authorized", "authorization denied")):
                    return "Error: non-SELECT query"
                return f"Error: {e}"
            except Exception as e:
                return f"Error: {e}"
    except Exception as e:
        return f"Error executing query: {e}"
    if df.empty:
        return "Query executed successfully. No results returned."
    if len(df) > MAX_ROWS:
        return (f"Query executed successfully. Result truncated to the first {MAX_ROWS} rows:\n"
                f"{df.head(MAX_ROWS).to_csv(index=False)}")
    return f"Query executed successfully:\n{df.to_csv(index=False)}"


# One in-memory collection of business notes per database, built at startup.
_chroma = chromadb.EphemeralClient()
_embed = DefaultEmbeddingFunction()
_notes = {}


def load_business_info():
    for folder in sorted(p for p in DATA.iterdir() if (p / "business_info.json").exists()):
        data = json.loads((folder / "business_info.json").read_text())
        collection = _chroma.get_or_create_collection(name=f"bi_{folder.name}", embedding_function=_embed)
        collection.add(documents=data["business_info"],
                       ids=[f"bi_{i}" for i in range(len(data["business_info"]))])
        _notes[data["database_name"]] = collection
        print(f"business notes: {data['database_name']} ({len(data['business_info'])})", flush=True)


@mcp.tool()
def get_business_info(database_name: str, search_string: str) -> str:
    """Retrieves UP TO the top 5 semantically similar results to the search string from a knowledge base containing business logic, rules, definitions, etc."""
    if not database_name:
        return "Error querying knowledge base: Missing database_name"
    if not search_string:
        return "Error querying knowledge base: Missing search_string"
    collection = _notes.get(database_name)
    if collection is None:
        return f"No business information found matching '{search_string}'."
    try:
        results = collection.query(query_texts=[search_string], n_results=N_RESULTS)
        docs = (results.get("documents") or [[]])[0] or []
    except Exception as e:
        return f"Error querying knowledge base: {e}"
    if not docs:
        return f"No business information found matching '{search_string}'."
    return "\n".join(f"{i + 1}. {doc.strip()}" for i, doc in enumerate(docs))


if __name__ == "__main__":
    load_business_info()
    mcp.run(transport="http", host="127.0.0.1", port=SETTINGS["mcp"]["port"])
