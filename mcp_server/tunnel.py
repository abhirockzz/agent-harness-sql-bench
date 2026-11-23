"""Start the ngrok tunnel to the MCP server, on your fixed ngrok domain.

    uv run mcp_server/tunnel.py

Reads MCP_PUBLIC_URL from .env (e.g. https://<your-domain>.ngrok-free.app/mcp) and runs
`ngrok http 8800 --url https://<your-domain>.ngrok-free.app`. Your domain is listed at
https://dashboard.ngrok.com/domains (free accounts get one). Without --url, ngrok
hands out a different URL on each start.
"""
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmark"))
from common import SETTINGS  # noqa: E402  (also loads .env)

url = os.environ.get("MCP_PUBLIC_URL", "")
parts = urlparse(url)
if parts.scheme != "https" or not parts.netloc:
    sys.exit("Set MCP_PUBLIC_URL in .env first, e.g. https://<your-domain>.ngrok-free.app/mcp "
             "(your domain: https://dashboard.ngrok.com/domains)")
port = str(SETTINGS["mcp"]["port"])
print(f"tunnel: https://{parts.netloc} -> localhost:{port}", flush=True)
# Any extra arguments go to ngrok (e.g. --log stdout).
os.execvp("ngrok", ["ngrok", "http", port, "--url", f"https://{parts.netloc}", *sys.argv[1:]])
