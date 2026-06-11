"""
Wiki Brain — smoke tests against the bundled demo wiki.

NEW HERE? Run this file after any code change — all lines should say OK.

WHAT IT TESTS (no GitHub, no network):
  - WikiEngine loads wiki/*.md
  - get_page finds pages by name and alias
  - search returns sensible results
  - folder path validation rules
  - get_status() async tool

Run from repo root:  python mcp-server/test_server.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from server import (
    WikiEngine,
    WIKI_DIR,
    _truncate,
    _validate_folder_path,
    _normalize_folder,
)

PASS = 0
FAIL = 0
TOTAL = 0


def test(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if condition:
        PASS += 1
        print(f"  OK  {name}")
    else:
        FAIL += 1
        msg = f"  FAIL {name}"
        if detail:
            msg += f" -- {detail}"
        print(msg)


def main():
    # LEARN: Each test("name", condition) increments PASS or FAIL. No pytest — plain Python.
    global PASS, FAIL, TOTAL
    start = time.time()

    print("=" * 60)
    print(" Wiki Brain MCP Server -- Test Suite (demo wiki)")
    print("=" * 60)

    print("\n1. Engine Loading")
    engine = WikiEngine(WIKI_DIR)
    n = len(engine.pages)
    test("Wiki directory exists", WIKI_DIR.exists())
    test("Pages loaded", n >= 10, f"got {n}")
    test("Word index built", len(engine.word_index) > 50, f"got {len(engine.word_index)} words")
    test("Name map built", len(engine.name_map) > 15, f"got {len(engine.name_map)} entries")

    print("\n2. Folder Structure")
    folders = engine.get_folders()
    for ef in ["academics", "people", "personal", "projects", "topics", "root"]:
        test(f"Folder '{ef}' exists", ef in folders, f"got {list(folders.keys())}")

    print("\n3. Page Retrieval")
    for stem in ["profile", "index", "task-tracker", "mongodb", "python"]:
        test(f"get_page('{stem}')", engine.get_page(stem) is not None)

    alias_tests = [
        ("Profile", "profile"),
        ("Projects Overview", "projects-index"),
        ("People", "people-index"),
        ("Changelog", "changelog"),
        ("Courses", "courses"),
    ]
    for alias, expected in alias_tests:
        page = engine.get_page(alias)
        test(
            f"get_page('{alias}') -> {expected}",
            page is not None and page.stem == expected,
            f"got {page.stem if page else 'None'}",
        )

    print("\n4. Search")
    for query, expect in [
        ("task tracker", "task-tracker"),
        ("mongodb", "mongodb"),
        ("python", "python"),
        ("jordan", "jordan"),
    ]:
        results = engine.search(query)
        test(f"search('{query}') finds results", len(results) > 0)
        if expect:
            stems = [r["page"] for r in results]
            test(f"  contains '{expect}'", any(expect in s for s in stems), f"got {stems[:5]}")

    test("search('xyznonexistent123') empty", len(engine.search("xyznonexistent123")) == 0)

    folder_results = engine.search("react", folder="projects")
    test("folder filter projects", all(r["folder"] == "projects" for r in folder_results) or len(folder_results) == 0)

    print("\n5. List Pages")
    test("list_pages() >= 10", len(engine.list_pages()) >= 10)
    test("list_pages('people') >= 1", len(engine.list_pages("people")) >= 1)

    print("\n6. Folder Path Validation")
    test("_validate_folder_path('people') ok", _validate_folder_path("people") is None)
    test("_validate_folder_path('work/notes') ok", _validate_folder_path("work/notes") is None)
    test("_validate_folder_path('..') rejected", _validate_folder_path("../x") is not None)
    test("_validate_folder_path('root') rejected", _validate_folder_path("root") is not None)
    test("_normalize_folder strips slashes", _normalize_folder("/people/") == "people")

    print("\n7. Truncation and Edge Cases")
    test("truncate short", _truncate("hello", 100) == "hello")
    test("get_page('') is None", engine.get_page("") is None)
    test("search('') empty", len(engine.search("")) == 0)

    print("\n8. get_status (async)")
    import asyncio
    import server as srv

    async def _status():
        return await srv.get_status()

    try:
        status = asyncio.run(_status())
        test("get_status returns ok", status.get("status") == "ok")
        test("get_status has wiki stats", "total_pages" in status.get("wiki", {}))
        test("get_status has no jos key", "jos" not in status)
    except Exception as e:
        test("get_status runs without error", False, str(e))

    print("\n9. Performance")
    t0 = time.time()
    for _ in range(50):
        engine.search("python mongodb task")
    avg_ms = (time.time() - t0) / 50 * 1000
    test("search avg < 500ms", avg_ms < 500, f"avg {avg_ms:.1f}ms")

    print("\n10. Notion sync helpers")
    import notion_sync as ns

    fm, body = ns._parse_frontmatter("---\ntitle: Test\ntags: [a, b]\n---\n# Hi")
    test("_parse_frontmatter title", fm.get("title") == "Test")
    test("_parse_frontmatter body", body.startswith("# Hi"))
    test("_parse_tags", ns._parse_tags('[ "x", "y" ]') == ["x", "y"])
    test("_content_hash stable", len(ns._content_hash("abc")) == 64)

    print("\n11. Render auto-config (GitHub repo/branch)")
    import os
    import writer as wr

    saved = {k: os.environ.get(k) for k in (
        "GITHUB_REPO", "RENDER_GIT_REPO_SLUG",
        "GITHUB_BRANCH", "RENDER_GIT_BRANCH",
    )}
    try:
        for k in saved:
            os.environ.pop(k, None)
        os.environ["RENDER_GIT_REPO_SLUG"] = "alice/wiki-brain"
        os.environ["RENDER_GIT_BRANCH"] = "main"
        test("github_repo_from_env uses Render slug", wr.github_repo_from_env() == "alice/wiki-brain")
        test("github_branch_from_env uses Render branch", wr.github_branch_from_env() == "main")
        os.environ["GITHUB_REPO"] = "override/repo"
        test("GITHUB_REPO overrides Render slug", wr.github_repo_from_env() == "override/repo")
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f" Results: {PASS}/{TOTAL} passed, {FAIL} failed ({elapsed:.1f}s)")
    print("=" * 60)
    return FAIL == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
