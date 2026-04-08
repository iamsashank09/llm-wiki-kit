# LLM Wiki Schema

> This file tells Claude how to maintain this wiki. Read it before any wiki operation.

## Directory Structure

- `raw/` — Source documents. **Immutable.** Never modify these.
- `wiki/` — LLM-maintained wiki pages. You own this directory entirely.
- `wiki/index.md` — Master index of all pages with one-line summaries.
- `wiki/log.md` — Chronological log of all operations.

### Recommended Folders

Organize pages by type:

```
wiki/
├── sources/          # One page per ingested source
├── concepts/         # Ideas, theories, techniques
├── entities/         # People, orgs, products, projects
├── synthesis/        # Cross-source analysis
├── index.md
└── log.md
```

Use **kebab-case** for filenames: `attention-mechanism.md`, `karpathy-gpt-video.md`

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

**Source summaries** (`sources/`) — One per ingested source:
```markdown
---
tags: [paper|video|article, topic1, topic2]
source: filename.pdf
created: YYYY-MM-DD
---
# Title (Author, Year)

## Summary
Brief overview of the source.

## Key Points
- Point 1 with [[Cross-Reference]]
- Point 2

## See Also
- [[Related Concept]]
```

**Concept pages** (`concepts/`) — Ideas, theories, techniques:
```markdown
---
tags: [concept, domain]
sources: [source1.pdf, source2.md]
created: YYYY-MM-DD
---
# Concept Name

Definition and explanation.

## How It Works
Details with [[links]] to related concepts.

## See Also
- [[Related Concept]]
```

**Entity pages** (`entities/`) — People, organizations, products.

**Synthesis pages** (`synthesis/`) — Cross-source analysis:
```markdown
---
tags: [synthesis, topic]
sources: [source1.pdf, source2.md]
created: YYYY-MM-DD
---
# Comparison: X vs Y

## From [[Source A]]
Key perspective.

## From [[Source B]]
Alternative perspective.

## Synthesis
How they connect/differ.
```

### Cross-References
- Always use `[[Page Name]]` when mentioning a topic that has its own page.
- If you mention something important that doesn't have a page yet, still use `[[brackets]]` — the lint tool will flag it as a page that should be created.

## Workflows

### Ingest a new source
1. Call `wiki_ingest` with the file path, URL, or YouTube link
2. Read the returned content carefully
3. Create a source summary page: `wiki_write_page("sources/descriptive-name.md", "...")`
4. Create or update concept/entity pages as needed
5. Add `[[cross-references]]` between related pages
6. Update `wiki/index.md` with new pages
7. Call `wiki_log` to record what you did

### Update existing pages (when new source adds context)
1. Read the existing page with `wiki_read_page`
2. Add new source to the `sources:` frontmatter list
3. Add `updated: YYYY-MM-DD` to frontmatter
4. Integrate new information — don't just append, weave it in
5. Add new `[[cross-references]]` to the new source page
6. If sources disagree, add a "Perspectives" or "Debate" section

### Answer a question
1. Call `wiki_search` with relevant terms
2. Call `wiki_read_page` for the most relevant results
3. Synthesize an answer citing wiki pages: `*Sources: [[page1]], [[page2]]*`
4. If the question reveals a gap, note it for future ingest
5. For complex cross-source questions, create a synthesis page

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
