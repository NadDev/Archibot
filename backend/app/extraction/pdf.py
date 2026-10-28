from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader
from .base import DocumentChunk, DocumentProcessingError, chunk_text


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
                DocumentChunk(
                    page_number=page_number,
                    chunk_index=index,
                    text=chunk,
                    locator_type="page",
                    locator=f"Page {page_number}",
                    source_order=page_number,
                )
                for index, chunk in enumerate(page_chunks, start=1)
            )
    except DocumentProcessingError:
        raise
    except Exception as exc:
        raise DocumentProcessingError("The PDF is invalid or could not be read.") from exc

    if not chunks:
        raise DocumentProcessingError("The PDF contains no extractable text; OCR is required for scans.")
    return chunks