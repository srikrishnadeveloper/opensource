I went through every ID in `DEAD_CODE_AUDIT.md` and checked it against the code. Here is the impact verdict: **what you can delete without losing usefulness** vs **what would break or weaken the product**.

---

## Short answer

**Yes — you can delete a focused subset (~30 items) with zero loss of current MCP behavior** (search, read, write, memory, status, graph, demo wiki, 39/39 tests).

**No — you must not delete whole tools, resources, transport paths, or “redundant” APIs** listed as RD/DORMANT/FP. That would break real users (ChatGPT archives, Neon memory, SSE, `move_page`, etc.).

**Several INC items are already broken** — deleting them makes things worse; they need **fixes**, not removal.

---

## Tier 1 — Safe to delete (no functionality loss today)

These are truly unused or cosmetic. Removing them does **not** change what the MCP server does for Cursor, ChatGPT, or the demo wiki.

| ID | What | Damages functionality? |
|----|------|------------------------|
| **DC-001** | `import httpx`, `import json` in `server.py` | **No** — never used |
| **DC-002** | Inner `import base64` in `append_to_page` (line 1274) | **No** — duplicate of line 47 |
| **DC-003** | `_rebuild_engine()` | **No** — nothing calls it today (you’d re-add it if you build `reload_wiki`) |
| **DC-004** | `safe_body()`, `safe_excerpt()`, `contains_secrets()` in `sanitize.py` | **No** for this repo — server never calls them |
| **DC-005** | `_fmt_dt()`, `MemoryStore.delete()`, `MemoryStore.count()` | **No** for current MCP — no tool uses them |
| **DC-006** | FTS index line in `SCHEMA_SQL` | **No** — search uses `ILIKE`, not FTS |
| **DC-007** | Unused `title` param on `extract_page_meta()` | **No** — if you update call sites |
| **DC-008** | `include_meta=False` branch in `_build_page()` | **No** — no caller uses `False` |
| **DC-009** | `WikiPage.word_count` field | **No** — set but never read |
| **DC-010** | Stale comment “reload_wiki removed” | **No** — comment only |
| **DC-011** | `/health`, `/healthz` in `_OPEN_PATHS` set | **No** — already handled earlier in middleware |
| **DC-012** | Wrong module docstring (lines 1–45) | **No** — **replace**, don’t leave empty |
| **DC-018** | `datetime` import (with `_fmt_dt`) | **No** — only used by dead `_fmt_dt` |
| **DC-019** | `source` in SQL SELECT (if you stop fetching it) | **No** — MCP already drops it in `_memory_to_dict` |
| **DC-021** | Extra blank lines | **No** |
| **DC-025** | `__pycache__/widgets.cpython-312.pyc` | **No** — orphan bytecode |
| **DC-026** | `GitHubWriter.self.repo` | **No** — only `self.base` is used |
| **DC-028** | Unused OCEAN regex capture group 1 | **No** — simplify regex only |
| **DC-030** | Wrap test scripts in `if __name__` | **No** — improves scripts, doesn’t change server |
| **LB-001** | Local `__pycache__/` | **No** — regenerated on run |
| **DC-017** | `wiki/images/_index.json` | **N/A** — file not on disk |
| **ST-001–ST-022** | Wrong page counts, stale doc refs, docstrings | **No** — docs/comments only (**fix** text, don’t delete features) |

**Optional DC-005 note:** Removing `MemoryStore.close()` only matters on process exit (tiny pool leak). **No user-visible feature loss.**

---

## Tier 2 — Safe only with care (minor / future / ops impact)

| ID | What | Damages functionality? |
|----|------|------------------------|
| **DC-013** | Remove duplicate `body` or `summary` in `get_personality` | **Yes, if you remove one key** — MCP clients may read both. Keep both or treat as API break |
| **DC-014** | Remove test scripts from Docker / delete files | **No** for running MCP on Render. **Yes** for local dev/testing if you delete the files |
| **DC-015** | Stop copying `test_*.py` into Docker image | **No** for production MCP — **yes** if you rely on tests inside the container |
| **DC-016** | Drop `requests` / delete `_test_write.py` | **No** for server — **yes** for cloud write smoke tests |
| **DC-024** | Remove lazy import in `create_page` | **Don’t delete the import** — **move** it to top; deleting breaks `create_page` |
| **DC-027** | Stop writing `word_count` / `summary` into frontmatter in `writer.py` | **No** for MCP read tools. **Maybe** for people editing markdown outside MCP (Obsidian, git diff). Safer to **keep** writer metadata |
| **DC-029** | Remove manual `frontmatter={}` on `create_page` | **Don’t blindly delete** — **replace** with parse from `full_content`; blind delete can break in-memory page state |
| **DC-020** | Drop `metadata` DB column | **No** today. **Yes** later if you want rich memory metadata |
| **DC-022** | Remove static `source` string in `get_personality` | **Changes API shape** — clients may use it; **fix** to dynamic list instead of delete |
| **RD-001** | Merge duplicate `_WIKILINK_RE` | **No** if refactor is correct — **yes** if import breaks |
| **RD-008** | Merge duplicate READMEs | **No** for server — docs only |
| **LB-002** | Add `.dockerignore` | **No** — improves builds |

---

## Tier 3 — Do NOT delete (would break or gut the product)

### Whole MCP tools / APIs

