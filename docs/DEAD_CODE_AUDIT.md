# Wiki Brain Open Source — Dead / Redundant Code Audit

**Audit date:** 2026-06-08  
**Pass 3 (line-by-line):** 2026-06-08 — full re-read; §Line-by-line appendix  
**Pass 4 (line-by-line):** 2026-06-08 — re-verified **46 on-disk files** (incl. local `__pycache__`); glob index may show phantom `widgets/` paths — **not on disk**  
**Scope:** All files under `opensource/` — unused, redundant, non-functional, and stale content  
**Rule:** Items in **SAFE TO REMOVE** were verified: deleting them does not break `python mcp-server/test_server.py` (39/39) or normal MCP stdio/cloud paths, unless noted.

Related: [ISSUES_TRACKER.md](ISSUES_TRACKER.md) (bugs/security), [PRIVACY_AUDIT.md](PRIVACY_AUDIT.md) (PII scan).

---

## Summary

| Category | Items | Est. lines removable |
|----------|------:|---------------------:|
| **SAFE TO REMOVE** (dead code) | 28 | ~115 |
| **REDUNDANT** (duplicate / overlap) | 21 | ~140 (if consolidated) |
| **DORMANT** (valid but unused in demo/default) | 13 | 0 (keep for full product) |
| **STALE** (comments/docs/wiki text) | 18 | ~95 lines |
| **LOCAL BLOAT** (gitignored artifacts) | 2 | delete locally |
| **DOCKER / FILE BLOAT** | 3 | 3 files in image |
| **INCOMPLETE** (runs but stale/wrong data) | 5 | fix, don't delete |
| **FALSE POSITIVE** (looks dead, is not) | 3 | do not remove |

---

## SAFE TO REMOVE — dead code (no functionality loss)

These symbols are **defined but never called** from any runtime path in `opensource/`.

### DC-001 — Unused imports in `server.py`

| Lines | Code | Why dead |
|------:|------|----------|
| 50 | `import httpx` | Never referenced; HTTP client lives in `writer.py` only. |
| 51 | `import json` | No `json.` usage anywhere in file. |

**Remove:** 2 lines. **Risk:** None.

---

### DC-002 — Redundant inner `import base64` in `append_to_page`

| Lines | Code | Why redundant |
|------:|------|---------------|
| 47 | `import base64` (module top) | Used here. |
| 1274 | `import base64` (inside `append_to_page`) | Duplicate of top-level import. |

**Remove:** line 1274 only. **Risk:** None.

---

### DC-003 — `_rebuild_engine()` never called

| File | Lines | Definition |
|------|------:|------------|
| `server.py` | 1352–1356 | Rebuilds `WikiEngine` from disk |

Leftover from removed `reload_wiki` admin tool. Writes use partial in-memory patches instead; nothing calls this.

**Remove:** entire function (~5 lines). **Risk:** None today. Re-add if you restore `reload_wiki`.

---

### DC-004 — `sanitize.py` exports never used by server

| Function | Lines | Used in `server.py`? |
|----------|------:|:--------------------:|
| `safe_body()` | 154–159 | No — server uses `redact()` + `safe_content()` |
| `safe_excerpt()` | 170–173 | No — search uses `redact()` on excerpts directly |
| `contains_secrets()` | 176–188 | No — not called anywhere in repo |

**Still used from server:** `redact`, `is_private`, `private_placeholder`, `safe_content`.

**Remove:** 3 functions + module docstring references (~40 lines). **Risk:** None unless external code imports these (none in this repo).

---

### DC-005 — `memory.py` dead helpers and methods

| Symbol | Lines | Why dead |
|--------|------:|----------|
| `_fmt_dt()` | 200–201 | Defined, never called |
| `MemoryStore.delete()` | 148–151 | No MCP tool wraps it |
| `MemoryStore.count()` | 153–156 | Never called |
| `MemoryStore.close()` | 73–76 | Pool never closed on shutdown (leak on exit only) |

**Remove:** `_fmt_dt`, `delete`, `count` (~15 lines). **Keep `close()`** if you add lifespan hook later, or remove if you accept pool-at-exit.

**Risk:** None for MCP tools. Removing `delete` blocks a future `forget_memory` tool unless re-added.

---

### DC-006 — Unused DB index (schema dead weight)

| File | Line | Code |
|------|-----:|------|
| `memory.py` | 46 | `CREATE INDEX ... memories_content_fts ... to_tsvector` |

`MemoryStore.search()` uses `ILIKE`, not FTS. Index is created on every connect but never used.

**Remove:** 1 line from `SCHEMA_SQL`. **Risk:** None for current search behavior.

---

### DC-007 — `extract_page_meta(..., title)` — unused parameter

| File | Line | Issue |
|------|-----:|-------|
| `writer.py` | 197 | Parameter `title` is never read in function body |

**Remove:** parameter from signature + update call sites (pass only `content`). **Risk:** None.

---

### DC-008 — `_build_page(..., include_meta=False)` dead branch

| File | Lines | Issue |
|------|------:|-------|
| `writer.py` | 251, 266, 287 | `include_meta` kwarg exists but **always** defaults to `True`; no caller passes `False` |

**Remove:** parameter and `if include_meta` branches; always include meta. **Risk:** None.

---

### DC-009 — `WikiPage.word_count` field never read

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 102, 158, 166, 1176 | Set on load / create; never read after assignment |

`get_graph` uses `page.size`, not `word_count`. Frontmatter stores word_count separately.

**Remove:** dataclass field + assignments (~4 lines). **Risk:** None.

---

### DC-010 — Stale comment block after removed admin tools

| File | Lines | Content |
|------|------:|---------|
| `server.py` | 1499–1500 | `# reload_wiki and sync_local administrative tools removed` |

**Remove:** comment only. **Risk:** None.

---

### DC-011 — `_OPEN_PATHS` redundant entries (when auth enabled)

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 392, 410–421 | `/health` and `/healthz` returned **before** `_OPEN_PATHS` check; including them in `_OPEN_PATHS` is unreachable when `MCP_API_KEY` is set |

**Remove:** `/health` and `/healthz` from `_OPEN_PATHS` set (keep `/` if intentional). **Risk:** None.

---

### DC-012 — Module docstring header (lines 1–45) documents removed APIs

| File | Lines | Lists tools/resources that **do not exist** |
|------|------:|-----------------------------------------------|
| `server.py` | 1–45 | `get_profile`, `reload_wiki`, `sync_local`, `wiki://profile`, `wiki://stats` |

Not executable code, but misleads maintainers. **Replace** with accurate 19-tool / 3-resource list (see README). **Risk:** None.

---

