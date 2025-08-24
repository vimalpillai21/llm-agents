import os
from dotenv import load_dotenv

load_dotenv(override=True)

market_mcp = {"command": "uv","args": ["run","market_server.py"]}

trader_mcp_server_params = [
    {"command": "uv","args": ["run","accounts_server.py"]},
    {"command": "uv", "args": ["run", "push_server.py"]},
    market_mcp,
]

def researcher_mcp_server_params(name: str):
    playwright_params = {"command": "npx","args": ["-y", "@playwright/mcp@latest"]}

    return [
        {"command": "uvx", "args": ["mcp-server-fetch"]},
        {"command": "npx", "args": ["-y","mcp-memory-libsql"],"env": {"LIBSQL_URL": f"file:./memory/{name}.db"}},
        playwright_params

    ]