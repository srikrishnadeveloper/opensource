Here’s your **learning roadmap** and what was added to the repo.

## Start here

Open **`opensource/docs/LEARNING.md`** — full study order, glossary, and hands-on exercises. Linked from `README.md` too.

---

## Files to learn (in order)

### 1. Understand the product (15 min)
| File | What you learn |
|------|----------------|
| `README.md` | What Wiki Brain does |
| `wiki/index.md` + `wiki/profile.md` | Real wiki pages, frontmatter, `[[wikilinks]]` |
| `.env.example` | All config variables |
| `examples/mcp-cursor.json` | How Cursor starts the server |

### 2. Core code (main focus) ⭐
| # | File | Start here because… |
|---|------|---------------------|
| 1 | **`mcp-server/sanitize.py`** | Smallest file (~145 lines) — privacy/redaction |
| 2 | **`mcp-server/test_server.py`** | Shows how the engine behaves; run after changes |
| 3 | **`mcp-server/writer.py`** | GitHub saves (only if you use cloud writes) |
| 4 | **`mcp-server/server.py`** | The brain — search, tools, auth (~1500 lines) |

**Inside `server.py`, read in this order:**
1. Configuration → `WIKI_DIR`
2. `WikiPage` + `WikiEngine` → how `.md` becomes searchable data
3. `search()` + `get_page()` → reading
4. `APIKeyMiddleware` → cloud password
5. `@mcp_server.tool()` read tools
6. Write helpers + folder tools
7. `if __name__ == "__main__"` → how it starts

### 3. Deploy (when ready)
| File | Purpose |
|------|---------|
| `requirements.txt` | Python deps (`mcp`, `httpx`) |
| `Dockerfile` | Render container |
| `render.yaml` | Cloud service config |
| `docs/CHATGPT.md`, `docs/GITHUB.md` | Connect ChatGPT + writes |

### Skip for now
- `mcp-server/widgets/` — not connected to current server
- `docs/DEAD_CODE_AUDIT.md`, `ISSUES_TRACKER.md` — internal notes

---

## Comments added for beginners

Search **`# LEARN:`** in these files — plain-English explanations at each important section:

- `server.py` — architecture, engine, auth, tools, entry point
- `writer.py` — why GitHub, SHA, folders, frontmatter
- `sanitize.py` — “start here” file, two privacy layers
- `test_server.py` — how tests work
- `Dockerfile`, `requirements.txt`, `examples/mcp-cursor.json`

---

## First 3 things to do

```powershell
cd opensource
python mcp-server/test_server.py          # 1. See it work
```

Open `wiki/topics/python.md` and add a line — rerun tests.

Open `sanitize.py` and read top to bottom (15 min) — then `server.py` from line 54 (`Wiki Engine`).

---

## One-sentence mental model

**Cursor asks a question → MCP calls a tool in `server.py` → `WikiEngine` searches `wiki/*.md` → `sanitize.py` cleans the answer → text goes back to the AI.**

If you want, next step can be a **walkthrough of one tool** (e.g. trace `search` or `create_page` line-by-line in chat).