### DC-013 — `get_personality` duplicate response keys

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 778–779 | `"body"` and `"summary"` assigned **identical** redacted truncated string |

**Remove:** one key (keep `summary` OR `body`) — **breaking change** for clients that read both. Safer: keep both, note as redundant duplicate data (~0 lines unless API cleanup).

---

### DC-014 — Optional test scripts (not imported by server)

| File | Role | In production Docker? |
|------|------|:---------------------:|
| `_test_cloud.py` | Manual Render smoke test | Yes (copied) |
| `_test_write.py` | Manual write round-trip | Yes (copied) |
| `test_server.py` | Unit tests | Yes (copied) |

Not dead for development; **dead weight in Docker image** (see DC-017).

---

## REDUNDANT — duplicate logic or overlapping surface

Removing these **can** break clients or behavior if done without a major version bump.

### RD-001 — Duplicate `_WIKILINK_RE` regex

| Location | Lines |
|----------|------:|
| `server.py` | 86 |
| `writer.py` | 191 |

Identical pattern compiled twice.

**Consolidate:** shared `wiki_util.py` or import from one module. **Risk:** Low if import path correct.

---

### RD-002 — `move_page` is a pure alias of `rename_page`

| File | Lines | Code |
|------|------:|------|
| `server.py` | 1474–1483 | `return await rename_page(name=..., new_folder=..., reason=...)` |

**Remove tool:** breaks MCP `tools/list` contract for any connector that registered `move_page`.  
**Keep:** convenience for LLMs. Mark as redundant wrapper.

---

### RD-003 — MCP tools vs MCP resources overlap

| Tool | Resource | Overlap |
|------|----------|---------|
| `get_status()` | `wiki://status` (`resource_status`) | Resource formats same data as markdown |
| `get_personality()` | `wiki://personality` (`resource_personality`) | Resource = subset of tool output |
| `read_page('index')` | `wiki://index` (`resource_index`) | Same index page |

**Remove resources:** older MCP clients using `wiki://*` URIs break.  
**Remove tools:** ChatGPT/Cursor use tools, not resources. **Keep both** unless you survey clients.

---

### RD-004 — `get_stats()` vs `get_status()` wiki metrics

| Tool | Returns |
|------|---------|
| `get_stats()` | Markdown table: page counts, folder breakdown |
| `get_status()` | JSON: git info + `wiki.total_pages` + folders + changelog + modified files |

~60% overlap on page/folder counts.

**Consolidate:** merge into one tool — **breaking**. Document as intentional (human markdown vs structured status).

---

### RD-005 — `search_prompts()` vs `search(folder=...)`

`search_prompts` = `engine.search(query, folder="chatgpt"|"copilot")` + different output format, **no** privacy redaction (bug in ISSUES_TRACKER SEC-006).

For demo wiki (no `chatgpt/` folder): always empty.

**Remove `search_prompts`:** breaks users with prompt archives. **Redundant** for demo only.

---

### RD-006 — `list_folders()` vs `list_pages()` / `get_folders()`

| API | Output |
|-----|--------|
| `list_folders()` | MCP tool — folder names + counts |
| `list_pages()` | All pages (or by folder) |
| `WikiEngine.get_folders()` | Internal dict used by stats/status |

`list_folders` duplicates data available via `list_pages` aggregation. **Keep** — small tool, LLM-friendly.

---

### RD-007 — `create_page` rebuilds page locally with `_build_page` after GitHub already built it

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 1149–1156 | `writer.create_wiki_page()` already calls `_build_page` on GitHub; server calls `_build_page` again for local copy |

**Redundant work**, not removable without changing writer to return final content. **Risk:** refactor only.

---

### RD-008 — Documentation triple overlap

| File | Overlaps with |
|------|---------------|
| `README.md` | Install, tools table, structure |
| `mcp-server/README.md` | Subset of root README (~80% duplicate) |
| `AGENTS.md` | Mirrors `CLAUDE.md` (intentional per AGENTS line 3) |
| `PRIVACY_AUDIT.md` | Partial overlap with `ISSUES_TRACKER.md` |

**Safe doc cleanup:** merge `mcp-server/README.md` into root with a link; keep AGENTS+CLAUDE pair; refresh PRIVACY_AUDIT references.

---

### RD-009 — `get_personality` / `resource_personality` hardcoded page list

| File | Lines | Looks for stems |
|------|------:|-----------------|
| `server.py` | 748, 1076 | `psychology`, `traits`, `behavior`, `preferences` |

Demo wiki only has `preferences` (and no OCEAN markdown). Three of four names are **always miss** in demo.

**Not dead code** — needed for full personal wikis from `mine/`. **Dormant** in demo (see DORMANT section).

---

### RD-010 — `_git_pull` + `WIKI_AUTO_PULL` vs GitHub write path

Cloud deploy uses GitHub API writes; `git pull` on startup only affects local clone layout. Rarely used on Render (ephemeral FS).

**Redundant** for cloud; **used** for local dev with `WIKI_AUTO_PULL=1`.

---

### RD-011 — `asyncpg` in `requirements.txt` when memory disabled

Always installed; `memory` module optional at runtime via `NEON_DATABASE_URL`.

**Remove dep:** breaks `remember`/`recall` when user adds Neon later unless optional extra. Keep dependency.

---

### RD-012 — SSE transport path vs Render `streamable-http`

| File | Lines | Path |
|------|------:|------|
| `server.py` | 1654–1655, 1666–1677 | `--sse`, `sse_app`, `_secured_sse` |

`render.yaml` / Dockerfile use `streamable-http` only. SSE code is **unused on default deploy** but functional if `MCP_TRANSPORT=sse`.

**Remove:** breaks SSE clients. Mark dormant for Render.

---

### RD-013 — `memory` table columns never set from MCP

| Column | Default | MCP `remember()` sets? |
|--------|---------|:----------------------:|
| `source` | `'chatgpt'` | No — always default |
| `metadata` | `{}` | No — `mem.add()` called without metadata |

Schema supports features with no public API. **Dead feature paths**, not dead schema.

---

### RD-014 — `get_graph` link `strength` always `1`

| File | Line | Value |
|------|-----:|-------|
| `server.py` | 1005 | `"strength": 1` constant |

**Remove field:** minor API shape change for graph consumers.

---

## DORMANT — valid code, inactive in demo / default config

Do **not** remove without product decision.

