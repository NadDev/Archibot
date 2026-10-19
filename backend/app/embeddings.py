from __future__ import annotations

from math import isfinite
from typing import Any, Sequence

from fastembed import TextEmbedding


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSIONS = 384


class EmbeddingProviderError(RuntimeError):
    pass


class FastEmbedEmbeddingProvider:
    def __init__(
        self,
        *,
        model: str = DEFAULT_EMBEDDING_MODEL,
        encoder: Any | None = None,
    ) -> None:
        self._encoder = encoder or TextEmbedding(model_name=model)

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        normalized_texts = [text.strip() for text in texts]
        if not normalized_texts or any(not text for text in normalized_texts):
            raise ValueError("Embedding inputs must contain non-empty text.")

        try:
            embeddings = [
                [float(value) for value in vector]
                for vector in self._encoder.embed(normalized_texts)
            ]
        except Exception as exc:
            raise EmbeddingProviderError("Local embedding generation failed.") from exc

        if len(embeddings) != len(normalized_texts):
            raise EmbeddingProviderError("FastEmbed returned an unexpected number of vectors.")

        if any(len(vector) != EMBEDDING_DIMENSIONS for vector in embeddings):
            raise EmbeddingProviderError(f"FastEmbed must return {EMBEDDING_DIMENSIONS}-dimensional vectors.")
        if any(not isfinite(value) for vector in embeddings for value in vector):
            raise EmbeddingProviderError("FastEmbed returned a non-finite value.")
        return embeddings