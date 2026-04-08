# LLM Wiki Schema

> This file tells Codex how to maintain this wiki. **Customize it for your domain.**

## Structure

- `raw/` — Source documents. **Immutable.**
- `wiki/` — LLM-maintained pages.
- `wiki/index.md` — Master index.
- `wiki/log.md` — Operation log.

Suggested folders: `sources/`, `concepts/`. Create others as needed. Use **kebab-case** filenames.

## MCP Tools

- `wiki_ingest` — Ingest a source (file, URL, YouTube)
- `wiki_write_page` / `wiki_read_page` — Create/read pages
- `wiki_search` — Full-text search
- `wiki_lint` — Find broken links, orphans
- `wiki_status` — Wiki overview
- `wiki_log` — Append to log
- `wiki_graph` — Generate knowledge graph HTML

## Page Format

- Start with `# Title`
- Use `[[Cross-References]]` to link pages
- Optional `sources:` frontmatter to track where info came from

## Workflows

**Ingest:** `wiki_ingest` → create source summary → create/update concept pages → update index

**Query:** `wiki_search` → `wiki_read_page` → synthesize answer with citations

**Lint:** `wiki_lint` → fix broken links → flesh out stubs

## Principles

- Connect new content to existing pages
- Cross-reference aggressively with `[[brackets]]`
- Flag contradictions between sources
- Keep index.md current