| ID | What | Why dormant in opensource |
|----|------|---------------------------|
| DM-001 | `search_prompts` | No `wiki/chatgpt/` or `wiki/copilot/` in demo |
| DM-002 | `_extract_ocean()` / `_OCEAN_ROW_RE` | No psychology/traits pages with OCEAN scores in demo |
| DM-003 | `get_personality` loops for `psychology`, `traits`, `behavior` | Only `preferences.md` exists |
| DM-004 | `WIKI_AUTO_PULL` / `_git_pull()` | Default `0` in `.env.example` |
| DM-005 | Write tools (`create_page`, …) | Need `GITHUB_TOKEN`; unset in default local dev |
| DM-006 | Memory tools | Need `NEON_DATABASE_URL` |
| DM-007 | SSE transport | Render uses `streamable-http` |
| DM-008 | `APIKeyMiddleware` | Skipped in stdio mode (Cursor default) |
| DM-009 | `resource_*` MCP resources | Most clients use tools only |
| DM-010 | `get_people('')` → people-index | Works; lightly used in tests |
| DM-011 | `sanitize` private-folder rules | Demo has no `secrets/` or `private/` pages |

---

## STALE — non-code clutter (safe to edit)

| ID | File | Lines | Issue |
|----|------|------:|-------|
| ST-001 | `.env.example` | 18 | Says write tools enable **images** (removed) |
| ST-002 | `wiki/index.md` | 11 | Claims **12 pages**; actual count is **11** `.md` files |
| ST-003 | `PRIVACY_AUDIT.md` | 15–21 | References `_verify_apps_sdk.py`, `test_fastmcp_return.py`, `widgets/` — gone |
| ST-004 | `server.py` | 1499 | Comment about removed tools (DC-010) |
| ST-005 | `ISSUES_TRACKER.md` | DEAD-001/002 | Says widgets/images removed — still accurate |
| ST-006 | `get_personality` docstring | 743–744 | Claims combines 4 files; demo has 1 |
| ST-007 | `create_page` docstring | 1112–1113 | Lists folders not in demo wiki |
| ST-008 | `FastMCP` instructions | 463–464 | “Immediately visible” overstated on cloud |
| ST-009 | `README.md` project tree | 104–117 | Omits `docs/ISSUES_TRACKER.md`, `DEAD_CODE_AUDIT.md` |

---

## DOCKER / FILE BLOAT

### DC-015 — Dockerfile copies all `*.py` into runtime image

```dockerfile
COPY mcp-server/*.py .
```

Copies into `/app/`:

| File | Needed at runtime? |
|------|:------------------:|
| `server.py` | Yes |
| `writer.py` | Yes (if writes enabled) |
| `sanitize.py` | Yes |
| `memory.py` | Yes (if Neon enabled) |
| `test_server.py` | **No** |
| `_test_cloud.py` | **No** |
| `_test_write.py` | **No** |

**Fix:** `COPY mcp-server/server.py mcp-server/writer.py ...` explicitly, or multi-stage build. **Saves:** ~15 KB + avoids shipping test harness in production.

---

### DC-016 — `_test_write.py` uses `requests` (not in requirements)

Dead path on fresh install until manual `pip install requests`. Either remove script, switch to `httpx`, or add dev dependency.

---

### DC-017 — Glob phantom `wiki/images/_index.json`

Some directory listings show `wiki/images/_index.json`; file read fails (missing or broken). If present on disk, delete — **no code references it**.

---

### DC-018 — `datetime` import only used by dead `_fmt_dt`

| File | Lines | Issue |
|------|------:|-------|
| `memory.py` | 20, 200–201 | `from datetime import datetime` exists solely for `_fmt_dt()` which is never called. Remove both together. |

---

### DC-019 — Memory `source` column fetched then dropped at MCP boundary

| File | Lines | Issue |
|------|------:|-------|
| `memory.py` | 116, 133, 141, 169 | SQL `SELECT ... source ...`; `_row()` includes `"source"`. |
| `server.py` | 1542–1555 | `_memory_to_dict()` **omits** `source` — value is read from DB and discarded. |

**Remove:** drop `source` from SELECTs, or expose in MCP response. **Risk:** None if removed from SQL.

---

### DC-020 — Memory `metadata` JSONB column write-only

| File | Lines | Issue |
|------|------:|-------|
| `memory.py` | 41, 97–104 | `metadata` inserted (always `{}` from `remember()`). Never SELECT'd or returned. |

**Remove column** only with DB migration; or wire into `remember()` API later.

---

### DC-021 — Whitespace-only dead lines

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 719–721 | Triple blank line before `get_status` |
| `server.py` | 1637–1639 | Triple blank line before entry point |

**Remove:** 4 blank lines. **Risk:** None.

---

### DC-022 — `get_personality` static `source` string when pages missing

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 775 | Always returns `"psychology · traits · behavior · preferences"` even when only `preferences` loaded (demo). Misleading metadata, not a crash. |

**Fix:** build `source` from keys actually present in `sections`.

---

### DC-023 — Repeated `if get_writer is None` boilerplate (6×)

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 1121–1126, 1198–1203, 1252–1257, 1300–1305, 1402–1409 | Same 4-line guard in every write tool. |

**Not dead** — functional. Optional: decorator/helper to DRY (~24 lines saved).

---

### DC-024 — Lazy import inside `create_page` on every call

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 1149 | `from writer import _build_page, extract_page_meta` inside function body — runs on every `create_page` call. |

**Move** to module-level (with existing writer import block). **Risk:** None.

---

### DC-025 — Orphan `widgets.cpython-312.pyc` (deleted `widgets.py` bytecode)

| File | Issue |
|------|-------|
| `mcp-server/__pycache__/widgets.cpython-312.pyc` | `widgets.py` source **gone** but bytecode remains from prior import. Proves widget module existed; not used by current `server.py`. |

**Remove:** delete `.pyc` (or entire `__pycache__/`). **Risk:** None. Already in `.gitignore`.

---

### DC-026 — `GitHubWriter.repo` attribute never read

| File | Lines | Issue |
|------|------:|-------|
| `writer.py` | 30 | `self.repo = repo` stored; only `self.base` URL used for API calls. |

**Remove:** attribute assignment. **Risk:** None.

---

### DC-027 — Writer frontmatter metrics never read back by server

| File | Lines | Issue |
|------|------:|-------|
| `writer.py` | 287–296, 321–326 | Writes `word_count`, `char_count`, `heading_count`, `wikilinks`, `summary` into markdown frontmatter on create/update. |
| `server.py` | `_parse_frontmatter`, `_load` | Parser loads keys into `fm` dict but engine **never uses** these metrics on read — only `title`, `aliases`, `tags`, privacy keys. |

**Dead on read path** — metadata is write-only decoration unless user reads raw markdown. Not removable without changing write format.

---

### DC-028 — `_OCEAN_ROW_RE` capture group 1 unused

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 585 | Regex group 1 `([OCEAN])` captured; `_extract_ocean` only uses `group(2)` trait name and `group(3)` score. |

