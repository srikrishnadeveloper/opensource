# Wiki Brain Open Source — Issues Tracker

**Audit date:** 2026-06-08  
**Re-audit (pass 2):** 2026-06-08 — full tree rescan (39 files; widgets/images confirmed removed)  
**Scope:** Every file under `opensource/` — security, bugs, docs drift, dead code, ops gaps  
**Test baseline:** `python mcp-server/test_server.py` → **39/39 passed** (engine/search only; no write/auth/sanitize tests)

Use this file to track fixes before a public release. Severity: **CRITICAL** → **INFO**.

---

## Summary

| Severity | Count |
|----------|------:|
| CRITICAL | 3 |
| HIGH | 11 |
| MEDIUM | 15 |
| LOW | 19 |
| INFO | 13 |
| RESOLVED (pass 2) | 2 |
| **Total open** | **48** |

---

## CRITICAL — fix before any public deploy with write tools

### SEC-001 — Path traversal in local write sync (`_write_local_copy`)

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `_write_local_copy()`, `_delete_local_copy()` (lines ~1332–1349); called from `create_page`, `update_page`, `append_to_page`, `rename_page` |
| **Problem** | `folder` and `name` are not validated. A value like `people/../../escape` resolves **outside** `WIKI_DIR` when written. Confirmed: writes land in parent directories, not under `wiki/`. |
| **Impact** | Any MCP client that can call write tools (or local dev with GitHub token) could create/delete files outside the wiki tree on the host filesystem. |
| **Fix** | Add `_safe_wiki_path(folder, name) -> Path` that rejects `..`, backslashes, absolute paths, and ensures `path.resolve().is_relative_to(WIKI_DIR.resolve())`. Use in all local sync helpers. |

### SEC-002 — Path traversal in GitHub write paths (`writer.py`)

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/writer.py` — `create_wiki_page()`, `put_file()` path construction |
| **Problem** | `folder` / `name` are only stripped; `..` segments are allowed. Path becomes `wiki/{folder}/{name}.md` which can target **outside** `wiki/` in the GitHub repo (e.g. `wiki/foo/../../README.md`). |
| **Impact** | Compromised or malicious MCP session + `GITHUB_TOKEN` can modify arbitrary files in the connected repo, not just `wiki/`. |
| **Fix** | Validate folder/name: allow only `[a-zA-Z0-9_-]+` per segment; reject `..`; optionally enforce an allowlist of top-level folders. |

### SEC-003 — HTTP deploy is public when `MCP_API_KEY` is unset

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — entry point (~1659–1679), `APIKeyMiddleware` |
| **Problem** | If `MCP_API_KEY` is empty on Render, server logs a warning but **still serves all MCP tools without authentication**. |
| **Impact** | Full read (and write, if `GITHUB_TOKEN` set) exposure to the internet. |
| **Fix** | Fail fast on `streamable-http` / `sse` when `MCP_API_KEY` is missing (exit non-zero). Document in `RENDER.md`. |

---

## HIGH — functional bugs or meaningful security gaps

### BUG-001 — `append_to_page` in-memory state wrong after GitHub write

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `append_to_page()` (~1270–1283) |
| **Problem** | Decoded GitHub response is assigned to `page.body` and `page.content`, but the API returns the **full file** (frontmatter + body). Body should be re-parsed via `_parse_frontmatter`. On decode failure, in-memory and local copy stay stale while GitHub is updated. |
| **Fix** | After successful append, re-fetch from GitHub or run `_append_under_heading` locally on `page.content`, then `_parse_frontmatter` for `page.body`. |

### BUG-002 — `_git_pull()` hardcodes `origin master`

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `_git_pull()` (~1363–1364) |
| **Problem** | Always pulls `master`; `.env.example` and `render.yaml` default `GITHUB_BRANCH=main`. |
| **Impact** | `WIKI_AUTO_PULL=1` fails or pulls wrong branch on modern repos. |
| **Fix** | Use `os.environ.get("GITHUB_BRANCH", "main")` (match `writer.py` / `render.yaml`). |

### BUG-003 — Default branch mismatch: `writer.py` vs config

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/writer.py` (`GitHubWriter.__init__` default `master`, `get_writer()` default `master`); `.env.example` / `render.yaml` use `main` |
| **Problem** | If `GITHUB_BRANCH` is unset, writes target `master` while deploy/docs assume `main`. |
| **Fix** | Change default to `main` everywhere. |

