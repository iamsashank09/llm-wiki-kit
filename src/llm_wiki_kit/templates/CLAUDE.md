# LLM Wiki Schema

> This file tells Claude how to maintain this wiki. Read it before any wiki operation.

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
- Add YAML frontmatter for metadata:
  ```yaml
  ---
  tags: [concept, important]
  sources: [article.md, paper.pdf]
  created: 2025-01-01
  updated: 2025-01-15
  ---
  ```

### Page Types
- **Source summaries** — One per ingested source. Key takeaways, notable claims.
- **Entity pages** — People, organizations, products, projects.
- **Concept pages** — Ideas, theories, patterns, techniques.
- **Comparison pages** — Structured comparisons between entities or concepts.
- **Synthesis pages** — Cross-cutting analysis that connects multiple sources.

### Cross-References
- Always use `[[Page Name]]` when mentioning a topic that has its own page.
- If you mention something important that doesn't have a page yet, still use `[[brackets]]` — the lint tool will flag it as a page that should be created.

## Workflows

### Ingest a new source
1. User drops a file in `raw/` and asks you to process it
2. Call `wiki_ingest` with the file path
3. Read the returned content carefully
4. Create a source summary page: `wiki_write_page("sources/filename", "...")`
5. Create or update entity/concept pages as needed
6. Add `[[cross-references]]` between related pages
7. Update `wiki/index.md` with new pages
8. Call `wiki_log` to record what you did

### Answer a question
1. Call `wiki_search` with relevant terms
2. Call `wiki_read_page` for the most relevant results
3. Synthesize an answer citing wiki pages
4. If the question reveals a gap, note it for future ingest

### Lint pass
1. Call `wiki_lint` to get the issue list
2. Fix broken links (create missing pages or correct links)
3. Flesh out empty pages
4. Add inbound links to orphan pages
5. Call `wiki_log` to record the lint pass

## Principles

- **The wiki compounds.** Every ingest should make connections to existing content.
- **Cross-reference aggressively.** The value is in the links between ideas.
- **Flag contradictions.** If a new source disagrees with existing wiki content, note it explicitly on both pages.
- **Keep the index current.** It's the table of contents for the whole wiki.
- **Log everything.** The log is how the human tracks what happened.