**Simplify regex** to non-capturing group. **Risk:** None.

---

### DC-030 — Test scripts run at top level (not guarded)

| File | Issue |
|------|-------|
| `_test_write.py`, `_test_cloud.py` | No `if __name__ == "__main__"` — code executes on import. Dev-only scripts. |

**Fix:** wrap in `main()` guard. **Risk:** None for normal `python _test_write.py` usage.

---

### DC-029 — `create_page` in-memory `frontmatter` dict duplicates `_build_page` output

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 1168–1174 | Hand-built `frontmatter={}` on `WikiPage` — keys like `word_count` as strings; not parsed from `full_content`. Never read except `is_private()` (demo: always false). |

**Redundant assignment** — INC-003. Safe to parse from `full_content` instead of manual dict.

---

## Pass 3 — newly flagged REDUNDANT / INCOMPLETE

### RD-015 — `_get_wiki_stats()` rescans filesystem; engine already has sizes

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 699–717 | `rglob("*.md")` + `stat()` duplicates `engine.pages` + `get_folders()` already computed in same `get_status` call. |

**Redundant I/O** — not dead; could use `sum(p.size for p in engine.pages.values())`.

---

### RD-016 — `get_stats()` vs `_get_wiki_stats()` duplicate folder math

Both count pages per folder. `get_stats` uses engine; `get_status` uses `_get_wiki_stats`. Same data, two code paths (already RD-004).

---

### RD-017 — `read_page` / `search` / `recall` duplicate payload: structured + `summary` string

| Tools | Pattern |
|-------|---------|
| `search` | `results[]` + `summary` repeats same hits |
| `read_page` | `body` + `summary` (summary = header + body) |
| `recall`, `list_memories` | `memories[]` + `summary` |

**Intentional** for LLM clients — redundant bytes on wire, not removable without API break.

---

### RD-018 — `resource_status()` re-formats JSON from `get_status()` as markdown

| File | Lines | Issue |
|------|------:|-------|
| `server.py` | 1037–1068 | ~70 lines building markdown that duplicates `get_status()` tool output |

**Keep** for `wiki://status` resource URI consumers.

---

### INC-001 — `update_page` does not refresh `page.wikilinks` after content replace

| File | Lines | `server.py` 1222–1231 |
| After update, `get_graph` uses stale wikilinks until restart. **Buggy, not dead.**

---

### INC-002 — `rename_page` builds `WikiPage` without `wikilinks` / `word_count`

| File | Lines | `server.py` 1457–1463 |
| Defaults to empty/`0`; graph/search degraded until restart.

---

### INC-003 — `create_page` `frontmatter` dict ≠ parsed frontmatter in `content`

| File | Lines | `server.py` 1168–1174 vs 1155 |
| Manual dict may diverge from `_build_page` output in `full_content`.

---

### INC-004 — `append_to_page` in-memory path assigns full file to `page.body`

| File | Lines | `server.py` 1271–1277 |
| Documented in ISSUES_TRACKER BUG-001. **Broken, not dead.**

---

### INC-005 — `delete_page` / `rename_page` incomplete index cleanup

`name_map` aliases and `word_index` not fully cleared (ISSUES_TRACKER IDX-001).

---

## Pass 3 — newly flagged STALE (wiki + docstrings)

| ID | File | Line(s) | Issue |
|----|------|--------:|-------|
| ST-010 | `wiki/changelog.md` | 14 | Says "12 sample pages" — actual count is **11** |
| ST-011 | `wiki/index.md` | 11 | Says "**12 pages**" — should be **11** |
| ST-012 | `wiki/index.md` | — | `jordan-friend.md` exists, linked from `people-index`, **not** listed in index nav table |
| ST-013 | `get_stats` docstring | 877 | Claims "prompt totals, data inventory" — only outputs folder counts |
| ST-014 | `FastMCP` instructions | 456–473 | Omits `list_folders`, `rename_page`, `move_page`, `delete_page` from write/admin list |
| ST-015 | `list_pages` docstring | 788 | Lists folders (`google`, `browser`, …) not in demo wiki |
| ST-016 | `sanitize.py` module doc | 15–17 | Documents `safe_body` / `safe_excerpt` as public API — unused (DC-004) |
| ST-017 | `DEAD_CODE_AUDIT.md` | — | Did not link to `ISSUES_TRACKER.md` in Summary before pass 3 (fixed below) |

---

## Pass 4 — newly flagged (missed in passes 1–3)

### RD-019 — Frontmatter `sources:` never parsed

| File | Lines | Issue |
|------|------:|-------|
| `CLAUDE.md` | 36 | Schema documents `sources: [raw source files]` |
| `wiki/profile.md` | 7 | `sources: [demo]` present |
| `server.py` `_parse_frontmatter` | 118–134 | No code reads `sources` key |

**Dead schema field** for MCP — traceability is human-only in markdown.

---

### RD-020 — Frontmatter date key mismatch (`created` vs `created_at`)

| Location | Keys used |
|----------|-----------|
| Demo `wiki/*.md` (all 11 pages) | `created:`, `updated:` (date only) |
| `writer.py` `_build_page` | `created_at:`, `updated_at:` (ISO timestamps) |
| `CLAUDE.md` template | `created:`, `updated:` |

Pages created via `create_page` get different frontmatter shape than demo vault. **Not dead code** — schema drift / inconsistency.

---

### RD-021 — Inconsistent tag slice limits in tool outputs

| File | Lines | Slice |
|------|------:|-------|
| `server.py` search results | 263 | `tags[:6]` |
| `server.py` list_pages | 363 | `tags[:4]` |
| `server.py` get_graph nodes | 991 | `tags[:4]` |

**Redundant inconsistency** — not dead; pick one cap.

---

### RD-022 — Mixed MCP tool return types (str vs structured dict)

| Returns `str` | Returns `dict` (structured_output) |
|---------------|-----------------------------------|
| `list_pages`, `list_folders`, `search_prompts`, `get_people`, `get_stats`, `remember` | `search`, `read_page`, `get_status`, `get_personality`, `get_graph`, `recall`, `list_memories` |
| Write tools return `str` confirmation | |

**Intentional** heterogeneity — harder for generic MCP clients. Not removable without API break.

---

### LB-001 — Local `__pycache__/` (5 files, gitignored)

| File | Verdict |
|------|---------|
| `__pycache__/server.cpython-312.pyc` | Build artifact — **not in git** |
| `__pycache__/widgets.cpython-312.pyc` | **Orphan** — DC-025 |
| `__pycache__/memory.cpython-312.pyc` | Build artifact |
| `__pycache__/sanitize.cpython-312.pyc` | Build artifact |
| `__pycache__/writer.cpython-312.pyc` | Build artifact |
| `__pycache__/test_server.cpython-312.pyc` | Test artifact |