### SEC-004 — API key in query string (`?token=`)

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `APIKeyMiddleware` (~430–432); `docs/CHATGPT.md`; `_test_write.py`, `_test_cloud.py` |
| **Problem** | Token accepted via URL query for ChatGPT compatibility. Query strings appear in access logs, browser history, Referer headers, and proxy logs. |
| **Impact** | Credential leakage if logs are retained or shared. |
| **Fix** | Prefer Bearer header in docs; add log-sanitization middleware; warn in `CHATGPT.md`; consider short-lived session tokens after initial `?token=` handshake. |

### SEC-005 — Write tools have no folder allowlist or confirmation

| Field | Detail |
|-------|--------|
| **Files** | `create_page`, `delete_page`, `rename_page`, `update_page` in `server.py` |
| **Problem** | Any authenticated MCP client can create/delete/rename any page when `GITHUB_TOKEN` is configured. No dry-run, no protected paths (e.g. `index.md`, `profile.md`). |
| **Fix** | Optional `WIKI_WRITE_ALLOW_FOLDERS`; block deletes of core pages; require explicit flag for destructive ops. |

### SEC-006 — `search_prompts` skips privacy redaction

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `search_prompts()` (~808–834) |
| **Problem** | Unlike `search()`, does not filter `sanitize.is_private()` pages and does not call `sanitize.redact()` on excerpts. |
| **Impact** | Private/secret folder content can leak via prompt search if those folders exist. |
| **Fix** | Mirror `search()` privacy filter + `sanitize.redact()` on excerpts. |

### SEC-007 — `list_pages` exposes private page metadata

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `list_pages()` (~783–805), `WikiEngine.list_pages()` (~353–366) |
| **Problem** | Lists stem, title, folder, tags for **all** pages including those in `secrets/`, `private/`, or tagged `private`. |
| **Impact** | Metadata disclosure (existence of sensitive pages). |
| **Fix** | Skip or mask private pages in listing (same rules as `is_private()`). |

### SEC-008 — Memory tools return raw content (no redaction)

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `recall()`, `list_memories()`, `remember()` |
| **Problem** | Memory text is stored and returned without `sanitize.redact()`. Users can `remember()` secrets that then leak on `recall`. |
| **Fix** | Redact on read; optionally block `contains_secrets()` on write. |

### SEC-009 — `read_page` leaks private page names in “not found” suggestions

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `read_page()` (~538–548) |
| **Problem** | When a page is not found, suggestions come from raw `engine.search()` with **no** `sanitize.is_private()` filter. Private/secret pages can appear in `suggestions` and the human-readable `summary`. |
| **Impact** | Confirms existence and stem names of hidden pages. |
| **Fix** | Filter suggestions the same way `search()` does before returning hints. |

### SEC-010 — Symlink escape on wiki **read**/index (`WikiEngine._load`)

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `WikiEngine._load()` (~140–146) |
| **Problem** | `wiki_dir.rglob("*.md")` follows symlinks. A symlink `wiki/link.md → /etc/passwd` (or any readable file) is indexed; `read_text()` pulls **out-of-tree content** into `page.body`. Confirmed in isolated test. |
| **Impact** | Local wiki with untrusted symlinks (or compromised write access) can exfiltrate arbitrary readable files via `read_page` / `search`. |
| **Fix** | Use `rglob` with `follow_symlinks=False` (Python 3.12+), or resolve each path and reject if not under `wiki_dir.resolve()`. |

