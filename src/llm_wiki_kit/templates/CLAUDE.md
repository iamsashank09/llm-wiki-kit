# LLM Wiki Schema

> This file tells Claude how to maintain this wiki. **Feel free to customize it for your domain.**

## Directory Structure

- `raw/` — Source documents. **Immutable.** Never modify these.
- `wiki/` — LLM-maintained wiki pages. You own this directory entirely.
- `wiki/index.md` — Master index of all pages with one-line summaries.
- `wiki/log.md` — Chronological log of all operations.

### Suggested Folders

```
wiki/
├── sources/      # One page per ingested source
├── concepts/     # Ideas, theories, techniques
├── index.md
└── log.md
```

Create other folders as needed (`entities/`, `synthesis/`, etc). Use **kebab-case** filenames.

## MCP Tools

- `wiki_ingest` — Ingest a source (file path, URL, or YouTube link)
- `wiki_write_page` — Create or update a wiki page
- `wiki_read_page` — Read a wiki page
- `wiki_search` — Full-text search across all pages
- `wiki_lint` — Health-check for broken links, orphans, etc.
- `wiki_status` — Overview of the wiki
- `wiki_log` — Append to the chronological log
- `wiki_graph` — Generate interactive HTML knowledge graph

## Page Format

Each page should have:
- A `# Title` header
- `[[Cross-References]]` to related pages
- Optional frontmatter for tracking sources:
  ```yaml
  ---
  sources: [paper.pdf, video.md]
  ---
  ```

### Page Types

**Source summaries** — One per ingested source. Key takeaways, notable claims, links to concepts.

**Concept pages** — Ideas, theories, techniques. Link back to sources that discuss them.

**Synthesis pages** — When you need to compare/connect multiple sources on a topic.

## Workflows

### Ingest
1. `wiki_ingest` the file/URL/YouTube link
2. Create a source summary in `sources/`
3. Create or update concept pages
4. Add `[[cross-references]]` liberally
5. Update `index.md`

### Update existing pages
When a new source adds context to an existing page:
- Add it to `sources:` frontmatter
- Weave in new information (don't just append)
- Link to the new source page

### Answer questions
1. `wiki_search` for relevant terms
2. `wiki_read_page` the top results
3. Cite your sources: `*See [[page1]], [[page2]]*`
4. For complex cross-source questions, consider creating a synthesis page

## Principles

- **The wiki compounds.** Connect new content to existing pages.
- **Cross-reference aggressively.** The value is in the links.
- **Flag contradictions.** If sources disagree, note it explicitly.
- **Keep index.md current.** It's the table of contents.