**Safe:** `Remove-Item -Recurse mcp-server/__pycache__` locally. Docker build won't include if `.dockerignore` added.

---

### LB-002 — No `.dockerignore` (only `.gitignore`)

| Issue |
|-------|
| `__pycache__`, `.env`, `docs/`, test scripts can leak into Docker context if present locally. Dockerfile only `COPY`s specific paths today — **low risk** but missing best practice. |

---

### FP-001 — `resource_index` / `resource_status` / `resource_personality` look uncalled

Static analysis reports these as dead. They are registered via `@mcp_server.resource(...)` — **not dead**. MCP framework invokes them by URI.

---

### FP-002 — `WikiPage.content` field

Used by `sanitize.safe_content(page)` in `get_people` and `resource_index`. **Not dead** (pass 3 incorrectly implied write-only).

---

### FP-003 — `sanitize.is_private()` frontmatter checks

`private` / `visibility` keys unused in demo wiki but **required** for production wikis. DORMANT in demo, not dead.

---

| ID | File | Line(s) | Issue |
|----|------|--------:|-------|
| ST-018 | `ISSUES_TRACKER.md` DEAD-001 | — | Widgets source removed — but `widgets.cpython-312.pyc` orphan remains (DC-025) |
| ST-019 | `DEAD_CODE_AUDIT.md` DC-017 | — | `wiki/images/_index.json` **not on disk** (pass 4); close as resolved |
| ST-020 | `wiki/profile.md` | 7 | `sources: [demo]` never consumed by engine (RD-019) |
| ST-021 | `test_server.py` | 41, 107 | Two `WikiEngine` instances per test run — redundant work |
| ST-022 | Pass 3 appendix | — | `widgets/` listed as removed — confirmed absent; glob index can be stale |

---

## Pass 4 — on-disk file inventory (46 files)

| Path | Lines (approx) | Verdict |
|------|----------------|---------|
| `.env.example` | 31 | KEEP |
| `.gitignore` | 27 | KEEP; add `.dockerignore` optional |
| `AGENTS.md` | 27 | KEEP |
| `CLAUDE.md` | 72 | KEEP; RD-019/020 schema drift |
| `Dockerfile` | 18 | KEEP |
| `LICENSE` | 22 | KEEP |
| `README.md` | 157 | KEEP |
| `render.yaml` | 25 | KEEP |
| `docs/CHATGPT.md` | 73 | KEEP |
| `docs/DEAD_CODE_AUDIT.md` | this file | KEEP |
| `docs/GITHUB.md` | 44 | KEEP |
| `docs/ISSUES_TRACKER.md` | — | KEEP |
| `docs/PRIVACY_AUDIT.md` | 61 | STALE refs |
| `docs/RENDER.md` | 35 | KEEP |
| `examples/mcp-cursor.json` | 12 | KEEP |
| `examples/mcp-claude-desktop.json` | 12 | KEEP |
| `mcp-server/server.py` | 1682 | see appendix |
| `mcp-server/writer.py` | 384 | DC-026,027 |
| `mcp-server/sanitize.py` | 189 | DC-004 |
| `mcp-server/memory.py` | 202 | DC-005,018–020 |
| `mcp-server/test_server.py` | 130 | ST-021 |
| `mcp-server/_test_cloud.py` | 63 | dev only |
| `mcp-server/_test_write.py` | 87 | dev only |
| `mcp-server/requirements.txt` | 4 | KEEP |
| `mcp-server/README.md` | 31 | REDUND |
| `mcp-server/__pycache__/*.pyc` | 5 files | LB-001 delete locally |
| `scripts/*.ps1`, `scripts/*.sh` | 4 files | KEEP |
| `wiki/*.md` | 11 files | ST-010–012, ST-020 |

**Absent on disk (do not delete again):** `mcp-server/widgets/`, `widgets.py`, `wiki/images/`

---

## File-by-file dead-code map

| File | Dead / redundant | Safe removals |
|------|------------------|---------------|
| `mcp-server/server.py` (~1682 lines) | DC-001–003,009–012,021–024; RD-002–004,007,009,012,015–018; INC-001–005; ST-014–015 | ~20 lines safe + docstring |
| `mcp-server/writer.py` (~384 lines) | DC-007,008; RD-001 | ~10 lines |
| `mcp-server/sanitize.py` (~189 lines) | DC-004; ST-016 | ~40 lines |
| `mcp-server/memory.py` (~202 lines) | DC-005,006,018–020; RD-013 | ~25 lines |
| `mcp-server/test_server.py` | TEST gaps only | 0 (keep) |
| `mcp-server/_test_*.py` | DC-014,016 | 0 or delete files for prod |
| `mcp-server/requirements.txt` | RD-011 | 0 (keep asyncpg) |
| `scripts/*` | All used | 0 |
| `examples/*.json` | Both needed | 0 |
| `docs/*` | ST-003, RD-008 | edit only |
| `wiki/*.md` | ST-010,011,012 | Fix page counts + index nav (no file deletes) |
| `Dockerfile` | DC-015 | change COPY line |
| `CLAUDE.md` / `AGENTS.md` | RD-008 intentional mirror | 0 |
| `README.md` | RD-008 partial dup | optional trim |

---

## Recommended removal order (safest first)

1. **DC-001, DC-002** — unused imports (2 min)  
2. **DC-010, DC-011, DC-012** — comments + docstring (5 min)  
3. **DC-004** — unused `sanitize` exports (5 min)  
4. **DC-005, DC-006** — memory dead code + FTS index (5 min)  
5. **DC-003, DC-007, DC-008, DC-009** — engine/writer cleanup (15 min)  
6. **DC-015** — Dockerfile explicit COPY (5 min)  
7. **ST-001, ST-002, ST-003** — stale docs/wiki text (10 min)  
8. **RD-001** — shared wikilink regex (optional refactor)  
9. Do **not** remove RD-002, RD-003, RD-005 without MCP version bump  

---

## Verification after cleanup

```powershell
cd opensource\mcp-server
python test_server.py

# Optional: grep for removed symbols (should be 0 hits except docs)
rg "safe_body|safe_excerpt|contains_secrets|_rebuild_engine|_fmt_dt" .

# Docker smoke (if Docker installed)
docker build -t wiki-brain-test ..
docker run --rm -e MCP_API_KEY=test -e MCP_TRANSPORT=streamable-http -p 8000:8000 wiki-brain-test
curl http://localhost:8000/health
```

---

## What is NOT dead (common false positives)

