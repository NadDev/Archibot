from __future__ import annotations

from io import BytesIO

import fitz
import numpy as np
from pypdf import PdfReader

from .base import DocumentChunk, DocumentProcessingError, chunk_text
from .ocr import recognize_text


MIN_NATIVE_TEXT_CHARS = 24
MAX_OCR_PAGES = 30
OCR_RENDER_SCALE = 2
MAX_OCR_RENDER_PIXELS = 12_000_000


def extract_pdf_chunks(
    pdf_bytes: bytes,
    *,
    max_chars: int = 1200,
    overlap_chars: int = 160,
) -> list[DocumentChunk]:
    if not pdf_bytes:
        raise DocumentProcessingError("The PDF is empty.")

    ocr_document = None
    try:
        reader = PdfReader(BytesIO(pdf_bytes), strict=False)
        if reader.is_encrypted:
            raise DocumentProcessingError("Encrypted PDFs are not supported.")

        chunks: list[DocumentChunk] = []
        ocr_page_count = 0
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if len("".join(text.split())) < MIN_NATIVE_TEXT_CHARS:
                if ocr_document is None:
                    ocr_document = fitz.open(stream=pdf_bytes, filetype="pdf")
                ocr_page_count += 1
                if ocr_page_count > MAX_OCR_PAGES:
                    raise DocumentProcessingError("OCR is limited to 30 scanned pages per PDF.")
                ocr_page = ocr_document.load_page(page_number - 1)
                if ocr_page.rect.width * ocr_page.rect.height * OCR_RENDER_SCALE**2 > MAX_OCR_RENDER_PIXELS:
                    raise DocumentProcessingError("A scanned PDF page exceeds the OCR image size limit.")
                render_matrix = fitz.Matrix(OCR_RENDER_SCALE, OCR_RENDER_SCALE)
                pixmap = ocr_page.get_pixmap(matrix=render_matrix, alpha=False)
                image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
                    pixmap.height, pixmap.width, pixmap.n
                )
                ocr_text = recognize_text(image)
                if ocr_text and ocr_text.casefold() not in text.casefold():
                    text = f"{text}\n{ocr_text}".strip()
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
    finally:
        if ocr_document is not None:
            ocr_document.close()

    if not chunks:
        raise DocumentProcessingError("The PDF contains no extractable text after OCR.")
    return chunks