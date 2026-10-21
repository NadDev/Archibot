from __future__ import annotations

from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException

from .auth import AuthenticatedUser, get_current_user
from .chunk_store import InMemoryChunkStore, SupabaseChunkStore
from .config import get_settings
from .retrieval import retrieve_chunks
from .schemas import (
    AskRequest,
    IngestRequest,
    IngestResponse,
    AssistantResponse,
    Citation,
    ResponseSection,
    RetrievedChunk,
    RetrievalQuery,
    RetrievalResponse,
    SourceType,
)

app = FastAPI(title="Archibot API", version="0.1.0")
settings = get_settings()


_memory_chunk_stores: dict[str, InMemoryChunkStore] = {}


def _chunk_store_for(user: AuthenticatedUser) -> InMemoryChunkStore | SupabaseChunkStore:
    if settings.supabase_url and settings.supabase_publishable_key:
        return SupabaseChunkStore(settings, access_token=user.access_token)
    if user.id not in _memory_chunk_stores:
        _memory_chunk_stores[user.id] = InMemoryChunkStore([])
    return _memory_chunk_stores[user.id]


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
def retrieval_search(
    query: RetrievalQuery,
    user: AuthenticatedUser = Depends(get_current_user),
) -> RetrievalResponse:
    chunks = _chunk_store_for(user).list_chunks(
        project_id=query.project_id,
        owner_id=user.id,
        locality=query.locality,
    )
    items = retrieve_chunks(query=query, chunks=chunks)
    return RetrievalResponse(total=len(items), items=items)


@app.post("/v1/ingestion/chunks", response_model=IngestResponse)
def ingestion_chunks(
    payload: IngestRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> IngestResponse:
    chunks = [(chunk.text, chunk.metadata) for chunk in payload.chunks]
    if any(chunk.metadata.visibility.value != "private" for chunk in payload.chunks):
        raise HTTPException(status_code=403, detail="User ingestion is limited to private chunks.")
    try:
        inserted = _chunk_store_for(user).add_chunks(chunks, owner_id=user.id)
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
def assistant_answer(
    request: AskRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> AssistantResponse:
    chunks = _chunk_store_for(user).list_chunks(
        project_id=request.project_id,
        owner_id=user.id,
        locality=request.locality,
    )
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