| Item | Why keep |
|------|----------|
| `move_page` | Registered MCP tool — wrapper is intentional |
| `search_prompts` | Needed when user adds `chatgpt/` wiki folder |
| `_git_pull` | Used when `WIKI_AUTO_PULL=1` |
| `_extract_ocean` | Needed when personality pages include OCEAN scores |
| `resource_index/status/personality` | MCP resource URIs for resource-capable clients |
| `get_stats` vs `get_status` | Different output formats for LLM vs structured clients |
| `AGENTS.md` + `CLAUDE.md` | Dual discovery for Cursor vs Claude |
| `list_folders` | Smaller tool surface for folder-only queries |
| `append_to_page` broken in-memory sync | **Buggy but used** — fix, don't delete (ISSUES_TRACKER BUG-001) |
| All 11 demo wiki pages | Loaded and searchable |

---

## Line-by-line appendix (pass 3)

Verdict key: **KEEP** = required · **REMOVE** = safe dead code · **REDUND** = duplicate/overlap · **DORMANT** = unused in demo · **STALE** = wrong/outdated text · **FIX** = runs but wrong

### `mcp-server/server.py` (1682 lines)

| Lines | Content | Verdict | Notes |
|------:|---------|---------|-------|
| 1–45 | Module docstring | **STALE** | DC-012: lists `get_profile`, `reload_wiki`, `sync_local`, `wiki://profile`, `wiki://stats` |
| 47 | `import base64` | **KEEP** | Used in `append_to_page` |
| 48–49 | `hashlib`, `hmac` | **KEEP** | Auth middleware |
| 50 | `import httpx` | **REMOVE** | DC-001: unused |
| 51 | `import json` | **REMOVE** | DC-001: unused |
| 52–67 | `logging`…`sanitize` | **KEEP** | |
| 73–77 | `_REPO_ROOT`, `WIKI_DIR` | **KEEP** | |
| 79–80 | `MAX_RESPONSE_CHARS`, `SEARCH_EXCERPT_LEN` | **KEEP** | |
| 86 | `_WIKILINK_RE` | **KEEP** | RD-001: duplicate in writer.py |
| 89–102 | `WikiPage` dataclass | **KEEP** | DC-009: `word_count` field never read |
| 105–114 | `WikiEngine.__init__` | **KEEP** | |
| 118–134 | `_parse_frontmatter` | **KEEP** | PARSE-001: not real YAML |
| 136–191 | `_load` | **KEEP** | SEC-010 symlink follow (ISSUES_TRACKER) |
| 193–208 | `_prune_deleted_pages` | **KEEP** | |
| 212–266 | `search` | **KEEP** | |
| 268–288 | `_excerpt` | **KEEP** | |
| 292–351 | `get_page` | **KEEP** | Steps 5–7 dormant for demo |
| 353–366 | `list_pages` | **KEEP** | |
| 368–372 | `get_folders` | **KEEP** | |
| 379–382 | `_truncate` | **KEEP** | |
| 389–445 | `APIKeyMiddleware` | **KEEP** | DC-011: `/health` in `_OPEN_PATHS` unreachable |
| 452–475 | `FastMCP(...)` | **KEEP** | ST-014: instructions incomplete |
| 478–484 | `_get_engine` | **KEEP** | |
| 489–526 | `search` tool | **KEEP** | RD-017: results + summary |
| 529–579 | `read_page` tool | **KEEP** | SEC-009: suggestions leak private pages |
| 584–611 | `_OCEAN_ROW_RE`, `_extract_ocean`, `_first_paragraph` | **DORMANT** | DM-002 in demo |
| 614–654 | `_get_git_info` | **KEEP** | 3× subprocess per `get_status` |
| 657–667 | `_get_recent_changelog` | **KEEP** | |
| 670–696 | `_get_recently_modified_files` | **KEEP** | |
| 699–717 | `_get_wiki_stats` | **REDUND** | RD-015: duplicate filesystem scan |
| 719–721 | blank lines | **REMOVE** | DC-021 |
| 722–738 | `get_status` | **KEEP** | |
| 741–780 | `get_personality` | **KEEP** | DC-013/022: duplicate body/summary; static source |
| 783–805 | `list_pages` tool | **KEEP** | ST-015 docstring |
| 808–834 | `search_prompts` | **DORMANT** | DM-001: empty in demo |
| 837–872 | `get_people` | **KEEP** | |
| 875–898 | `get_stats` | **KEEP** | RD-004; ST-013 docstring |
| 903–917 | `_resolve_link` | **KEEP** | |
| 920–1025 | `get_graph` | **KEEP** | RD-014: `strength: 1` constant |
| 1030–1035 | `resource_index` | **KEEP** | RD-003; missing newline before next decorator |
| 1036–1068 | `resource_status` | **KEEP** | RD-018 |
| 1071–1080 | `resource_personality` | **KEEP** | RD-003; subset of tool |
| 1087–1092 | writer import try/except | **KEEP** | |
| 1095–1098 | `_rel_path_for` | **KEEP** | |
| 1101–1186 | `create_page` | **KEEP** | DC-024 lazy import; INC-003 frontmatter |
| 1189–1237 | `update_page` | **KEEP** | INC-001 wikilinks stale |
| 1240–1287 | `append_to_page` | **FIX** | DC-002; INC-004 |
| 1290–1325 | `delete_page` | **KEEP** | INC-005 index cleanup |
| 1332–1349 | `_write_local_copy`, `_delete_local_copy` | **KEEP** | SEC-001 path traversal |
| 1352–1356 | `_rebuild_engine` | **REMOVE** | DC-003 |
| 1359–1379 | `_git_pull` | **DORMANT** | DM-004; BUG-002 wrong branch |
| 1384–1471 | `rename_page` | **KEEP** | INC-002; BUG-005 non-atomic |
| 1474–1483 | `move_page` | **REDUND** | RD-002 wrapper |
| 1488–1496 | `list_folders` | **KEEP** | RD-006 |
| 1499–1500 | stale comment | **REMOVE** | DC-010 |
| 1506–1635 | memory tools | **KEEP** | DC-019 source dropped |
| 1637–1639 | blank lines | **REMOVE** | DC-021 |
| 1644–1681 | `__main__` | **KEEP** | DM-007 SSE path; DC-003 auth warn |

---

### `mcp-server/writer.py` (384 lines)

