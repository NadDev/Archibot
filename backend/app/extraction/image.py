from __future__ import annotations

from io import BytesIO
import warnings

import numpy as np
from PIL import Image, ImageOps

from .base import DocumentChunk, DocumentProcessingError, chunk_text
from .ocr import recognize_text_with_confidence


MAX_IMAGE_PIXELS = 20_000_000


def extract_image_chunks(
    image_bytes: bytes,
    document_format: str,
    *,
    max_chars: int = 1200,
    overlap_chars: int = 160,
    report: dict[str, object] | None = None,
) -> list[DocumentChunk]:
    if not image_bytes:
        raise DocumentProcessingError("The image is empty.")
    if document_format not in {"png", "jpeg", "webp"}:
        raise DocumentProcessingError("This image format is not supported.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(image_bytes)) as opened_image:
                expected_format = "JPEG" if document_format == "jpeg" else document_format.upper()
                if opened_image.format != expected_format:
                    raise DocumentProcessingError("The image content does not match its file format.")
                if getattr(opened_image, "n_frames", 1) != 1:
                    raise DocumentProcessingError("Animated images are not supported.")
                if opened_image.width * opened_image.height > MAX_IMAGE_PIXELS:
                    raise DocumentProcessingError("The image dimensions exceed the supported limit.")
                image = ImageOps.exif_transpose(opened_image).convert("RGB")
                try:
                    ocr_result = recognize_text_with_confidence(np.asarray(image))
                except DocumentProcessingError as exc:
                    if report is not None:
                        report["pages"] = [{
                            "locator_type": "image",
                            "locator": "Image",
                            "confidence": None,
                            "character_count": 0,
                            "error": str(exc)[:300],
                        }]
                    raise
                text = ocr_result.text
    except DocumentProcessingError:
        raise
    except Exception as exc:
        raise DocumentProcessingError("The image is invalid or could not be read.") from exc

    if report is not None:
        report["source_count"] = 1
        report["pages"] = [{
            "locator_type": "image",
            "locator": "Image",
            "confidence": ocr_result.confidence,
            "character_count": len(text),
            "error": None if text else "No readable text detected.",
        }]
    chunks = chunk_text(text, max_chars=max_chars, overlap_chars=overlap_chars)
    if not chunks:
        raise DocumentProcessingError("The image contains no readable text.")
    return [
        DocumentChunk(
            page_number=None,
            chunk_index=index,
            text=chunk,
            locator_type="image",
            locator="Image",
            source_order=1,
        )
        for index, chunk in enumerate(chunks, start=1)
    ]