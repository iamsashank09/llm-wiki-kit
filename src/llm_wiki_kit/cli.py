"""CLI entry point for llm-wiki-kit."""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="llm-wiki-kit",
        description="LLM Wiki Kit — an MCP server for persistent, LLM-maintained knowledge bases.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # serve command
    serve_parser = subparsers.add_parser(
        "serve", help="Start the MCP server (stdio transport)"
    )
    serve_parser.add_argument(
        "--root",
        default=".",
        help="Wiki root directory (default: current directory)",
    )

    # init command (convenience — can also use MCP tool)
    init_parser = subparsers.add_parser(
        "init", help="Initialize a new wiki in the current directory"
    )
    init_parser.add_argument(
        "--agent",
        default="claude",
        choices=["claude", "codex", "cursor", "generic"],
        help="LLM agent to generate schema for",
    )
    init_parser.add_argument(
        "--root",
        default=".",
        help="Directory to initialize the wiki in",
    )

    args = parser.parse_args()

    if args.command == "serve":
        _serve(args.root)
    elif args.command == "init":
        _init(args.root, args.agent)
    else:
        parser.print_help()
        sys.exit(1)


def _serve(root: str) -> None:
    import os

    os.environ["LLM_WIKI_ROOT"] = str(root)

    from llm_wiki_kit.server import mcp

    mcp.run(transport="stdio")


def _init(root: str, agent: str) -> None:
    from pathlib import Path

    from llm_wiki_kit.core.wiki import Wiki

    wiki = Wiki(Path(root))
    result = wiki.init(agent=agent)
    print(result)


if __name__ == "__main__":
    main()