| Lines | Content | Verdict | Notes |
|------:|---------|---------|-------|
| 1–9 | module docstring | **KEEP** | |
| 13–17 | imports | **KEEP** | |
| 20–98 | `GitHubWriteError`, `GitHubWriter` HTTP | **KEEP** | PERF-001: new client per call |
| 104–125 | `create_wiki_page` | **KEEP** | SEC-002 path validation missing |
| 127–148 | `update_wiki_page` | **KEEP** | |
| 150–173 | `append_to_wiki_page` | **KEEP** | |
| 175–184 | `delete_wiki_page` | **KEEP** | |
| 191–194 | regex constants | **KEEP** | RD-001 duplicate wikilink |
| 197–243 | `extract_page_meta` | **KEEP** | DC-007: `title` param unused |
| 246–299 | `_build_page` | **KEEP** | DC-008: `include_meta=False` dead branch |
| 302–327 | `_update_meta_on_write` | **KEEP** | |
| 330–355 | `_append_under_heading` | **KEEP** | |
| 362–383 | `get_writer` singleton | **KEEP** | BUG-003 default branch `master` |

---

### `mcp-server/sanitize.py` (189 lines)

| Lines | Content | Verdict | Notes |
|------:|---------|---------|-------|
| 1–18 | module docstring | **STALE** | ST-016: lists unused exports |
| 25–74 | regex constants | **KEEP** | |
| 79–88 | `PRIVATE_*` sets | **KEEP** | |
| 91–92 | `_disabled` | **KEEP** | |
| 95–120 | `redact` | **KEEP** | |
| 123–141 | `is_private` | **KEEP** | |
| 144–151 | `private_placeholder` | **KEEP** | |
| 154–159 | `safe_body` | **REMOVE** | DC-004 |
| 162–167 | `safe_content` | **KEEP** | Used by `get_people`, `resource_index` |
| 170–173 | `safe_excerpt` | **REMOVE** | DC-004 |
| 176–188 | `contains_secrets` | **REMOVE** | DC-004 |

---

### `mcp-server/memory.py` (202 lines)

| Lines | Content | Verdict | Notes |
|------:|---------|---------|-------|
| 1–15 | module docstring | **KEEP** | |
| 19–21 | imports | **KEEP** | DC-018: `datetime` only for dead `_fmt_dt` |
| 29–30 | `MemoryError` | **KEEP** | |
| 33–47 | `SCHEMA_SQL` | **KEEP** | DC-006: FTS index unused; DC-020: metadata column |
| 39–40 | `source`, `metadata` columns | **DORMANT** | RD-013; DC-019/020 |
| 50–76 | `MemoryStore` init/connect/close | **KEEP** | DC-005: `close()` never called |
| 82–106 | `add` | **KEEP** | metadata always `{}` from MCP |
| 108–126 | `search` | **KEEP** | |
| 128–146 | `list_recent` | **KEEP** | |
| 148–151 | `delete` | **REMOVE** | DC-005 |
| 153–156 | `count` | **REMOVE** | DC-005 |
| 163–171 | `_row` | **KEEP** | `source` fetched then dropped at MCP |
| 174–176 | `_json` | **KEEP** | |
| 186–197 | `get_memory` | **KEEP** | |
| 200–201 | `_fmt_dt` | **REMOVE** | DC-005/018 |

---

### `mcp-server/test_server.py` (130 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–130 | **KEEP** | TEST-002: vacuous folder-filter test; no tool/sanitize coverage |

---

### `mcp-server/_test_cloud.py` (63 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–63 | **KEEP** (dev only) | DC-014/016: not runtime; `sys` used for exit |

---

### `mcp-server/_test_write.py` (87 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–87 | **KEEP** (dev only) | DEP-002: needs `requests` not in requirements |

---

### `mcp-server/requirements.txt` (4 lines)

| Line | Verdict | Notes |
|-----:|---------|-------|
| 1–3 | **KEEP** | DEP-001 unpinned; asyncpg required even without Neon (RD-011) |

---

### `mcp-server/README.md` (31 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–31 | **REDUND** | RD-008: ~80% duplicate of root README |

---

### `Dockerfile` (18 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–18 | **KEEP** | DC-015: copies test scripts; OPS-001: root user |

---

### `render.yaml` (25 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–25 | **KEEP** | All env vars referenced by server/writer |

---

### `.env.example` (31 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 18 | **STALE** | ST-001: mentions images |
| rest | **KEEP** | |

---

### `.gitignore` (33 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–33 | **KEEP** | `raw/`, `.obsidian` anticipatory |

---

### `scripts/install.ps1` (29 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–29 | **KEEP** | Runs tests |

---

### `scripts/install.sh` (22 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–22 | **KEEP** | |

---

### `scripts/start.ps1` (20 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–20 | **KEEP** | SCRIPT-001 naive `.env` parse |

---

### `scripts/start.sh` (17 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–17 | **KEEP** | SCRIPT-001 |

---

### `examples/mcp-cursor.json` (12 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–12 | **KEEP** | Placeholder paths intentional |

---

### `examples/mcp-claude-desktop.json` (12 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–12 | **KEEP** | Different root key (`mcpServers` vs `servers`) |

---

### `README.md` (157 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–157 | **KEEP** | RD-008; tools table accurate; omits audit docs |

---

### `CLAUDE.md` (72 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–72 | **KEEP** | DOC-008: `raw/` layer optional |

---

### `AGENTS.md` (27 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–27 | **KEEP** | RD-008: intentional mirror of CLAUDE.md |

---

### `LICENSE` (22 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–22 | **KEEP** | |

---

### `docs/CHATGPT.md` (73 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–73 | **KEEP** | SEC-004 query token documented |

---

### `docs/GITHUB.md` (44 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–44 | **KEEP** | |

---

### `docs/RENDER.md` (35 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–35 | **KEEP** | |

---

### `docs/PRIVACY_AUDIT.md` (61 lines)

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–61 | **STALE** | DOC-003: references deleted files |

---

### `docs/ISSUES_TRACKER.md`

| Verdict | Notes |
|---------|-------|
| **KEEP** | Security/bug tracker; complements this file |

---

### `wiki/*.md` (11 files, all lines KEEP unless noted)

| File | Lines | Verdict | Notes |
|------|------:|---------|-------|
| `index.md` | 1–37 | **STALE** | ST-011 page count; ST-012 missing jordan-friend in table |
| `changelog.md` | 1–16 | **STALE** | ST-010 "12 sample pages" |
| `profile.md` | all | **KEEP** | Demo persona |
| `preferences.md` | all | **KEEP** | Only personality page loaded in demo |
| `people/people-index.md` | all | **KEEP** | |
| `people/jordan-friend.md` | all | **KEEP** | Reachable via wikilinks, not index table |
| `projects/projects-index.md` | all | **KEEP** | |
| `projects/task-tracker.md` | all | **KEEP** | |
| `topics/python.md` | all | **KEEP** | |
| `topics/mongodb.md` | all | **KEEP** | |
| `academics/courses.md` | all | **KEEP** | |

