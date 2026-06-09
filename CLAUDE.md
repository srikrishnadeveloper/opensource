# Personal LLM Wiki — Schema

## Overview

A personal knowledge base maintained by an LLM agent. Raw sources are read once; structured markdown pages in `wiki/` are created and cross-linked.

**Wiki location:** set `WIKI_BRAIN_DIR` or use default `./wiki`

---

## Three-Layer Architecture

### Layer 1: Raw Sources (`raw/`)
- Immutable source files. Read only — never modify.
- Copy exports here from Downloads, cloud takeout, etc.
- Gitignored by default.

### Layer 2: The Wiki (`wiki/`)
- LLM-generated markdown with `[[wikilinks]]`.
- Organized by folder: `academics/`, `projects/`, `people/`, `personal/`, `topics/`, etc.

### Layer 3: This Schema (`CLAUDE.md` / `AGENTS.md`)
- Structure, conventions, and ingest workflows.

---

## Page Conventions

### Frontmatter
```yaml
---
title: Page Title
tags: [relevant, tags]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [raw source files]
---
```

### Cross-References
- Use `[[Page Name]]` wikilinks.
- Create entity pages when new people or concepts appear.

### Citations
- `(Source: filename.pdf)` for traceability.

---

## Workflows

### Ingest a New Source
1. User provides a file or directory.
2. LLM reads the source.
3. Create summary in `wiki/sources/` (optional).
4. Update related pages.
5. Update `wiki/index.md` and `wiki/changelog.md`.

### Explore a Directory
1. List and categorize files.
2. Propose ingest plan to user.
3. Ingest on approval.
4. Update exploration tracking if you maintain one.

---

## Important Notes

- Never modify files outside this repo without user consent.
- Raw sources are immutable.
- Prefer depth over breadth.
- Flag uncertainty with `> [!question]` callouts.
