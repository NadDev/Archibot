from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader


class DocumentProcessingError(ValueError):
    pass


@dataclass(frozen=True)
class DocumentChunk:
    page_number: int
    chunk_index: int
    text: str


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


def extract_pdf_chunks(
    pdf_bytes: bytes,
    *,
    max_chars: int = 1200,
    overlap_chars: int = 160,
) -> list[DocumentChunk]:
    if not pdf_bytes:
        raise DocumentProcessingError("The PDF is empty.")

    try:
        reader = PdfReader(BytesIO(pdf_bytes), strict=False)
        if reader.is_encrypted:
            raise DocumentProcessingError("Encrypted PDFs are not supported.")

        chunks: list[DocumentChunk] = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            page_chunks = chunk_text(text, max_chars=max_chars, overlap_chars=overlap_chars)
            chunks.extend(
                DocumentChunk(page_number=page_number, chunk_index=index, text=chunk)
                for index, chunk in enumerate(page_chunks, start=1)
            )
    except DocumentProcessingError:
        raise
    except Exception as exc:
        raise DocumentProcessingError("The PDF is invalid or could not be read.") from exc

    if not chunks:
        raise DocumentProcessingError("The PDF contains no extractable text; OCR is required for scans.")
    return chunks