**No wiki file is dead code** — all 11 are indexed and searchable. None should be deleted.

---

## Pass 3 — what was missed in passes 1–2

| ID | Finding |
|----|---------|
| DC-018–024 | `datetime` orphan import, memory `source`/`metadata` dead paths, blank lines, static personality source, write-tool boilerplate, lazy import |
| RD-015–018 | Filesystem rescan in `get_status`, wire-format duplication, resource markdown rebuild |
| INC-001–005 | Stale wikilinks/index after writes (fix, don't delete) |
| ST-010–017 | Wiki page count wrong in 2 files, orphan nav entry, misleading docstrings |
| Line-by-line appendix | Full per-file table above |

---

## Pass 4 — what was missed in passes 1–3

| ID | Finding |
|----|---------|
| DC-025 | Orphan `widgets.cpython-312.pyc` — proves deleted `widgets.py` |
| DC-026–029 | `GitHubWriter.repo` unused; writer frontmatter metrics read-never; OCEAN regex group 1; manual frontmatter dict |
| RD-019–022 | `sources:` never parsed; `created` vs `created_at` drift; tag slice inconsistency; mixed str/dict tools |
| LB-001–002 | Local `__pycache__`; no `.dockerignore` |
| FP-001–003 | MCP resources + `page.content` + `is_private` are **not** dead |
| ST-018–022 | Correct DEAD-001 status; DC-017 images file absent; test double engine |
| Inventory | **46 files** on disk; widgets/images folders **absent** (glob stale) |

### Pass 4 — `server.py` lines not previously called out

| Lines | Code | Verdict | Notes |
|------:|------|---------|-------|
| 97 | `content: str` on `WikiPage` | **KEEP** | FP-002: `safe_content()` |
| 100 | `frontmatter: dict` | **KEEP** | FP-003 privacy; most keys unused |
| 158 | `word_count = len(...)` in `_load` | **REMOVE** | DC-009 duplicate of DC-027 |
| 230–235 | title phrase boost loop | **KEEP** | iterates all pages — O(n) per search candidate |
| 324–349 | `get_page` fuzzy steps 5–7 | **DORMANT** | unused for unique demo stems |
| 597 | `m.group(1)` in OCEAN regex | **REMOVE** | DC-028 unused capture |
| 631 | trailing whitespace line | **STALE** | style only |
| 890–893 | `chatgpt`/`copilot` folder stats | **DORMANT** | empty in demo |
| 1035–1036 | missing newline between resources | **STALE** | DOC-007 |
| 1163 | `aliases=[]` on create | **KEEP** | new pages have no aliases until edited |
| 1171–1173 | str() casts in frontmatter dict | **REMOVE** | DC-029 dead dict keys |
| 1352–1356 | `_rebuild_engine` | **REMOVE** | DC-003 |
| 1636–1639 | triple blank lines | **REMOVE** | DC-021 |

### Pass 4 — `writer.py` lines not previously called out

| Lines | Code | Verdict | Notes |
|------:|------|---------|-------|
| 30 | `self.repo = repo` | **REMOVE** | DC-026 |
| 224–234 | `summary` extraction loop | **KEEP** | writes to FM; DC-027 never read back |
| 311–317 | `_set_fm_field` insert path | **KEEP** | used on updates |
| 371 | `GITHUB_BRANCH` default `master` | **FIX** | BUG-003 ISSUES_TRACKER |

### Pass 4 — `memory.py` lines not previously called out

| Lines | Code | Verdict | Notes |
|------:|------|---------|-------|
| 43 | `memories_tags_idx` GIN | **KEEP** | used by `ANY(tags)` query unlike FTS index |
| 97–104 | `metadata` INSERT | **DORMANT** | DC-020 always `{}` |
| 116,169 | `source` in SELECT/`_row` | **REMOVE** | DC-019 dropped at MCP boundary |

### Pass 4 — `sanitize.py` — no new dead lines beyond DC-004

All regex constants used by `redact()` / `is_private()` / `contains_secrets()`.

### Pass 4 — `test_server.py` line-by-line

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–4 | KEEP | docstring |
| 6–11 | KEEP | imports |
| 13–15 | KEEP | globals |
| 18–29 | KEEP | `test()` helper |
| 41 | REDUND | ST-021: second engine created at 107 via module |
| 44 | KEEP | `n >= 10` weak threshold |
| 87–88 | STALE | TEST-002 vacuous folder test |
| 99–112 | KEEP | only async tool test |
| 114–119 | KEEP | perf smoke |
| 128–129 | KEEP | exit code |

### Pass 4 — `_test_cloud.py` line-by-line

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–7 | KEEP | docstring |
| 8–10 | KEEP | `sys` used for exit |
| 25 | REDUND | trailing slash URL `mcp/?token=` vs `_test_write` `mcp?token=` |
| 36 | STALE | `Mcp-Session-Id` header casing (MCP-001) |
| 41–61 | KEEP | init + tools/list smoke |
| 52–59 | KEEP | JSON parse in loop — no `tools/call` test |

### Pass 4 — `_test_write.py` line-by-line

| Lines | Verdict | Notes |
|------:|---------|-------|
| 1–87 | KEEP (dev) | DEP-002 needs `requests` |
| 28–32 | KEEP | `_parse_sse` |
| 35–41 | KEEP | `call()` helper |
| 44–86 | KEEP | top-level script execution (not `if __name__`) — runs on import |

See **DC-030** — test scripts execute at top level.

### Pass 4 — wiki files line-by-line (frontmatter only)

All 11 pages share pattern lines 1–7: `title`, optional `aliases`, `tags`, `created`, `updated`. None use `created_at`/`updated_at` (RD-020). Only `profile.md` has `sources:` (ST-020). **No wiki file is deletable.**

| File | Body lines | Verdict |
|------|----------|---------|
| `index.md` | 9–37 | ST-011, ST-012 |
| `changelog.md` | 9–16 | ST-010 |
| `profile.md` | 10–33 | KEEP; `sources` unused |
| `preferences.md` | 8–20 | KEEP; only personality page for OCEAN path |
| `people/people-index.md` | 8–18 | KEEP |
| `people/jordan-friend.md` | 8–14 | KEEP; missing from index table |
| `projects/projects-index.md` | 8–22 | KEEP |
| `projects/task-tracker.md` | 8–25 | KEEP |
| `topics/python.md` | 8–24 | KEEP |
| `topics/mongodb.md` | 8–16 | KEEP |
| `academics/courses.md` | 8–20 | KEEP |

---

*Update this file when dead code is removed — mark `[REMOVED yyyy-mm-dd]` next to the ID.*

=