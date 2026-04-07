# LLM Wiki Schema

> This file tells your LLM agent how to maintain this wiki. Read it before any wiki operation.

## Directory Structure

- `raw/` — Source documents. **Immutable.** Never modify these.
- `wiki/` — LLM-maintained wiki pages. You own this directory entirely.
- `wiki/index.md` — Master index of all pages with one-line summaries.
- `wiki/log.md` — Chronological log of all operations.

## MCP Tools Available

You have these tools via the `llm-wiki-kit` MCP server:

- `wiki_ingest` — Ingest a source (file path, URL, or YouTube link). Auto-detects format.
- `wiki_write_page` — Create or update a wiki page
- `wiki_read_page` — Read a wiki page
- `wiki_search` — Full-text search across all pages
- `wiki_lint` — Health-check for broken links, orphans, etc.
- `wiki_status` — Overview of the wiki
- `wiki_log` — Append to the chronological log

## Conventions

### Page Format
- Each page starts with a `# Title` header
- Use `[[Page Name]]` for cross-references to other wiki pages
- Add YAML frontmatter when useful (tags, sources, dates)

### Page Types
- **Source summaries** — One per ingested source
- **Entity pages** — People, organizations, products
- **Concept pages** — Ideas, theories, patterns
- **Comparison pages** — Structured comparisons
- **Synthesis pages** — Cross-cutting analysis

### Workflows

#### Ingest
1. Call `wiki_ingest` with the file path
2. Create a source summary page
3. Create/update entity and concept pages
4. Cross-reference with `[[Page Name]]`
5. Update `wiki/index.md`
6. Log with `wiki_log`

#### Query
1. `wiki_search` for relevant pages
2. `wiki_read_page` for details
3. Synthesize with citations

#### Lint
1. `wiki_lint` to find issues
2. Fix broken links, empty pages, orphans
3. Log the lint pass

## Principles

- The wiki compounds — connect new content to existing pages
- Cross-reference aggressively with `[[brackets]]`
- Flag contradictions explicitly
- Keep index.md current
- Log everything
