# Privacy audit — opensource/

Last audit: **2026-06-08**

## Summary

All files in `opensource/` were scanned for personal data, credentials, and deployment-specific leaks.

**Status: CLEAN** after fixes below (re-scan before every public release).

## Critical fixes applied

| Issue | Files | Action |
|-------|-------|--------|
| **Real `MCP_API_KEY` hardcoded** | `_test_write.py`, `_test_cloud.py` | Removed secrets; scripts now require `MCP_TEST_URL` + `MCP_API_KEY` env vars |
| **Personal Render URL** | Same 2 files | Replaced with env-based URL |
| **Hardcoded personal stats** | `server.py` `get_stats()` | Removed WhatsApp/Gmail/YouTube counts; now computed from wiki only |
| **Personal names in tests** | `test_server.py` | Replaced with fictional "Alex Dev" |
| **Personal docstring examples** | `server.py`, `writer.py` | Generic examples only |
| **Preview widget leak** | Widget system | Removed entirely from open-source repo |
| **Copyright name** | `LICENSE` | Changed to "Wiki Brain contributors" |

## Action required (you)

1. **Rotate `MCP_API_KEY` on Render** — a key was previously embedded in test scripts. Treat it as compromised even after removal.
2. **Rotate GitHub PAT** if it was ever in `git remote` URL or committed.
3. If this folder was already pushed with secrets, **git history may still contain them** — use a fresh repo or `git filter-repo` before going public.

## Scan checklist (re-run before release)

```powershell
cd opensource
# Personal names / paths
rg -i "srikrishna|srik2|selvam|mithun|madukkarai|gigabyte" .

# Secrets
rg "github_pat_|ghp_[A-Za-z0-9]{20,}|3yZ4" .

# Hardcoded stats from personal wiki
rg "36,070|6,135|15,007|17,003" .

# Real deploy URLs (allow placeholders only)
rg "wiki-brain-mcp\.onrender\.com" .
```

Expected: **no matches** except `github_pat_xxxxxxxx` placeholder in docs.

## Safe intentional content

| Item | Why it's OK |
|------|-------------|
| `alex@example.com`, `jordan@example.com` | RFC 2606 fictional demo emails |
| `sanitize.py` mentions Aadhaar/PAN | Redaction patterns, not real IDs |
| `render.yaml` service name `wiki-brain-mcp` | Generic product name, not your instance URL |
| `User-Agent: wiki-brain-mcp` | Product identifier |

## Demo wiki

`wiki/` contains only fictional data (Alex Dev, Jordan Lee, Task Tracker). No government IDs, chats, or exports.
