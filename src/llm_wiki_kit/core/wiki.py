"""Core Wiki class — manages the wiki directory structure and operations."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from llm_wiki_kit.core.index import SearchIndex

# Directory layout constants
RAW_DIR = "raw"
WIKI_DIR = "wiki"
INDEX_FILE = "wiki/index.md"
LOG_FILE = "wiki/log.md"
SCHEMA_FILE = "WIKI.md"
DB_FILE = ".llm-wiki-kit.db"


class Wiki:
    """Represents an LLM Wiki instance rooted at a directory."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.raw_dir = self.root / RAW_DIR
        self.wiki_dir = self.root / WIKI_DIR
        self.index_file = self.root / INDEX_FILE
        self.log_file = self.root / LOG_FILE
        self.schema_file = self.root / SCHEMA_FILE
        self.db_path = self.root / DB_FILE
        self._search_index: SearchIndex | None = None

    @property
    def search_index(self) -> SearchIndex:
        if self._search_index is None:
            self._search_index = SearchIndex(self.db_path)
        return self._search_index

    @property
    def is_initialized(self) -> bool:
        return self.wiki_dir.exists() and self.schema_file.exists()

    def init(self, agent: str = "claude") -> str:
        """Initialize the wiki directory structure."""
        if self.is_initialized:
            return f"Wiki already initialized at {self.root}"

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.wiki_dir.mkdir(parents=True, exist_ok=True)

        self.index_file.write_text(
            "# Wiki Index\n\n"
            "_This index is maintained by the LLM. "
            "Each page is listed with a link and one-line summary._\n\n"
            "## Pages\n\n"
            "_No pages yet. Ingest a source to get started._\n"
        )

        self.log_file.write_text(
            "# Wiki Log\n\n"
            "_Chronological record of wiki operations._\n\n"
            f"## [{_now()}] init | Wiki initialized\n\n"
            f"Agent: {agent}\n"
        )

        schema_content = _load_schema_template(agent)
        self.schema_file.write_text(schema_content)

        self.search_index.initialize()

        return (
            f"Wiki initialized at {self.root}\n"
            f"  raw/     → drop source files here\n"
            f"  wiki/    → LLM-maintained wiki pages\n"
            f"  WIKI.md  → schema for {agent}\n"
        )

    def ingest_source(self, file_path: str) -> dict:
        """Register a source file and return its content for LLM processing."""
        source = Path(file_path)

        # Accept absolute paths or paths relative to wiki root
        if not source.is_absolute():
            source = self.root / source

        if not source.exists():
            return {"error": f"File not found: {source}"}

        content = source.read_text(errors="replace")

        # Get current wiki state for context
        index_content = ""
        if self.index_file.exists():
            index_content = self.index_file.read_text()

        self.append_log("ingest", f"Source: {source.name}")

        return {
            "source_name": source.name,
            "source_path": str(source),
            "content": content,
            "content_length": len(content),
            "current_index": index_content,
            "instructions": (
                "You have received a new source document. Please:\n"
                "1. Read and understand the content\n"
                "2. Create/update relevant wiki pages using wiki_write_page\n"
                "3. Update the index using wiki_write_page for 'index.md'\n"
                "4. Add cross-references ([[Page Name]]) between related pages\n"
                "5. Log what you did using wiki_log"
            ),
        }

    def write_page(self, page_name: str, content: str) -> str:
        """Write or update a wiki page and re-index it."""
        if not page_name.endswith(".md"):
            page_name += ".md"

        page_path = self.wiki_dir / page_name
        page_path.parent.mkdir(parents=True, exist_ok=True)

        is_update = page_path.exists()
        page_path.write_text(content)

        # Index for search
        self.search_index.upsert_page(page_name, content)

        action = "Updated" if is_update else "Created"
        return f"{action} wiki/{page_name} ({len(content)} chars)"

    def read_page(self, page_name: str) -> dict:
        """Read a wiki page."""
        if not page_name.endswith(".md"):
            page_name += ".md"

        page_path = self.wiki_dir / page_name
        if not page_path.exists():
            return {"error": f"Page not found: wiki/{page_name}"}

        return {
            "page_name": page_name,
            "content": page_path.read_text(),
        }

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Full-text search across wiki pages."""
        return self.search_index.search(query, limit)

    def lint(self) -> dict:
        """Health-check the wiki for issues."""
        issues: list[dict] = []
        pages = list(self.wiki_dir.glob("**/*.md"))

        # Collect all page names (without .md) for cross-ref checking
        page_names = {p.stem.lower() for p in pages}

        # Track inbound links per page
        inbound_links: dict[str, int] = {p.stem.lower(): 0 for p in pages}
        # Don't count index and log as orphans
        meta_pages = {"index", "log"}

        for page_path in pages:
            content = page_path.read_text()
            name = page_path.stem.lower()

            # Check for empty pages
            stripped = content.strip()
            if not stripped or stripped == f"# {page_path.stem}":
                issues.append({
                    "type": "empty_page",
                    "page": page_path.stem,
                    "message": "Page is empty or has only a title",
                })

            # Find [[wiki links]] and check they resolve
            links = re.findall(r"\[\[([^\]]+)\]\]", content)
            for link in links:
                link_lower = link.lower()
                if link_lower in inbound_links:
                    inbound_links[link_lower] += 1
                if link_lower not in page_names:
                    issues.append({
                        "type": "broken_link",
                        "page": page_path.stem,
                        "link": link,
                        "message": f"Links to [[{link}]] but no such page exists",
                    })

        # Check for orphan pages (no inbound links, not index/log)
        for page_name, count in inbound_links.items():
            if count == 0 and page_name not in meta_pages:
                issues.append({
                    "type": "orphan_page",
                    "page": page_name,
                    "message": "No other page links to this page",
                })

        return {
            "total_pages": len(pages),
            "issue_count": len(issues),
            "issues": issues,
            "summary": (
                f"Found {len(issues)} issue(s) across {len(pages)} pages"
            ),
        }

    def status(self) -> dict:
        """Get an overview of the wiki state."""
        if not self.is_initialized:
            return {"initialized": False, "message": "Wiki not initialized. Run wiki_init first."}

        pages = list(self.wiki_dir.glob("**/*.md"))
        sources = list(self.raw_dir.glob("**/*"))
        sources = [s for s in sources if s.is_file()]

        # Get recent log entries
        recent_log = ""
        if self.log_file.exists():
            log_lines = self.log_file.read_text().strip().split("\n")
            recent_log = "\n".join(log_lines[-20:])

        return {
            "initialized": True,
            "root": str(self.root),
            "page_count": len(pages),
            "source_count": len(sources),
            "pages": [p.stem for p in pages],
            "sources": [s.name for s in sources],
            "recent_log": recent_log,
        }

    def append_log(self, operation: str, details: str) -> str:
        """Append an entry to the wiki log."""
        entry = f"\n## [{_now()}] {operation} | {details}\n"
        if self.log_file.exists():
            with open(self.log_file, "a") as f:
                f.write(entry)
        return f"Logged: {operation} | {details}"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")


def _load_schema_template(agent: str) -> str:
    """Load a schema template for the given agent."""
    templates_dir = Path(__file__).parent.parent / "templates"
    template_file = templates_dir / f"{agent.upper()}.md"

    if template_file.exists():
        return template_file.read_text()

    # Fallback to generic
    generic = templates_dir / "GENERIC.md"
    if generic.exists():
        return generic.read_text()

    return _default_schema(agent)


def _default_schema(agent: str) -> str:
    return f"""\