### SEC-011 — GitHub API error bodies echoed to MCP clients

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/writer.py` (~56, 84, 97); all write tools return `f"Error: {e}"` |
| **Problem** | `GitHubWriteError` includes `r.text[:200–300]` from GitHub. Write tools pass this string back to the LLM/client. |
| **Impact** | May leak repo structure, branch names, permission errors, or internal GitHub messages. |
| **Fix** | Log full error server-side; return generic message to client. |

---

## MEDIUM — consistency, dead code, index correctness

### IDX-001 — In-memory index incomplete after writes

| Field | Detail |
|-------|--------|
| **Files** | `create_page`, `update_page`, `delete_page`, `rename_page` in `server.py` |
| **Problem** | `create_page` only indexes title/tag words, not body words. `delete_page` / `rename_page` do not clean or rebuild `word_index` / `name_map` fully. `update_page` does not refresh search index. |
| **Impact** | Search results wrong until server restart (Docker redeploy on Render masks this locally). |
| **Fix** | Call `_rebuild_engine()` after writes, or extract shared `_index_page()` / `_deindex_page()` helpers. |

### DOC-001 — Stale module docstring in `server.py` header

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` (lines 1–45) |
| **Problem** | Documents tools that **do not exist**: `get_profile`, `reload_wiki`, `sync_local`. Documents resources `wiki://profile`, `wiki://stats` — only `wiki://index`, `wiki://status`, `wiki://personality` are registered. |
| **Fix** | Update header to match actual 19 tools and 3 resources. |

### DOC-002 — `.env.example` mentions removed image writes

| Field | Detail |
|-------|--------|
| **Files** | `.env.example` line ~18 |
| **Problem** | Comment says write tools enable "images"; image/JOS pipeline was removed from opensource. |
| **Fix** | Change comment to list actual write tools only. |

### DOC-003 — `PRIVACY_AUDIT.md` references missing files

| Field | Detail |
|-------|--------|
| **Files** | `docs/PRIVACY_AUDIT.md` |
| **Problem** | References `_verify_apps_sdk.py`, `test_fastmcp_return.py`, `widgets/_preview.html` — not present in current `opensource/` tree (partially stale audit). |
| **Fix** | Re-scan and update audit doc; link to this tracker. |

### DEAD-001 — ~~Orphan `mcp-server/widgets/` directory~~ [RESOLVED pass 2]

| Field | Detail |
|-------|--------|
| **Status** | Folder no longer present in tree (pass 2 glob: 39 files, no `widgets/`). |
| **Action** | None — verify it stays out if merging from `mine/`. |

### DEAD-002 — ~~Orphan `wiki/images/`~~ [RESOLVED pass 2]

| Field | Detail |
|-------|--------|
| **Status** | `wiki/images/` no longer on disk. |
| **Action** | None. |

### BUG-004 — Stem collision: pages keyed by filename only

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `WikiEngine._load()` (`self.pages[f.stem] = page`) |
| **Problem** | Two files in different folders with the same stem (e.g. `people/notes.md` and `projects/notes.md`) collide — last loaded wins; the other is invisible to `get_page` / search index. |
| **Impact** | Silent data loss in index for multi-folder wikis. Demo wiki has unique stems today (11 pages). |
| **Fix** | Key by `(folder, stem)` or full relative path; update `get_page` / write helpers. |

### BUG-005 — `rename_page` is non-atomic on GitHub

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `rename_page()` (~1435–1442) |
| **Problem** | Creates new path via `put_file`, then deletes old. If delete fails, duplicate files exist on GitHub. |
| **Fix** | Use GitHub git trees API for atomic move, or rollback create on delete failure. |

### BUG-006 — Slash in `name` creates unintended nested GitHub paths

| Field | Detail |
|-------|--------|
| **Files** | `writer.py` `create_wiki_page()`; `server.py` `create_page` / `rename_page` |
| **Problem** | `name` like `foo/bar` becomes `wiki/{folder}/foo/bar.md` — not path traversal but bypasses single-segment assumptions. |
| **Fix** | Reject `/` and `\` in `name` (and each `folder` segment). |

### DOC-004 — FastMCP `instructions` overstate write visibility on cloud

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` — `FastMCP(..., instructions=...)` (~463–464) |
| **Problem** | Tells the model writes are “immediately visible via search/read” — on Render, in-memory index updates are partial (IDX-001) and filesystem is ephemeral until redeploy. |
| **Fix** | Clarify: “visible in this session; cloud deploy may need redeploy for baked image.” |

### PRIV-001 — `get_personality` / `resource_personality` skip `is_private()` check

