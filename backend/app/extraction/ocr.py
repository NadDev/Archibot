from __future__ import annotations

from threading import Lock

import numpy as np
from rapidocr_onnxruntime import RapidOCR

from .base import DocumentProcessingError


_engine: RapidOCR | None = None
_engine_lock = Lock()


def recognize_text(image: np.ndarray) -> str:
    global _engine
    try:
        with _engine_lock:
            if _engine is None:
                _engine = RapidOCR()
            results, _ = _engine(image)
    except Exception as exc:
        raise DocumentProcessingError("OCR could not process this document.") from exc

    if not results:
        return ""
    return "\n".join(
        text.strip()
        for result in results
        if len(result) > 2 and float(result[2]) >= 0.35
        if (text := str(result[1]).strip())
    )