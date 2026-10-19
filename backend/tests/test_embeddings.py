from __future__ import annotations

import pytest

from app.embeddings import (
    EMBEDDING_DIMENSIONS,
    EmbeddingProviderError,
    FastEmbedEmbeddingProvider,
)


class FakeFastEmbedModel:
    def __init__(self, vectors: list[list[float]]) -> None:
        self.vectors = vectors
        self.inputs: list[str] | None = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.inputs = texts
        return self.vectors


def test_fastembed_provider_batches_inputs_and_preserves_order() -> None:
    first_vector = [0.1] * EMBEDDING_DIMENSIONS
    second_vector = [0.2] * EMBEDDING_DIMENSIONS
    encoder = FakeFastEmbedModel([first_vector, second_vector])
    provider = FastEmbedEmbeddingProvider(encoder=encoder)

    embeddings = provider.embed(["  premier texte ", "second texte"])

    assert embeddings == [first_vector, second_vector]
    assert encoder.inputs == ["premier texte", "second texte"]
    assert type(embeddings[0][0]) is float


@pytest.mark.parametrize("texts", [[], ["  "]])
def test_embedding_provider_rejects_empty_input(texts: list[str]) -> None:
    provider = FastEmbedEmbeddingProvider(encoder=FakeFastEmbedModel([]))

    with pytest.raises(ValueError, match="non-empty"):
        provider.embed(texts)


def test_embedding_provider_rejects_wrong_dimensions() -> None:
    provider = FastEmbedEmbeddingProvider(encoder=FakeFastEmbedModel([[0.1, 0.2]]))

    with pytest.raises(EmbeddingProviderError, match="384-dimensional"):
        provider.embed(["some text"])


def test_embedding_provider_rejects_non_finite_values() -> None:
    vector = [0.1] * EMBEDDING_DIMENSIONS
    vector[4] = float("nan")
    provider = FastEmbedEmbeddingProvider(encoder=FakeFastEmbedModel([vector]))

    with pytest.raises(EmbeddingProviderError, match="non-finite"):
        provider.embed(["some text"])