| Field | Detail |
|-------|--------|
| **Files** | `get_personality()`, `resource_personality()` (~741–780, ~1071–1080) |
| **Problem** | Reads `page.body` directly; only applies `redact()` on combined output, not `is_private()` gate per page. |
| **Fix** | Use `sanitize.safe_body(page)` and skip private pages. |

### PRIV-002 — `WIKI_DISABLE_REDACTION=1` bypasses all privacy

| Field | Detail |
|-------|--------|
| **Files** | `sanitize.py`, `.env.example` |
| **Problem** | Intentional dev bypass; if set on Render by mistake, all redaction and private-page hiding is disabled. |
| **Fix** | Refuse to start HTTP transport when this env is set; or ignore on non-localhost. |

### DOC-005 — `create_page` docstring lists folders not in demo wiki

| Field | Detail |
|-------|--------|
| **Files** | `server.py` — `create_page` docstring (~1112–1113) |
| **Problem** | Lists `chatgpt`, `copilot`, `google`, `browser`, `contacts`, `certificates`, `devices` — demo wiki only has `academics`, `people`, `personal`, `projects`, `topics`, `root`. |
| **Fix** | Document as examples, not enforced allowlist; or align with `WIKI_ALLOWED_FOLDERS` config. |

### MEM-001 — FTS index created but never used

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/memory.py` — `memories_content_fts` GIN index; `search()` uses `ILIKE` only |
| **Problem** | Dead schema complexity; ILIKE `%query%` can't use FTS index. |
| **Fix** | Switch search to `to_tsvector` / `plainto_tsquery`, or drop unused index. |

### MEM-002 — No `delete_memory` MCP tool

| Field | Detail |
|-------|--------|
| **Files** | `memory.py` has `delete()`; `server.py` has no tool wrapper |
| **Problem** | Memories can be added but not removed via MCP (GDPR / mistake correction gap). |
| **Fix** | Add `forget_memory(id)` tool. |

### MEM-003 — No size limits on `remember()` content

| Field | Detail |
|-------|--------|
| **Files** | `remember()`, `memory.add()` |
| **Problem** | Unbounded TEXT inserts — DB fill / DoS via repeated large memories. |
| **Fix** | Cap content length (e.g. 4 KB) and rate-limit per session if possible. |

### OPS-001 — Docker image runs as root

| Field | Detail |
|-------|--------|
| **Files** | `Dockerfile` |
| **Problem** | No `USER` directive; container processes run as root. |
| **Fix** | Add non-root user after `pip install`. |

---

## LOW — quality, supply chain, dev experience

### TEST-001 — Test suite coverage gaps

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/test_server.py` |
| **Problem** | Tests only `WikiEngine` + `get_status`. No tests for: `sanitize.py`, auth middleware, write tools, memory tools, path validation, `search_prompts` privacy. |
| **Fix** | Add unit tests per module; mock GitHub/Neon for integration tests. |

### TEST-002 — Weak / vacuous assertions

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/test_server.py` (~87–88) |
| **Problem** | `search('react', folder='projects')` passes when **zero** results (`or len(folder_results) == 0`) — does not verify folder filter works. Page count test `>= 10` passes with 11 pages but won't catch regressions to 9. |
| **Fix** | Use known demo content for folder-filter test; assert exact minimum page count. |

### DEP-001 — Unpinned Python dependencies

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/requirements.txt` — `mcp>=1.11.0`, `httpx>=0.27`, `asyncpg>=0.29` |
| **Problem** | Builds are non-reproducible; upstream breaking changes or vulnerabilities can slip in silently. |
| **Fix** | Pin exact versions or use lock file; add Dependabot / `pip-audit` in CI. |