# LLM Wiki Schema

> Auto-generated for: {agent}

## Directory Structure

- `raw/` — Source documents. Immutable. Never modify these.
- `wiki/` — LLM-maintained wiki pages. You own this directory entirely.
- `wiki/index.md` — Master index of all pages with one-line summaries.
- `wiki/log.md` — Chronological log of all operations.

## Conventions

### Page Format
- Each page starts with a `# Title` header
- Use `[[Page Name]]` for cross-references to other wiki pages
- Add YAML frontmatter for metadata when useful:
  ```yaml
  ---
  tags: [concept, important]
  sources: [article.md, paper.pdf]
  created: 2025-01-01
  updated: 2025-01-15
  ---
  ```

### Page Types
- **Source summaries** — one per ingested source, key takeaways
- **Entity pages** — people, organizations, products
- **Concept pages** — ideas, theories, patterns
- **Comparison pages** — structured comparisons between entities/concepts
- **Synthesis pages** — cross-cutting analysis across multiple sources

### Workflows

#### Ingest
1. Use `wiki_ingest` to read the source
2. Create a source summary page
3. Create/update entity and concept pages as needed
4. Add `[[cross-references]]` between related pages
5. Update `index.md`
6. Log the operation with `wiki_log`

#### Query
1. Use `wiki_search` to find relevant pages
2. Read the pages with `wiki_read_page`
3. Synthesize an answer with citations to wiki pages

#### Lint
1. Run `wiki_lint` periodically
2. Fix broken links, flesh out empty pages
3. Create pages for frequently-referenced but missing topics
4. Resolve contradictions between pages
"""
