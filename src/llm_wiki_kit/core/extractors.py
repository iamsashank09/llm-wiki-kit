"""Content extractors for different source formats.

Each extractor handles a specific format (PDF, URL, YouTube, etc.)
and returns plain text/markdown content for wiki processing.

Optional dependencies are checked at runtime with helpful error messages.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse, parse_qs


@dataclass
class ExtractedContent:
    """Result of extracting content from a source."""

    text: str
    source_type: str
    title: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def content_length(self) -> int:
        return len(self.text)


# --- Source type detection ---

_YOUTUBE_PATTERNS = (
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)",
)


def detect_source_type(source: str) -> str:
    """Detect whether a source is a URL, YouTube link, or file (by extension)."""
    if any(re.search(p, source) for p in _YOUTUBE_PATTERNS):
        return "youtube"

    if source.startswith(("http://", "https://")):
        return "url"

    ext = Path(source).suffix.lower()
    return {
        ".pdf": "pdf",
        ".md": "markdown",
        ".txt": "text",
        ".html": "html",
        ".htm": "html",
    }.get(ext, "text")


# --- Extractors ---

def extract(source: str, wiki_root: Path | None = None) -> ExtractedContent:
    """Extract content from any supported source. Auto-detects type.

    Args:
        source: File path (absolute or relative) or URL.
        wiki_root: Wiki root directory for resolving relative paths.

    Returns:
        ExtractedContent with the extracted text and metadata.
    """
    source_type = detect_source_type(source)

    extractors = {
        "youtube": _extract_youtube,
        "url": _extract_url,
        "pdf": _extract_pdf,
        "markdown": _extract_text_file,
        "text": _extract_text_file,
        "html": _extract_html_file,
    }

    extractor = extractors.get(source_type, _extract_text_file)

    if source_type in ("youtube", "url"):
        return extractor(source)

    # It's a file — resolve the path
    path = Path(source)
    if not path.is_absolute() and wiki_root:
        path = wiki_root / path

    if not path.exists():
        return ExtractedContent(
            text="",
            source_type="error",
            title=str(path),
            metadata={"error": f"File not found: {path}"},
        )

    return extractor(path)


def _extract_text_file(path: Path) -> ExtractedContent:
    """Extract content from a plain text or markdown file."""
    content = path.read_text(errors="replace")
    title = path.stem.replace("-", " ").replace("_", " ").title()

    # Try to get title from first heading
    first_heading = re.match(r"^#\s+(.+)$", content, re.MULTILINE)
    if first_heading:
        title = first_heading.group(1).strip()

    return ExtractedContent(
        text=content,
        source_type="markdown" if path.suffix == ".md" else "text",
        title=title,
        metadata={"file_name": path.name, "file_size": path.stat().st_size},
    )


def _extract_html_file(path: Path) -> ExtractedContent:
    """Extract content from a local HTML file using trafilatura if available."""
    raw_html = path.read_text(errors="replace")
    text = _html_to_text(raw_html)

    title = path.stem.replace("-", " ").replace("_", " ").title()
    title_match = re.search(r"<title>(.+?)</title>", raw_html, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()

    return ExtractedContent(
        text=text,
        source_type="html",
        title=title,
        metadata={"file_name": path.name},
    )


def _extract_pdf(path: Path) -> ExtractedContent:
    """Extract text from a PDF file using pymupdf."""
    try:
        import pymupdf  # noqa: F811
    except ImportError:
        return ExtractedContent(
            text="",
            source_type="error",
            title=path.name,
            metadata={
                "error": (
                    "PDF support requires pymupdf. Install with:\n"
                    "  pip install 'llm-wiki-kit[pdf]'\n"
                    "  # or: pip install pymupdf"
                )
            },
        )

    pages_text = []
    metadata = {"file_name": path.name, "file_size": path.stat().st_size}

    with pymupdf.open(str(path)) as doc:
        metadata["page_count"] = len(doc)
        metadata["pdf_title"] = doc.metadata.get("title", "")
        metadata["pdf_author"] = doc.metadata.get("author", "")

        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            if text.strip():
                pages_text.append(f"<!-- Page {page_num} -->\n{text}")

    title = metadata["pdf_title"] or path.stem.replace("-", " ").replace("_", " ").title()
    full_text = "\n\n".join(pages_text)

    return ExtractedContent(
        text=full_text,
        source_type="pdf",
        title=title,
        metadata=metadata,
    )


def _extract_url(url: str) -> ExtractedContent:
    """Extract article content from a web URL using trafilatura."""
    try:
        import trafilatura
    except ImportError:
        return ExtractedContent(
            text="",
            source_type="error",
            title=url,
            metadata={
                "error": (
                    "Web URL support requires trafilatura. Install with:\n"
                    "  pip install 'llm-wiki-kit[web]'\n"
                    "  # or: pip install trafilatura"
                )
            },
        )

    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ExtractedContent(
                text="",
                source_type="error",
                title=url,
                metadata={"error": f"Failed to download: {url}"},
            )

        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            output_format="txt",
        ) or ""

        title = url
        title_match = re.search(r"<title[^>]*>(.+?)</title>", downloaded, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()

        return ExtractedContent(
            text=text,
            source_type="url",
            title=title,
            metadata={"url": url},
        )

    except Exception as e:
        return ExtractedContent(
            text="",
            source_type="error",
            title=url,
            metadata={"error": f"Failed to extract from {url}: {e}"},
        )


def _extract_youtube(url: str) -> ExtractedContent:
    """Extract transcript from a YouTube video."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return ExtractedContent(
            text="",
            source_type="error",
            title=url,
            metadata={
                "error": (
                    "YouTube support requires youtube-transcript-api. Install with:\n"
                    "  pip install 'llm-wiki-kit[youtube]'\n"
                    "  # or: pip install youtube-transcript-api"
                )
            },
        )

    video_id = _extract_youtube_id(url)
    if not video_id:
        return ExtractedContent(
            text="",
            source_type="error",
            title=url,
            metadata={"error": f"Could not extract video ID from: {url}"},
        )

    try:
        transcript_entries = YouTubeTranscriptApi.get_transcript(video_id)
        lines = [entry["text"] for entry in transcript_entries]
        text = " ".join(lines)

        # Build timestamped version for metadata
        timestamped = []
        for entry in transcript_entries:
            mins, secs = divmod(int(entry["start"]), 60)
            timestamped.append(f"[{mins:02d}:{secs:02d}] {entry['text']}")

        return ExtractedContent(
            text=text,
            source_type="youtube",
            title=f"YouTube: {video_id}",
            metadata={
                "video_id": video_id,
                "url": url,
                "timestamped_transcript": "\n".join(timestamped),
                "segment_count": len(transcript_entries),
            },
        )

    except Exception as e:
        return ExtractedContent(
            text="",
            source_type="error",
            title=url,
            metadata={"error": f"Failed to get transcript for {video_id}: {e}"},
        )


def _extract_youtube_id(url: str) -> str | None:
    """Extract the video ID from various YouTube URL formats."""
    parsed = urlparse(url)

    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/")

    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/")[2]

    return None


def _html_to_text(html: str) -> str:
    """Convert HTML to plain text. Uses trafilatura if available, else regex."""
    try:
        import trafilatura
        result = trafilatura.extract(html, include_tables=True, output_format="txt")
        if result:
            return result
    except ImportError:
        pass

    # Fallback: basic regex stripping
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