### DEP-002 — `_test_write.py` depends on `requests` (not in requirements)

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/_test_write.py` (imports `requests`); `requirements.txt` lists only `mcp`, `httpx`, `asyncpg` |
| **Problem** | `python _test_write.py` fails on fresh install unless user manually `pip install requests`. |
| **Fix** | Switch to `httpx` (already a dep) or add `requests` to requirements / optional `[dev]` extra. |

### OPS-002 — No CI/CD pipeline

| Field | Detail |
|-------|--------|
| **Files** | (missing) `.github/workflows/` |
| **Problem** | No automated test/lint on PRs. |
| **Fix** | Add workflow: `pip install`, `python test_server.py`, `ruff`/`mypy` optional. |

### OPS-003 — No `SECURITY.md`

| Field | Detail |
|-------|--------|
| **Files** | (missing) |
| **Problem** | No documented vulnerability reporting process for open source. |
| **Fix** | Add `SECURITY.md` with contact / disclosure policy. |

### OPS-004 — No rate limiting on HTTP MCP endpoint

| Field | Detail |
|-------|--------|
| **Files** | `server.py` HTTP transport |
| **Problem** | Public or leaked URL can be hammered (DoS, brute-force on API key). |
| **Fix** | Render-level rate limits, or Starlette middleware (slowapi, etc.). |

### SCRIPT-001 — Naive `.env` parsing in start scripts

| Field | Detail |
|-------|--------|
| **Files** | `scripts/start.ps1` (~9–15), `scripts/start.sh` (~8–12) |
| **Problem** | Simple `KEY=VALUE` split; breaks on quoted values containing `=`, multiline secrets, or spaces. `start.sh` pipes `.env` through `sed` + `source`. |
| **Fix** | Use `python-dotenv` or document "no spaces around values". |

### SAN-001 — Over-aggressive redaction on generic "token"

| Field | Detail |
|-------|--------|
| **Files** | `sanitize.py` — `_SECRET_KEYS` includes bare `token` |
| **Problem** | Innocuous prose like "session token: optional" may become `***REDACTED***`. |
| **Fix** | Narrow generic fallbacks; require minimum entropy on captured values. |

### SAN-002 — Aadhaar regex false positives

| Field | Detail |
|-------|--------|
| **Files** | `sanitize.py` — `_AADHAAR_RE` |
| **Problem** | Any 12-digit number (with optional spaces) is masked — can hit order IDs, timestamps. |
| **Fix** | Tighten pattern (checksum digit) or require context keyword "aadhaar". |

### PERF-001 — New `httpx.AsyncClient` per GitHub API call

| Field | Detail |
|-------|--------|
| **Files** | `writer.py` — `get_file`, `put_file`, `delete_file` |
| **Problem** | No connection pooling; extra latency on write-heavy sessions. |
| **Fix** | Shared client on `GitHubWriter` instance. |

### DOC-006 — `create_page` folder not validated (only strip)

| Field | Detail |
|-------|--------|
| **Files** | `server.py`, `writer.py` |
| **Problem** | Slashes in `folder` create nested paths (`people/sub`); may be intended but undocumented. |
| **Fix** | Document or restrict to single path segment. |

### DOC-007 — `resource_index` missing newline before next decorator

| Field | Detail |
|-------|--------|
| **Files** | `server.py` ~1035–1036 |
| **Problem** | `return ...` immediately followed by `@mcp_server.resource` — valid Python but hurts readability. |
| **Fix** | Add blank line (style only). |

### CODE-001 — Unused `httpx` import in `server.py`

| Field | Detail |
|-------|--------|
| **Files** | `mcp-server/server.py` line 50 |
| **Problem** | `import httpx` is never used (`writer.py` owns HTTP calls). |
| **Fix** | Remove dead import. |

### SEC-012 — No request-body size limits (DoS)

| Field | Detail |
|-------|--------|
| **Files** | `create_page`, `update_page`, `append_to_page`, `remember` |
| **Problem** | No max length on page `content` or memory text — huge payloads can exhaust RAM, DB, or GitHub API. |
| **Fix** | Cap writes (e.g. 512 KB/page, 4 KB/memory). |

### DOC-008 — `CLAUDE.md` references `raw/` layer not in public repo

| Field | Detail |
|-------|--------|
| **Files** | `CLAUDE.md` |
| **Problem** | Three-layer schema assumes `raw/` directory; opensource only ships `wiki/` + gitignored `raw/` placeholder in `.gitignore`. |
| **Fix** | Mark `raw/` as optional local-only in opensource docs. |

### MCP-001 — MCP session header casing differs between test scripts

| Field | Detail |
|-------|--------|
| **Files** | `_test_write.py` (`mcp-session-id`) vs `_test_cloud.py` (`Mcp-Session-Id`) |
| **Problem** | Inconsistent client headers may cause flaky smoke tests. |
| **Fix** | Align with FastMCP canonical header; document in `mcp-server/README.md`. |

### PRIV-004 — `get_graph` exposes raw page titles in nodes

| Field | Detail |
|-------|--------|
| **Files** | `get_graph()` node builder (~986–988) |
| **Problem** | `label: page.title` is not passed through `sanitize.redact()`. Unusual but titles could contain sensitive strings. |
| **Fix** | Redact titles or use stem only. |

### PARSE-001 — Frontmatter parser is not real YAML

| Field | Detail |
|-------|--------|
| **Files** | `WikiEngine._parse_frontmatter()` (~118–134) |
| **Problem** | Line-based `key: val` split — fails on multiline values, `:` in values, nested structures. Tags array parsing is fragile. |
| **Impact** | Malformed or rich frontmatter silently mis-indexed; not a security parser bug but data integrity risk. |
| **Fix** | Use `yaml.safe_load` on frontmatter block (add `pyyaml` dep) or document supported subset. |

---

## INFO — operational notes (not necessarily code bugs)

### INFO-001 — Rotate credentials if ever committed

| Detail |
|--------|
| Per `PRIVACY_AUDIT.md`: rotate `MCP_API_KEY` and GitHub PAT if they appeared in git history or test scripts before sanitization. |

### INFO-002 — Server binds `0.0.0.0`

| Detail |
|--------|
| Required for Render/Docker. Ensure `MCP_API_KEY` is always set in production. |

### INFO-003 — `memory.search` ILIKE wildcards

| Detail |
|--------|
| User `%` or `_` in query acts as SQL wildcards (not injection — parameterized). Can cause slow scans. Escape wildcards if needed. |

### INFO-004 — `get_status` / `resource_status` expose git author and paths

| Detail |
|--------|
| May leak deploy machine identity or internal paths via `modified_files` — low risk for personal wiki, note for multi-tenant. |

### INFO-005 — Free Render plan cold starts

| Detail |
|--------|
| Documented in `RENDER.md`; ChatGPT may timeout on first request. |

### INFO-006 — Docker not verified locally

| Detail |
|--------|
| No Docker on audit machine; `Dockerfile` build untested in this audit. |

### INFO-007 — `pip audit` unavailable

| Detail |
|--------|
| Environment lacked `pip audit`; dependency CVE scan not run. Use CI with `pip-audit` or `uv pip compile`. |

### INFO-008 — Demo wiki has no `chatgpt/` or `copilot/` folders

| Detail |
|--------|
| `search_prompts` works but returns empty for demo install — expected; document in README. |

### INFO-009 — Auth compares SHA-256 hashes, not raw key

| Detail |
|--------|
| `APIKeyMiddleware` uses `hmac.compare_digest(sha256(token), sha256(key))` — good timing-safe compare; hashing is unusual but acceptable for fixed-length API keys. |

### INFO-010 — `_load` uses `errors="replace"` for UTF-8

| Detail |
|--------|
| Invalid bytes in markdown become U+FFFD silently — may corrupt search/index without warning. |

### INFO-011 — `_test_cloud.py` uses protocol `2024-11-05`

| Detail |
|--------|
| `_test_write.py` uses `2025-03-26`. Mismatch may hide connector compatibility issues — align when testing ChatGPT. |

### INFO-012 — README does not link to this tracker

| Detail |
|--------|
| Consider adding `docs/ISSUES_TRACKER.md` under Docs section for contributors. |

### INFO-013 — Render blueprint deploy succeeds without `MCP_API_KEY`

| Detail |
|--------|
| `render.yaml` marks `MCP_API_KEY` as `sync: false` but does not require it — combines with SEC-003 for accidental public deploy. |

---

## Pass 2 — what changed

| Finding | Notes |
|---------|--------|
| `mcp-server/widgets/` | **Gone** — DEAD-001 resolved |
| `wiki/images/` | **Gone** — DEAD-002 resolved |
| Symlink read escape | **New** SEC-010 |
| `read_page` suggestion leak | **New** SEC-009 |
| Stem collision | **New** BUG-004 |
| `requests` missing for `_test_write.py` | **New** DEP-002 |
| Unused `httpx` in `server.py` | **New** CODE-001 |
| Privacy PII scan | **Clean** — only fictional `alex@example.com`, `jordan@example.com` |

---

## File-by-file checklist

| Path | Status | Notes |
|------|--------|-------|
| `mcp-server/server.py` | **Issues** | SEC-001–003, SEC-009–010, SEC-012, BUG-001–006, DOC-001/004–007, IDX-001, SEC-004–008, PRIV-001–002/004, CODE-001, PARSE-001 |
| `mcp-server/writer.py` | **Issues** | SEC-002, SEC-011, BUG-003/006, PERF-001 |
| `mcp-server/sanitize.py` | **Issues** | SAN-001–002, PRIV-002 |
| `mcp-server/memory.py` | **Issues** | MEM-001–003, INFO-003 |
| `mcp-server/test_server.py` | **Issues** | TEST-001, TEST-002 |
| `mcp-server/_test_write.py` | **Issues** | DEP-002, SEC-004, MCP-001 |
| `mcp-server/_test_cloud.py` | **Issues** | SEC-004, MCP-001, INFO-011 |
| `mcp-server/requirements.txt` | **Issues** | DEP-001 |
| `mcp-server/widgets/*` | **Resolved** | Removed (pass 2) |
| `mcp-server/README.md` | **OK** | INFO-012 |
| `wiki/*.md` | **OK** | Fictional demo data, 11 pages |
| `wiki/images/` | **Resolved** | Removed (pass 2) |
| `scripts/install.ps1` | **OK** | Runs tests |
| `scripts/install.sh` | **OK** | (not re-run in audit) |
| `scripts/start.ps1` | **Issues** | SCRIPT-001 |
| `scripts/start.sh` | **Issues** | SCRIPT-001 |
| `examples/mcp-*.json` | **OK** | Placeholder paths only |
| `Dockerfile` | **Issues** | OPS-001; no widgets copy (correct) |
| `render.yaml` | **OK** | Health check `/health` |
| `.env.example` | **Issues** | DOC-002 |
| `.gitignore` | **OK** | Covers `.env`, secrets |
| `README.md` | **OK** | Accurate feature list |
| `AGENTS.md` | **OK** | |
| `CLAUDE.md` | **Issues** | DOC-008 (`raw/` layer) |
| `LICENSE` | **OK** | MIT, contributors |
| `docs/CHATGPT.md` | **Issues** | SEC-004 documents query token |
| `docs/GITHUB.md` | **OK** | (not line-audited; no issues found in grep) |
| `docs/RENDER.md` | **OK** | |
| `docs/PRIVACY_AUDIT.md` | **Issues** | DOC-003 stale references |
| `docs/ISSUES_TRACKER.md` | **This file** | |

---

## Suggested fix order

1. **SEC-001, SEC-002, SEC-003** — path validation + fail-closed auth  
2. **SEC-009, SEC-010** — suggestion leak + symlink read escape  
3. **BUG-002, BUG-003** — branch defaults  
4. **SEC-006, SEC-007, SEC-008, PRIV-001** — privacy consistency  
5. **BUG-001, IDX-001, BUG-004** — write path + index correctness  
6. **DOC-001–003, DOC-004** — docstring / instructions cleanup  
7. **TEST-001, DEP-001, DEP-002, OPS-002** — CI, pins, test deps  
8. Everything else  

---

## Re-audit commands

```powershell
cd opensource\mcp-server
python test_server.py

# Personal data scan
rg -i "srikrishna|srik2|selvam|mithun|madukkarai|gigabyte" ..

# Secrets
rg "github_pat_|ghp_[A-Za-z0-9]{20,}" ..

# Stale tool names
rg "get_profile|reload_wiki|sync_local|wiki://profile|wiki://stats" mcp-server/server.py
```

---

*Update this file when issues are fixed — mark with `[FIXED yyyy-mm-dd]` in the ID row or remove entry.*
