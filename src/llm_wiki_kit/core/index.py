"""SQLite FTS5-powered search index for wiki pages."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class SearchIndex:
    """Full-text search over wiki pages using SQLite FTS5."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self.initialize()
        return self._conn

    def initialize(self) -> None:
        """Create the FTS5 table if it doesn't exist."""
        self.conn.executescript("""
            CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                page_name,
                content,
                tokenize='porter unicode61'
            );
        """)
        self.conn.commit()

    def upsert_page(self, page_name: str, content: str) -> None:
        """Insert or update a page in the search index."""
        self.conn.execute(
            "DELETE FROM pages_fts WHERE page_name = ?",
            (page_name,),
        )
        self.conn.execute(
            "INSERT INTO pages_fts (page_name, content) VALUES (?, ?)",
            (page_name, content),
        )
        self.conn.commit()

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search for pages matching the query."""
        if not query.strip():
            return []

        try:
            rows = self.conn.execute(
                """
                SELECT page_name, snippet(pages_fts, 1, '**', '**', '...', 32) as snippet,
                       rank
                FROM pages_fts
                WHERE pages_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            # If FTS match syntax fails, try a simple LIKE fallback
            rows = self.conn.execute(
                """
                SELECT page_name, substr(content, 1, 200) as snippet, 0 as rank
                FROM pages_fts
                WHERE content LIKE ?
                LIMIT ?
                """,
                (f"%{query}%", limit),
            ).fetchall()

        return [
            {
                "page_name": row["page_name"],
                "snippet": row["snippet"],
                "score": abs(row["rank"]),
            }
            for row in rows
        ]

    def delete_page(self, page_name: str) -> None:
        """Remove a page from the search index."""
        self.conn.execute(
            "DELETE FROM pages_fts WHERE page_name = ?",
            (page_name,),
        )
        self.conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
