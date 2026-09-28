from datetime import UTC, datetime

from app.retrieval import retrieve_chunks
from app.schemas import ChunkMetadata, RetrievalQuery, SourceType


def _chunk(text: str, source_type: SourceType, locality: str | None) -> tuple[str, ChunkMetadata]:
    return (
        text,
        ChunkMetadata(
            source_type=source_type,
            source_id=f"{source_type.value}-1",
            project_id="p1",
            doc_version="v1",
            locality=locality,
            ingested_at=datetime(2026, 9, 28, tzinfo=UTC),
        ),
    )


def test_retrieval_filters_locality_for_local_regulation() -> None:
    chunks = [
        _chunk("PLU Lyon hauteur", SourceType.LOCAL_REGULATION, "lyon"),
        _chunk("PLU Nantes hauteur", SourceType.LOCAL_REGULATION, "nantes"),
        _chunk("Cours plan masse", SourceType.COURSE, None),
    ]

    result = retrieve_chunks(
        RetrievalQuery(
            question="hauteur plan",
            project_id="p1",
            top_k=5,
            locality="lyon",
        ),
        chunks,
    )

    localities = {item.metadata.locality for item in result if item.metadata.source_type == SourceType.LOCAL_REGULATION}
    assert localities == {"lyon"}


def test_retrieval_respects_top_k() -> None:
    chunks = [
        _chunk("cours site", SourceType.COURSE, None),
        _chunk("regle generale site", SourceType.GENERAL, None),
        _chunk("plu site", SourceType.LOCAL_REGULATION, "lyon"),
    ]

    result = retrieve_chunks(
        RetrievalQuery(question="site", project_id="p1", top_k=2, locality="lyon"),
        chunks,
    )

    assert len(result) == 2


def test_retrieval_applies_min_score_and_orders_results() -> None:
    chunks = [
        _chunk("hauteur zone UAb et gabarit", SourceType.LOCAL_REGULATION, "lyon"),
        _chunk("hauteur", SourceType.GENERAL, None),
        _chunk("atelier maquette", SourceType.COURSE, None),
    ]

    result = retrieve_chunks(
        RetrievalQuery(
            question="hauteur zone UAb",
            project_id="p1",
            top_k=5,
            locality="lyon",
            min_score=0.2,
        ),
        chunks,
    )

    assert len(result) >= 1
    assert result[0].metadata.source_type == SourceType.LOCAL_REGULATION
    assert all(item.score >= 0.2 for item in result)
