# 📚 llm-wiki-kit

An MCP server that implements [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) - persistent, LLM-maintained knowledge bases that compound over time.

**Instead of RAG** (rediscovering knowledge from scratch on every query), the LLM **incrementally builds and maintains a structured wiki** with interlinked markdown files, cross-references, summaries, and synthesis that get richer with every source you add.

## Why?

The tedious part of maintaining a knowledge base isn't the reading or thinking, it's the bookkeeping. Updating cross-references, keeping summaries current, noting contradictions, maintaining consistency. LLMs are perfect for this. You curate and direct. The LLM does everything else.

## Example use case: The Research Loop

Imagine you are researching a new and complex technology like LLM speculative decoding. Instead of reading 10 papers and taking manual notes, you use `llm-wiki-kit` to let your agent build a state map over time.

### The Workflow

1. Human: drops 3 PDFs into `raw/`
2. Human: "Analyze these papers and update the KB. Pay special attention to KV cache optimizations."
3. Agent (via MCP):
   - Calls `wiki_ingest` for each paper
   - Calls `wiki_write_page` to create `concepts/speculative_decoding.md`
   - Calls `wiki_write_page` to update `synthesis/cache_strategies.md` and link it to the papers
   - Calls `wiki_lint` to ensure the new "Draft Model" concept is cross-referenced with existing "Inference" pages

### The Result

Two weeks later, you start a fresh chat session in Cursor or Claude Code. You do not need to re-upload the papers or re-explain what you learned. You ask:

> "Based on our research so far, which draft model architecture is most efficient for Llama 3?"

Your agent calls `wiki_search`, reads the synthesis pages it wrote earlier, and answers from accumulated evidence:

> "Based on the compiled evidence in your KB, the Eagle architecture is currently leading because..."

## Quick Start

### Install

Requires Python 3.10+.

```bash
# Base install (markdown, text, HTML files)
uv pip install git+https://github.com/iamsashank09/llm-wiki-kit.git

# With PDF support
uv pip install "llm-wiki-kit[pdf] @ git+https://github.com/iamsashank09/llm-wiki-kit.git"

# With web article extraction
uv pip install "llm-wiki-kit[web] @ git+https://github.com/iamsashank09/llm-wiki-kit.git"

# With YouTube transcript support
uv pip install "llm-wiki-kit[youtube] @ git+https://github.com/iamsashank09/llm-wiki-kit.git"

# Everything
uv pip install "llm-wiki-kit[all] @ git+https://github.com/iamsashank09/llm-wiki-kit.git"
```

> **Note:** PyPI publishing is coming soon. For now, install directly from GitHub.

### Initialize a wiki

```bash
mkdir my-research && cd my-research
llm-wiki-kit init --agent claude
```

This creates:
```
my-research/
├── raw/          ← Drop source files here (immutable)
├── wiki/         ← LLM-maintained wiki pages
│   ├── index.md  ← Master index
│   └── log.md    ← Chronological operation log
└── WIKI.md       ← Schema file for your LLM agent
```

### Connect to your LLM agent

#### Claude Desktop / Claude Code

Add to your MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "llm-wiki-kit": {
      "command": "llm-wiki-kit",
      "args": ["serve", "--root", "/path/to/my-research"],
      "env": {}
    }
  }
}
```

#### OpenAI Codex

Add the server with:

```bash
codex mcp add llm-wiki-kit -- llm-wiki-kit serve --root /path/to/my-research
```

Or add it manually to `~/.codex/config.toml`:

```toml
[mcp_servers.llm-wiki-kit]
command = "llm-wiki-kit"
args = ["serve", "--root", "/path/to/my-research"]
```

#### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "llm-wiki-kit": {
      "command": "llm-wiki-kit",
      "args": ["serve", "--root", "/path/to/my-research"]
    }
  }
}
```

#### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "llm-wiki-kit": {
      "command": "llm-wiki-kit",
      "args": ["serve", "--root", "/path/to/my-research"]
    }
  }
}
```

#### Any MCP-compatible agent

```bash
llm-wiki-kit serve --root /path/to/my-research
```

The server uses stdio transport and is compatible with any MCP client.

### Use it

Once connected, your LLM agent has these tools:

| Tool | Description |
|---|---|
| `wiki_init` | Initialize a new wiki |
| `wiki_ingest` | Process a source document |
| `wiki_write_page` | Create/update a wiki page |
| `wiki_read_page` | Read a wiki page |
| `wiki_search` | Full-text search (FTS5) |
| `wiki_lint` | Health-check for issues |
| `wiki_status` | Overview of wiki state |
| `wiki_log` | Append to operation log |

**Example workflow:**

1. Drop an article into `raw/`
2. Tell your agent: *"Ingest raw/article.md"*
3. The agent reads it, creates wiki pages, cross-references related concepts, updates the index
4. Ask questions: *"How does X relate to Y?"* and the agent searches the wiki and synthesizes
5. Periodically: *"Run a lint pass"* to catch broken links, orphan pages, and contradictions

## Supported Formats

`wiki_ingest` auto-detects the source type and extracts content accordingly:

| Format | Input | Extra Dependency |
|---|---|---|
| Markdown / Text | `raw/notes.md` | None |
| HTML | `raw/page.html` | None (basic) or `[web]` (smart) |
| PDF | `raw/paper.pdf` | `pip install 'llm-wiki-kit[pdf]'` |
| Web article | `https://example.com/article` | `pip install 'llm-wiki-kit[web]'` |
| YouTube | `https://youtube.com/watch?v=...` | `pip install 'llm-wiki-kit[youtube]'` |

URL and YouTube sources are automatically saved to `raw/` for persistence. If an optional dependency isn't installed, you get a clear error message telling you exactly what to install.

## Architecture

Three layers, per [Karpathy's design](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):

```
┌─────────────────────────────────────────────┐
│  You (the human)                            │
│  Source, direct, ask questions, think        │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  Wiki (wiki/)                               │
│  LLM-maintained markdown files              │
│  Summaries, entities, concepts, synthesis   │
│  Cross-referenced with [[wiki links]]       │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  Raw Sources (raw/)                         │
│  Articles, papers, notes (immutable)        │
└─────────────────────────────────────────────┘
```

## Search

Wiki pages are indexed using **SQLite FTS5** with Porter stemming, with zero external dependencies and instant setup. Search supports:

- Simple queries: `"attention mechanism"`
- Boolean: `transformer AND attention`
- Negation: `transformer NOT GPT`
- Prefix: `trans*`

## Lint

The lint tool checks for:

- **Broken links:** `[[Page Name]]` references to pages that don't exist
- **Orphan pages:** pages with no inbound links
- **Empty pages:** pages with only a title or no content

## Use Cases

- **Technical onboarding:** Ingest an entire codebase's documentation into a wiki so an agent can answer architecture questions quickly
- **Project state:** Maintain a project wiki where the agent tracks current bugs, architectural decisions, and TODOs across multiple chat sessions
- **Competitive intel:** Feed the agent market reports and let it maintain a living landscape wiki that updates as new data arrives

## Tips

- **Transparency and auditing:** Since the wiki is just a folder of markdown files, you can point any viewer like VS Code, Zed, or [Obsidian](https://obsidian.md/) at the directory to audit the agent's work or visualize its internal knowledge graph. No GUI is required for the agent to function
- The wiki is just markdown files in a git repo, so version history and collaboration come free
- Start small. Even 5-10 sources produce a surprisingly useful wiki
- Let the LLM cross-reference aggressively because the value is in the connections

## Development

```bash
git clone https://github.com/iamsashank09/llm-wiki-kit
cd llm-wiki-kit
uv venv && source .venv/bin/activate
uv pip install -e .
```

## Credits

Based on the [LLM Wiki idea](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) by [Andrej Karpathy](https://karpathy.ai/).

## License

MIT
