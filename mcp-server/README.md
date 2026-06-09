# Wiki Brain MCP Server

Python MCP server — indexes `wiki/*.md`, exposes search/read/write tools to AI clients.

| File | Role |
|------|------|
| `server.py` | FastMCP entry point, WikiEngine, all MCP tools |
| `writer.py` | GitHub Contents API (cloud writes) |
| `sanitize.py` | Secret redaction on every read response |

See the [root README](../README.md) for install, ChatGPT, and Render setup.

## Run locally

```bash
# From repo root
export WIKI_BRAIN_DIR=./wiki   # optional — this is the default
python mcp-server/server.py
```

## Tests

```bash
python mcp-server/test_server.py
```

## Environment

See [`.env.example`](../.env.example) and [docs/GITHUB.md](../docs/GITHUB.md).
