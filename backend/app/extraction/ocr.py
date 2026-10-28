from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

import numpy as np
from rapidocr_onnxruntime import RapidOCR

from .base import DocumentProcessingError


_engine: RapidOCR | None = None
_engine_lock = Lock()


@dataclass(frozen=True)
class OCRResult:
    text: str
    confidence: float | None


def recognize_text_with_confidence(image: np.ndarray) -> OCRResult:
    global _engine
    try:
        with _engine_lock:
            if _engine is None:
                _engine = RapidOCR()
            results, _ = _engine(image)
    except Exception as exc:
        raise DocumentProcessingError("OCR could not process this document.") from exc

    if not results:
        return OCRResult(text="", confidence=None)
    accepted = [
        (str(result[1]).strip(), float(result[2]))
        for result in results
        if len(result) > 2 and float(result[2]) >= 0.35 and str(result[1]).strip()
    ]
    if not accepted:
        return OCRResult(text="", confidence=None)
    return OCRResult(
        text="\n".join(text for text, _ in accepted),
        confidence=round(sum(confidence for _, confidence in accepted) / len(accepted), 3),
    )


def recognize_text(image: np.ndarray) -> str:
    return recognize_text_with_confidence(image).text