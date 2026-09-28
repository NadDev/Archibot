from __future__ import annotations

import re
from typing import Iterable, List

from .schemas import ChunkMetadata, RetrievedChunk, RetrievalQuery, SourceType


WORD_RE = re.compile(r"[a-zA-Z0-9_]+")


def _tokenize(text: str) -> set[str]:
    return {match.group(0).lower() for match in WORD_RE.finditer(text)}


def _score(question: str, chunk_text: str) -> float:
    q = _tokenize(question)
    c = _tokenize(chunk_text)
    if not q:
        return 0.0
    overlap = len(q.intersection(c))
    query_coverage = overlap / len(q)
    chunk_coverage = overlap / max(1, len(c))
    return min(1.0, (0.7 * query_coverage) + (0.3 * chunk_coverage))


def _source_priority(source_type: SourceType, locality: str | None) -> int:
    if locality:
        order = {
            SourceType.LOCAL_REGULATION: 3,
            SourceType.COURSE: 2,
            SourceType.GENERAL: 1,
        }
        return order[source_type]
    order = {
        SourceType.COURSE: 3,
        SourceType.GENERAL: 2,
        SourceType.LOCAL_REGULATION: 1,
    }
    return order[source_type]


def _locality_match(metadata: ChunkMetadata, locality: str | None) -> bool:
    if metadata.source_type != SourceType.LOCAL_REGULATION:
        return True
    if locality is None:
        return True
    if metadata.locality is None:
        return False
    return metadata.locality.strip().lower() == locality.strip().lower()


def retrieve_chunks(
    query: RetrievalQuery,
    chunks: Iterable[tuple[str, ChunkMetadata]],
) -> List[RetrievedChunk]:
    scored: list[RetrievedChunk] = []
    for chunk_text, metadata in chunks:
        if metadata.project_id != query.project_id:
            continue
        if not _locality_match(metadata, query.locality):
            continue
        score = _score(query.question, chunk_text)
        if score < query.min_score:
            continue
        scored.append(
            RetrievedChunk(
                text=chunk_text,
                metadata=metadata,
                score=score,
            )
        )

    scored.sort(
        key=lambda item: (
            item.score,
            _source_priority(item.metadata.source_type, query.locality),
        ),
        reverse=True,
    )
    return scored[: query.top_k]
