"""MCP server for llm-wiki-kit — exposes wiki operations as tools."""

from __future__ import annotations

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from llm_wiki_kit.core.wiki import Wiki

mcp = FastMCP(
    "llm-wiki-kit",
    instructions=(
        "LLM Wiki — a persistent, LLM-maintained knowledge base. "
        "Use these tools to build and maintain a structured wiki from raw sources. "
        "The wiki compounds over time: cross-references, summaries, and synthesis "
        "are all maintained by you through these tools."
    ),
)


def _get_wiki() -> Wiki:
    """Get the Wiki instance from the configured root directory."""
    root = os.environ.get("LLM_WIKI_ROOT", os.getcwd())
    return Wiki(Path(root))


@mcp.tool()
def wiki_init(agent: str = "claude") -> str:
    """Initialize a new LLM Wiki in the current directory.

    Creates the directory structure (raw/, wiki/), the index, log,
    and a schema file tailored to your LLM agent.

    Args:
        agent: Which LLM agent you're using. Options: claude, codex, cursor, generic.
    """
    wiki = _get_wiki()
    return wiki.init(agent=agent)


@mcp.tool()
def wiki_ingest(file_path: str) -> dict:
    """Ingest a source document into the wiki.

    Reads the source file and returns its content along with the current
    wiki index. You should then create/update wiki pages based on the content.

    Args:
        file_path: Path to the source file (absolute, or relative to wiki root).
    """
    wiki = _get_wiki()
    return wiki.ingest_source(file_path)


@mcp.tool()
def wiki_write_page(page_name: str, content: str) -> str:
    """Create or update a wiki page.

    The page will be indexed for full-text search. Use [[Page Name]] syntax
    in your content to create cross-references between pages.

    Args:
        page_name: Name of the page (e.g. 'transformers' or 'concepts/attention.md').
        content: Full markdown content of the page.
    """
    wiki = _get_wiki()
    return wiki.write_page(page_name, content)


@mcp.tool()
def wiki_read_page(page_name: str) -> dict:
    """Read a wiki page.

    Args:
        page_name: Name of the page to read (e.g. 'transformers' or 'index').
    """
    wiki = _get_wiki()
    return wiki.read_page(page_name)


@mcp.tool()
def wiki_search(query: str, limit: int = 10) -> list[dict]:
    """Search the wiki using full-text search.

    Returns matching pages with snippets and relevance scores.

    Args:
        query: Search query (supports FTS5 syntax: AND, OR, NOT, "phrases").
        limit: Maximum number of results to return.
    """
    wiki = _get_wiki()
    return wiki.search(query, limit)


@mcp.tool()
def wiki_lint() -> dict:
    """Health-check the wiki for issues.

    Checks for: broken [[links]], orphan pages (no inbound links),
    empty pages, and other structural issues.
    """
    wiki = _get_wiki()
    return wiki.lint()


@mcp.tool()
def wiki_status() -> dict:
    """Get an overview of the wiki — page count, source count, recent activity."""
    wiki = _get_wiki()
    return wiki.status()


@mcp.tool()
def wiki_log(operation: str, details: str) -> str:
    """Append an entry to the wiki's chronological log.

    Use this after ingesting sources, making significant updates,
    or completing lint passes.

    Args:
        operation: Type of operation (e.g. 'ingest', 'update', 'lint', 'query').
        details: Description of what was done.
    """
    wiki = _get_wiki()
    return wiki.append_log(operation, details)
