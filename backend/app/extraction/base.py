from __future__ import annotations

from dataclasses import dataclass


class DocumentProcessingError(ValueError):
    pass


@dataclass(frozen=True)
class DocumentChunk:
    page_number: int | None
    chunk_index: int
    text: str
    locator_type: str
    locator: str
    source_order: int


def chunk_text(text: str, *, max_chars: int = 1200, overlap_chars: int = 160) -> list[str]:
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    if overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError("overlap_chars must be between zero and max_chars")

    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + max_chars, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        next_start = max(start + 1, end - overlap_chars)
        overlap_boundary = normalized.find(" ", next_start, end)
        start = overlap_boundary + 1 if overlap_boundary >= 0 else end
    return chunks