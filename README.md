# 📚 llm-wiki-kit

### Stop re-explaining your research to your AI agent every session.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

**llm-wiki-kit** gives your AI agent a persistent, structured memory that compounds over time. Drop PDFs, URLs, YouTube videos — your agent builds a wiki, connects the dots, and remembers everything across sessions.

Based on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Works with Claude, Codex, Cursor, Windsurf, and any MCP-compatible agent.



https://github.com/user-attachments/assets/8814a581-1832-4e94-a5df-9e9b6b041507



---

## The Problem

Every time you start a new chat:

```
You: "Remember that paper on speculative decoding I shared last week?"
Agent: "I don't have access to previous conversations..."
You: *sighs, re-uploads PDF, re-explains context*
```

You're constantly **re-teaching** your agent things it should already know.

## The Solution

With llm-wiki-kit, your agent maintains its own knowledge base:

```
You: "What did we learn about speculative decoding?"
Agent: *searches wiki* "Based on the 3 papers you've shared, the Eagle 
       architecture shows the best efficiency tradeoffs because..."
```

**The wiki persists.** Cross-references build up. Your agent gets smarter with every source you add.

---

## ⚡ Quickstart (2 minutes)

### 1. Install

```bash
pip install "llm-wiki-kit[all] @ git+https://github.com/iamsashank09/llm-wiki-kit.git"
```

### 2. Initialize a wiki

```bash
mkdir my-research && cd my-research
llm-wiki-kit init --agent claude
```

### 3. Connect your agent

Add to Claude Desktop config (`claude_desktop_config.json`):

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

<details>
<summary><b>Other agents (Codex, Cursor, Windsurf)</b></summary>

#### OpenAI Codex
```bash
codex mcp add llm-wiki-kit -- llm-wiki-kit serve --root /path/to/my-research
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

</details>

### 4. Use it

```
You: "Ingest this paper: raw/attention-is-all-you-need.pdf"
Agent: *creates wiki pages, cross-references concepts, updates index*

You: "Now ingest https://youtube.com/watch?v=kCc8FmEb1nY"
Agent: *extracts transcript, links to existing transformer concepts*

You: "How does the attention mechanism in the paper relate to Karpathy's explanation?"
Agent: *searches wiki, synthesizes answer from both sources*
```

Your agent now has **persistent memory** that survives across sessions.

---

## 🔥 What Makes This Different

| Feature | Why It Matters |
|---|---|
| **Multi-format ingest** | PDFs, URLs, YouTube, markdown — just drop it in |
| **Auto cross-referencing** | Agent builds `[[wiki links]]` between related concepts |
| **Persistent across sessions** | Start fresh chats without losing context |
| **Full-text search** | Agent finds relevant pages instantly (SQLite FTS5) |
| **Health checks** | `wiki_lint` catches broken links, orphan pages, contradictions |
| **Graph visualization** | `wiki_graph` generates an interactive HTML map of your knowledge (see below) |
| **Zero lock-in** | It's just markdown files in a folder — view in Obsidian, VS Code, anywhere |
| **Works with any MCP agent** | Claude, Codex, Cursor, Windsurf, and more |

---

## 📥 Supported Sources

Your agent can ingest anything:

| Drop this... | Get this... |
|---|---|
| `raw/paper.pdf` | Extracted text, page markers, metadata |
| `https://arxiv.org/abs/...` | Clean article content, auto-saved to `raw/` |
| `https://youtube.com/watch?v=...` | Full transcript with timestamps |
| `raw/notes.md` | Direct markdown ingestion |

Install what you need:
```bash
pip install "llm-wiki-kit[pdf]"      # PDF support
pip install "llm-wiki-kit[web]"      # URL extraction  
pip install "llm-wiki-kit[youtube]"  # YouTube transcripts
pip install "llm-wiki-kit[all]"      # Everything
```

---

## 🧠 How It Works

```
┌─────────────────────────────────────────────────────────┐
│  YOU                                                    │
│  "Ingest this paper. How does it relate to X?"         │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│  WIKI (agent-maintained)                                │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ concepts/    │  │ sources/     │  │ synthesis/   │  │
│  │ attention.md │◄─┤ paper-1.md   │──► cache.md     │  │
│  │ [[linked]]   │  │ [[linked]]   │  │ [[linked]]   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  + index.md (table of contents)                        │
│  + log.md (what happened when)                         │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│  RAW SOURCES (immutable)                                │
│  paper.pdf, article.html, transcript.md                 │
└─────────────────────────────────────────────────────────┘
```

The agent reads raw sources, writes wiki pages, and maintains the connections. You never touch the wiki directly — the agent does all the work.

---

## 📊 Knowledge Graph

`wiki_graph` generates an interactive HTML visualization of your wiki's structure:

<img width="1918" height="908" alt="llm-wiki-kit-graph" src="https://github.com/user-attachments/assets/66ae92e0-f1c9-479c-bcb2-76da9af38b1f" />


Nodes are color-coded by type (sources, concepts, synthesis). Click and drag to explore connections.

---

## 🛠 Available Tools

Your agent gets these MCP tools:

| Tool | What it does |
|---|---|
| `wiki_ingest` | Process any source (file, URL, YouTube) |
| `wiki_write_page` | Create or update a wiki page |
| `wiki_read_page` | Read a specific page |
| `wiki_search` | Full-text search across all pages |
| `wiki_lint` | Find broken links, orphans, empty pages |
| `wiki_status` | Overview: page count, sources, recent activity |
| `wiki_log` | Append to the operation log |
| `wiki_graph` | Generate interactive HTML graph visualization |

---

## 💡 Use Cases

**Research**: Feed papers into your wiki over weeks. Ask synthesis questions that span all your reading.

**Technical onboarding**: Ingest a codebase's docs. Your agent answers architecture questions from accumulated context.

**Competitive intel**: Add market reports, earnings calls, news. Agent maintains a living landscape that updates as you add more.

**Learning**: Watch YouTube tutorials, read blog posts. Agent builds a personalized wiki of everything you've studied.

**Book notes**: Ingest chapters as you read. Agent tracks characters, themes, plot threads, and connections.

---

## 🔍 Pro Tips

- **Use Obsidian** to visualize your wiki's graph — it's just a folder of markdown files
- **Git init** your wiki directory — get version history for free
- **Let the agent link aggressively** — the value compounds in the connections
- **Run lint periodically** — catches contradictions and gaps in your knowledge base
- **Start small** — even 5-10 sources produce a surprisingly useful wiki

---

## 📦 Development

```bash
git clone https://github.com/iamsashank09/llm-wiki-kit
cd llm-wiki-kit
uv venv && source .venv/bin/activate
uv pip install -e ".[all]"
```

---

## 🙏 Credits

Based on the [LLM Wiki idea](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) by [Andrej Karpathy](https://karpathy.ai/).

## 📄 License

MIT — do whatever you want with it.