| ID | What | If you delete… |
|----|------|----------------|
| **RD-002** | `move_page` tool | Breaks `tools/list` and any client/LLM using `move_page` |
| **RD-003** | `wiki://index`, `wiki://status`, `wiki://personality` resources | Breaks MCP resource clients |
| **RD-004** | `get_stats` or `get_status` | Breaks whichever tool you remove |
| **RD-005** | `search_prompts` | Breaks users with `wiki/chatgpt/` or `wiki/copilot/` |
| **RD-006** | `list_folders` | Loses a simple folder-only tool (LLM ergonomics) |
| **RD-012** | SSE transport (`--sse`, `sse_app`) | Breaks `MCP_TRANSPORT=sse` deployments |
| **RD-010** | `_git_pull` / `WIKI_AUTO_PULL` | Breaks local auto-sync when `WIKI_AUTO_PULL=1` |
| **RD-011** | `asyncpg` from requirements | Breaks `remember` / `recall` / `list_memories` when Neon is configured |
| **DM-005** | Write tools (`create_page`, etc.) | Core feature for GitHub-backed wiki |
| **DM-006** | Memory tools | Core optional feature for Neon users |
| **FP-001** | `resource_*` handlers | **Not dead** — framework calls them by URI |
| **FP-002** | `WikiPage.content` | Breaks `get_people`, `resource_index` (`safe_content`) |
| **FP-003** | `is_private()` / private-folder rules | Breaks privacy for `secrets/`, `private/` wikis |

### “Redundant” logic you must keep

| ID | What | Why keep |
|----|------|----------|
| **RD-007** | Double `_build_page` in `create_page` | One path is GitHub, one is local disk sync — removing either breaks sync |
| **RD-009** | Personality pages list (`psychology`, `traits`, …) | Idle in demo; **required** for full personal wikis |
| **RD-013** | `source` / `metadata` columns | Defaults work today; removing schema needs migration |
| **RD-014** | `strength: 1` on graph links | Removing changes graph JSON contract |
| **RD-015–018** | Duplicate summaries / filesystem rescan | Refactor only — deleting breaks `get_status` / tool responses |
| **RD-017** | `summary` + structured fields on tools | LLMs rely on `summary` strings — **do not remove** |
| **RD-019** | `sources:` in wiki frontmatter | Not used by engine; **human traceability** — deleting from wiki pages loses info, not MCP |
| **RD-020** | `created` vs `created_at` | **Don’t delete** — **align** conventions when fixing |
| **RD-021** | Different `tags[:4]` vs `[:6]` | Cosmetic; unifying is safe, deleting tag output is not |
| **RD-022** | Mixed str vs dict tools | **API break** if you force one shape |

### Dormant in demo but needed in production

| ID | What |
|----|------|
| **DM-001** | `search_prompts` |
| **DM-002** | OCEAN parsing |
| **DM-003** | Extra personality pages |
| **DM-004** | `WIKI_AUTO_PULL` |
| **DM-007** | SSE |
| **DM-008** | HTTP auth middleware |
| **DM-009** | MCP resources |
| **DM-010** | `get_people` |
| **DM-011** | Private-page sanitization |

---

## Tier 4 — Do NOT delete — fix instead (already hurts usefulness)

| ID | Problem | If you delete the code… |
|----|---------|-------------------------|
| **INC-001** | `update_page` doesn’t refresh `wikilinks` | `get_graph` / search stay wrong until restart — **worse** |
| **INC-002** | `rename_page` drops `wikilinks` | Same |
| **INC-003** | `create_page` frontmatter dict wrong | In-memory page state wrong |
| **INC-004** | `append_to_page` corrupts `page.body` | Same-session reads wrong after append |
| **INC-005** | Incomplete index cleanup on delete/rename | Search/name_map wrong |

Deleting these code paths would remove write features entirely; the fix is to **correct** them (ideally using `_rebuild_engine()` or proper re-indexing).

---

## Tier 5 — DC-023 (common mistake)

**DC-023** is “repeated `if get_writer is None`” — that is **not** dead code. Removing those guards would make write tools crash or misbehave when `GITHUB_TOKEN` is unset. **Only refactor into a helper; do not delete.**

---

## Recommended “safe cleanup batch” (won’t make it less useful)

If you want maximum cleanup with **zero** feature loss for current users:

1. DC-001, DC-002, DC-003, DC-004, DC-005 (`_fmt_dt`, `delete`, `count` only), DC-006, DC-007, DC-008, DC-009  
2. DC-010, DC-011, DC-012 (rewrite docstring), DC-018, DC-019, DC-021, DC-025, DC-026, DC-028  
3. LB-001, DC-015 (don’t copy tests into Docker)  
4. ST-001–ST-012 (fix wiki counts / index nav text)  
5. **Do not touch:** RD-002–006, RD-011–012, DM-*, FP-*, INC-*, write tools, memory tools, resources  

After that batch: **39/39 tests should still pass** and all 19 MCP tools + 3 resources behave the same.

---

## Bottom line

| Category | Count | Delete safely? |
|----------|------:|:--------------:|
| **DC-001 – DC-012, DC-018–021, DC-025–026, DC-028, DC-030** | ~20 | **Yes** |
| **STALE (ST-*)** | 18 | **Yes** (edit text only) |
| **LB-001** | 1 | **Yes** |
| **DC-013, DC-014, DC-015, DC-027, DC-029** | 5 | **Only with care** |
| **All RD-*, DM-*, FP-*** | 34+ | **No** |
| **INC-001 – INC-005** | 5 | **Fix, don’t delete** |

The audit is right that a **~115-line dead-code strip** is safe. It is **wrong to treat the whole document as a delete list** — about half the entries are “redundant but intentional,” “dormant for demo,” or “broken and needs fixing.”

I can apply **only the Tier 1 safe batch** in code next if you want.