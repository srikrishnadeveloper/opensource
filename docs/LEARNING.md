# Learn Wiki Brain — beginner path

You built this with AI help. This guide tells you **which files matter** and **in what order** to read them.

## Big picture (30 seconds)

```
You (Cursor / ChatGPT)
        │
        ▼
   MCP protocol  ←── "tools" the AI can call (search, read_page, create_page, …)
        │
        ▼
   server.py     ←── reads wiki/*.md, runs search, talks to GitHub for writes
        │
        ├── wiki/          your markdown notes (the actual knowledge)
        ├── sanitize.py    hides passwords before text goes back to the AI
        └── writer.py      saves changes to GitHub (cloud deploy)
```

**MCP** = Model Context Protocol. A standard way for ChatGPT/Cursor to call functions in your app.

**Wiki** = a folder of `.md` files with optional `[[wikilinks]]` between pages.

---

## Files to learn — in order

Read these top to bottom. Skip audit docs until you understand the code.

### Phase 1 — What the project is (15 min)

| # | File | Why read it |
|---|------|-------------|
| 1 | [`README.md`](../README.md) | Features, install, tool list |
| 2 | [`wiki/index.md`](../wiki/index.md) | Example wiki page + navigation |
| 3 | [`wiki/profile.md`](../wiki/profile.md) | Frontmatter (`title`, `tags`) + body |
| 4 | [`.env.example`](../.env.example) | Every config knob explained |
| 5 | [`examples/mcp-cursor.json`](../examples/mcp-cursor.json) | How Cursor launches the server |

### Phase 2 — Core Python (1–2 hours) ⭐ most important

| # | File | Lines | What you'll learn |
|---|------|-------|-------------------|
| 6 | [`mcp-server/sanitize.py`](../mcp-server/sanitize.py) | ~145 | Privacy: redact secrets, hide private pages |
| 7 | [`mcp-server/test_server.py`](../mcp-server/test_server.py) | ~150 | How the engine is tested; run after changes |
| 8 | [`mcp-server/writer.py`](../mcp-server/writer.py) | ~510 | GitHub API writes (only if you use cloud writes) |
| 9 | [`mcp-server/server.py`](../mcp-server/server.py) | ~1500 | **Main file** — engine, tools, auth, entry point |

**Inside `server.py`, read in this order:**

1. Configuration (`WIKI_DIR`, limits)
2. `WikiPage` + `WikiEngine` (how markdown becomes searchable data)
3. `search()` + `get_page()` (read path)
4. `APIKeyMiddleware` (cloud security)
5. `mcp_server` + read tools (`search`, `read_page`, …)
6. Write helpers (`_index_page_in_engine`, folder validation)
7. Write tools (`create_folder`, `create_page`, …)
8. `if __name__ == "__main__"` (how the process starts)

Look for `# LEARN:` comments — they explain jargon inline.

### Phase 3 — Deploy & connect (30 min)

| # | File | Why |
|---|------|-----|
| 10 | [`mcp-server/requirements.txt`](../mcp-server/requirements.txt) | Python packages (`mcp`, `httpx`) |
| 11 | [`Dockerfile`](../Dockerfile) | How Render builds the container |
| 12 | [`render.yaml`](../render.yaml) | Render service + env vars |
| 13 | [`docs/CHATGPT.md`](CHATGPT.md) | Connect ChatGPT to your deployed URL |
| 14 | [`docs/GITHUB.md`](GITHUB.md) | PAT for write tools |

### Phase 4 — Optional / skip for now

| File | Note |
|------|------|
| `mcp-server/widgets/` | Old UI experiments — **not wired** into current `server.py` |
| `docs/DEAD_CODE_AUDIT.md` | Internal cleanup notes |
| `docs/ISSUES_TRACKER.md` | Known bugs backlog |
| `_test_cloud.py`, `_test_write.py` | Manual tests against live Render URL |

---

## Key words glossary

| Term | Meaning |
|------|---------|
| **stem** | Filename without `.md` — `profile.md` → stem `profile` |
| **folder** | Subdirectory under `wiki/` — e.g. `people`, `topics` |
| **frontmatter** | YAML block at top of `.md` between `---` lines |
| **wikilink** | `[[page-name]]` — link to another wiki page |
| **tool** | One MCP function the AI can call (like an API endpoint) |
| **resource** | Static URI (`wiki://index`) some clients prefetch |
| **stdio** | Server talks over stdin/stdout — used by Cursor locally |
| **streamable-http** | Server is a web URL — used by Render + ChatGPT |

---

## Hands-on exercises

1. **Run tests:** `python mcp-server/test_server.py` — expect all OK.
2. **Start local server:** `python mcp-server/server.py` (stdio — waits for Cursor).
3. **Add a wiki page:** create `wiki/topics/my-note.md`, rerun tests, see page count change.
4. **Trace a read:** search `read_page` in `server.py` → see `get_page` → `sanitize.redact`.
5. **Trace a write:** search `create_page` → `writer.create_wiki_page` → `_index_page_in_engine`.

---

## When you're stuck

- "AI can't find my page" → check stem vs title in `get_page()` ladder
- "Write failed" → `GITHUB_TOKEN` + `GITHUB_REPO` in `.env`
- "401 on Render" → `MCP_API_KEY` must match ChatGPT connector token
