from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory

from ebooklib import ITEM_DOCUMENT, epub

from .base import DocumentChunk, DocumentProcessingError, chunk_text
from .package import validate_office_archive


class _ChapterText(HTMLParser):
    _BLOCK_TAGS = {"address", "article", "blockquote", "br", "dd", "div", "dt", "h1", "h2", "h3", "h4", "h5", "h6", "li", "p", "pre", "section", "tr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self._title_depth = 0
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "svg"}:
            self._ignored_depth += 1
        elif tag in {"title", "h1", "h2", "h3"}:
            self._title_depth += 1
        elif tag in self._BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "svg"} and self._ignored_depth:
            self._ignored_depth -= 1
        elif tag in {"title", "h1", "h2", "h3"} and self._title_depth:
            self._title_depth -= 1
        elif tag in self._BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        if self._title_depth:
            self.title_parts.append(data.strip())
        self.parts.append(data)


def extract_epub_chunks(data: bytes) -> list[DocumentChunk]:
    if not data:
        raise DocumentProcessingError("The EPUB is empty.")
    validate_office_archive(data, "META-INF/container.xml")
    try:
        with TemporaryDirectory() as temporary_directory:
            epub_path = Path(temporary_directory) / "document.epub"
            epub_path.write_bytes(data)
            book = epub.read_epub(str(epub_path), options={"ignore_ncx": True})
        chunks: list[DocumentChunk] = []
        chapter_order = 0
        for entry in book.spine:
            item_id = entry[0] if isinstance(entry, tuple) else entry
            item = book.get_item_with_id(item_id)
            if item is None or item.get_type() != ITEM_DOCUMENT:
                continue
            parser = _ChapterText()
            parser.feed(item.get_content().decode("utf-8-sig", errors="replace"))
            text = " ".join("".join(parser.parts).split())
            chapter_order += 1
            title = " ".join(" ".join(parser.title_parts).split()) or item.get_name()
            locator = f"Chapitre {chapter_order}: {title} ({item.get_name()})"[:500]
            chunks.extend(
                DocumentChunk(
                    page_number=None,
                    chunk_index=index,
                    text=chunk,
                    locator_type="chapter",
                    locator=locator,
                    source_order=chapter_order,
                )
                for index, chunk in enumerate(chunk_text(text), start=1)
            )
    except Exception as exc:
        raise DocumentProcessingError("The EPUB is invalid or could not be read.") from exc
    if not chunks:
        raise DocumentProcessingError("The EPUB contains no extractable text.")
    return chunks