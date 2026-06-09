# Wiki Brain — Agent Instructions

This file mirrors `CLAUDE.md` for tools that discover `AGENTS.md` automatically (Cursor, Copilot, Claude Code).

## Project

**Wiki Brain** — MCP server that indexes a folder of markdown wiki pages and exposes them to AI clients (Cursor, Claude Desktop, ChatGPT).

## Key paths

| Path | Purpose |
|------|---------|
| `mcp-server/server.py` | MCP server entry point |
| `wiki/` | Markdown knowledge base |
| `CLAUDE.md` | Wiki maintenance schema |
| `docs/` | Setup guides |

## When editing

- Keep `wiki/` free of secrets and government IDs in the public fork.
- Run `python mcp-server/test_server.py` after wiki or engine changes.
- Write tools need `GITHUB_TOKEN` + `GITHUB_REPO` — see `docs/GITHUB.md`.

## Demo vs production

This repo ships a **demo wiki** (fictional Alex Dev). Replace `wiki/` with your own vault for personal use.
