from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException

from .chunk_store import build_chunk_store
from .config import get_settings
from .retrieval import retrieve_chunks
from .schemas import (
    AskRequest,
    IngestRequest,
    IngestResponse,
    AssistantResponse,
    ChunkMetadata,
    Citation,
    ResponseSection,
    RetrievedChunk,
    RetrievalQuery,
    RetrievalResponse,
    SourceType,
)

app = FastAPI(title="Archibot API", version="0.1.0")
settings = get_settings()


DEMO_CHUNKS: list[tuple[str, ChunkMetadata]] = [
    (
        "Le plan masse organise les volumes et les retraits selon le contexte du site.",
        ChunkMetadata(
            source_type=SourceType.COURSE,
            source_id="course-archi-01",
            project_id="demo-project",
            doc_version="v1",
            locality=None,
            ingested_at=datetime(2026, 9, 28, tzinfo=UTC),
        ),
    ),
    (
        "En regle generale, la relation site-programme-usages doit rester coherente.",
        ChunkMetadata(
            source_type=SourceType.GENERAL,
            source_id="general-knowledge-01",
            project_id="demo-project",
            doc_version="v1",
            locality=None,
            ingested_at=datetime(2026, 9, 28, tzinfo=UTC),
        ),
    ),
    (
        "Le PLU de Lyon impose des hauteurs maximales selon la zone UAb.",
        ChunkMetadata(
            source_type=SourceType.LOCAL_REGULATION,
            source_id="plu-lyon-uab",
            project_id="demo-project",
            doc_version="v1",
            locality="lyon",
            ingested_at=datetime(2026, 9, 28, tzinfo=UTC),
        ),
    ),
    (
        "Le PLU de Nantes fixe des regles d'implantation en limite separative.",
        ChunkMetadata(
            source_type=SourceType.LOCAL_REGULATION,
            source_id="plu-nantes-limite",
            project_id="demo-project",
            doc_version="v1",
            locality="nantes",
            ingested_at=datetime(2026, 9, 28, tzinfo=UTC),
        ),
    ),
]

chunk_store = build_chunk_store(settings=settings, demo_chunks=DEMO_CHUNKS)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/demo-response", response_model=AssistantResponse)
def demo_response() -> AssistantResponse:
    now = datetime.now(UTC).isoformat()
    return AssistantResponse(
        schema_version="v1",
        cours=ResponseSection(
            text="Definition extraite des cours de l'etudiant.",
            citations=[
                Citation(
                    source_id="course-archi-01",
                    excerpt="Le plan masse organise les volumes sur la parcelle.",
                    score=0.91,
                )
            ],
        ),
        regle_generale=ResponseSection(
            text="En regle generale, la coherence site-programme-pratique guide les choix.",
            citations=[],
        ),
        source_reglementaire_locale=ResponseSection(
            text="Aucune source reglementaire locale disponible.",
            citations=[],
        ),
        warning_no_source=f"Aucune source locale disponible a {now}",
    )


@app.post("/v1/retrieval/search", response_model=RetrievalResponse)
def retrieval_search(query: RetrievalQuery) -> RetrievalResponse:
    chunks = chunk_store.list_chunks(project_id=query.project_id, locality=query.locality)
    items = retrieve_chunks(query=query, chunks=chunks)
    return RetrievalResponse(total=len(items), items=items)


@app.post("/v1/ingestion/chunks", response_model=IngestResponse)
def ingestion_chunks(payload: IngestRequest) -> IngestResponse:
    chunks = [(chunk.text, chunk.metadata) for chunk in payload.chunks]
    try:
        inserted = chunk_store.add_chunks(chunks)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Echec d'insertion des chunks (table/policy Supabase a verifier).",
        ) from exc
    return IngestResponse(inserted=inserted)


def _first_by_source(items: list[RetrievedChunk], source_type: SourceType) -> RetrievedChunk | None:
    for item in items:
        if item.metadata.source_type == source_type:
            return item
    return None


@app.post("/v1/assistant/answer", response_model=AssistantResponse)
def assistant_answer(request: AskRequest) -> AssistantResponse:
    chunks = chunk_store.list_chunks(project_id=request.project_id, locality=request.locality)
    items = retrieve_chunks(
        query=RetrievalQuery(
            question=request.question,
            project_id=request.project_id,
            top_k=request.top_k,
            locality=request.locality,
        ),
        chunks=chunks,
    )

    cours_item = _first_by_source(items, SourceType.COURSE)
    general_item = _first_by_source(items, SourceType.GENERAL)
    local_item = _first_by_source(items, SourceType.LOCAL_REGULATION)

    cours_section = ResponseSection(
        text=(cours_item.text if cours_item else "Aucun passage de cours pertinent trouve."),
        citations=(
            [Citation(source_id=cours_item.metadata.source_id, excerpt=cours_item.text, score=cours_item.score)]
            if cours_item
            else []
        ),
    )

    general_section = ResponseSection(
        text=(
            general_item.text
            if general_item
            else "Aucune regle generale pertinente trouvee."
        ),
        citations=(
            [
                Citation(
                    source_id=general_item.metadata.source_id,
                    excerpt=general_item.text,
                    score=general_item.score,
                )
            ]
            if general_item
            else []
        ),
    )

    if local_item:
        local_section = ResponseSection(
            text=local_item.text,
            citations=[
                Citation(
                    source_id=local_item.metadata.source_id,
                    excerpt=local_item.text,
                    score=local_item.score,
                )
            ],
        )
        warning = None
    else:
        local_section = ResponseSection(
            text="Aucune source reglementaire locale disponible pour cette requete.",
            citations=[],
        )
        warning = "Aucune source reglementaire locale disponible pour cette requete."

    return AssistantResponse(
        schema_version="v1",
        cours=cours_section,
        regle_generale=general_section,
        source_reglementaire_locale=local_section,
        warning_no_source=warning,
    )
