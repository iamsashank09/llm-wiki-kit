# LLM Wiki Schema

> This file tells your LLM agent how to maintain this wiki. Read it before any wiki operation.

## Directory Structure

- `raw/` — Source documents. **Immutable.** Never modify these.
- `wiki/` — LLM-maintained wiki pages. You own this directory entirely.
- `wiki/index.md` — Master index of all pages with one-line summaries.
- `wiki/log.md` — Chronological log of all operations.

### Recommended Folders

```
wiki/
├── sources/      # One page per ingested source
├── concepts/     # Ideas, theories, techniques
├── entities/     # People, orgs, products
├── synthesis/    # Cross-source analysis
├── index.md
└── log.md
```

Use **kebab-case** for filenames: `attention-mechanism.md`

## MCP Tools Available

You have these tools via the `llm-wiki-kit` MCP server:

- `wiki_ingest` — Ingest a source (file path, URL, or YouTube link). Auto-detects format.
- `wiki_write_page` — Create or update a wiki page
- `wiki_read_page` — Read a wiki page
- `wiki_search` — Full-text search across all pages
- `wiki_lint` — Health-check for broken links, orphans, etc.
- `wiki_status` — Overview of the wiki
- `wiki_log` — Append to the chronological log
- `wiki_graph` — Generate an interactive HTML visualization of the knowledge graph

## Conventions

### Page Format
- Each page starts with a `# Title` header
- Use `[[Page Name]]` for cross-references to other wiki pages
- Add YAML frontmatter when useful (tags, sources, dates)

### Page Types
- **Source summaries** (`sources/`) — One per ingested source. Include: summary, key points, `[[cross-references]]`
- **Concept pages** (`concepts/`) — Ideas, theories, patterns. Link to sources that discuss them.
- **Entity pages** (`entities/`) — People, organizations, products
- **Synthesis pages** (`synthesis/`) — Cross-source analysis comparing perspectives

### Workflows

#### Ingest
1. Call `wiki_ingest` with the file path, URL, or YouTube link
2. Create a source summary page in `sources/`
3. Create/update concept and entity pages
4. Cross-reference with `[[Page Name]]`
5. Update `wiki/index.md`
6. Log with `wiki_log`

#### Update existing pages
When a new source adds context to an existing concept:
1. Add source to frontmatter `sources:` list
2. Add `updated:` date
3. Integrate new info (don't just append)
4. Link to the new source page

#### Query
1. `wiki_search` for relevant pages
2. `wiki_read_page` for details
3. Synthesize with citations: `*Sources: [[page1]], [[page2]]*`
4. For complex questions, create a `synthesis/` page

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
