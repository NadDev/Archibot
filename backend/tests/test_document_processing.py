from __future__ import annotations

import pytest

from app.document_processing import (
    DocumentProcessingError,
    chunk_text,
    extract_pdf_chunks,
)


def _pdf_with_text(text: str) -> bytes:
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(content)} >>\nstream\n".encode("ascii") + content + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for object_number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets:
        pdf.extend(f"{offset:010} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("ascii")
    )
    return bytes(pdf)


def test_extract_pdf_text_preserves_page_and_chunk_references() -> None:
    chunks = extract_pdf_chunks(
        _pdf_with_text("Architecture course reference supports spatial design choices"),
        max_chars=24,
        overlap_chars=6,
    )

    assert len(chunks) > 1
    assert all(chunk.page_number == 1 for chunk in chunks)
    assert [chunk.chunk_index for chunk in chunks] == list(range(1, len(chunks) + 1))
    assert all(chunk.text for chunk in chunks)
    assert all(len(chunk.text) <= 24 for chunk in chunks)


def test_chunk_text_returns_empty_for_whitespace() -> None:
    assert chunk_text("  \n\t  ") == []


@pytest.mark.parametrize(
    ("max_chars", "overlap_chars"),
    [(0, 0), (10, -1), (10, 10)],
)
def test_chunk_text_rejects_invalid_limits(max_chars: int, overlap_chars: int) -> None:
    with pytest.raises(ValueError):
        chunk_text("some text", max_chars=max_chars, overlap_chars=overlap_chars)


@pytest.mark.parametrize(
    ("pdf_bytes", "message"),
    [
        (b"", "empty"),
        (b"not a pdf", "invalid"),
        (_pdf_with_text(""), "no extractable text"),
    ],
)
def test_extract_pdf_rejects_empty_invalid_or_scanned_documents(pdf_bytes: bytes, message: str) -> None:
    with pytest.raises(DocumentProcessingError, match=message):
        extract_pdf_chunks(pdf_bytes)