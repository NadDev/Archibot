from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.auth import AuthenticatedUser, get_current_user
from app.chunk_store import InMemoryChunkStore
from app.main import _memory_chunk_stores, app
from app.schemas import ChunkMetadata, SourceType

client = TestClient(app)


@pytest.fixture(autouse=True)
def authenticate_test_client():
    demo_chunks = [
        (
            "Le plan masse organise les volumes et les retraits selon le contexte du site.",
            ChunkMetadata(
                source_type=SourceType.COURSE,
                source_id="course-archi-01",
                project_id="demo-project",
                doc_version="v1",
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
    _memory_chunk_stores["test-user"] = InMemoryChunkStore(
        demo_chunks,
        default_owner_id="test-user",
    )
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id="test-user",
        access_token="test-token",
    )
    yield
    app.dependency_overrides.clear()
    _memory_chunk_stores.pop("test-user", None)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_allows_configured_frontend_preflight() -> None:
    response = client.options(
        "/v1/retrieval/search",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "authorization" in response.headers["access-control-allow-headers"].lower()


def test_retrieval_requires_authentication() -> None:
    app.dependency_overrides.clear()

    response = client.post(
        "/v1/retrieval/search",
        json={"question": "plan masse", "project_id": "demo-project"},
    )

    assert response.status_code == 401


def test_private_course_chunks_are_not_visible_to_another_user() -> None:
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id="another-user",
        access_token="another-token",
    )

    response = client.post(
        "/v1/retrieval/search",
        json={"question": "plan masse", "project_id": "demo-project"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_user_cannot_ingest_into_shared_architecture_corpus() -> None:
    response = client.post(
        "/v1/ingestion/chunks",
        json={
            "chunks": [
                {
                    "text": "Connaissance générale de l'architecture",
                    "metadata": {
                        "source_type": "general",
                        "source_id": "architecture-general",
                        "project_id": "architecture-global",
                        "doc_version": "v1",
                        "ingested_at": "2026-10-21T00:00:00Z",
                        "visibility": "shared",
                    },
                }
            ]
        },
    )

    assert response.status_code == 403


def test_retrieval_endpoint_returns_items() -> None:
    payload = {
        "question": "plan masse hauteur",
        "project_id": "demo-project",
        "top_k": 3,
        "locality": "lyon",
    }
    response = client.post("/v1/retrieval/search", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert len(body["items"]) >= 1


def test_assistant_answer_structure() -> None:
    payload = {
        "question": "hauteur zone UAb",
        "project_id": "demo-project",
        "top_k": 5,
        "locality": "lyon",
    }
    response = client.post("/v1/assistant/answer", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["schema_version"] == "v1"
    assert "cours" in body
    assert "regle_generale" in body
    assert "source_reglementaire_locale" in body


def test_assistant_answer_warns_when_no_local_source() -> None:
    payload = {
        "question": "hauteur zone UAb",
        "project_id": "demo-project",
        "top_k": 5,
        "locality": "marseille",
    }
    response = client.post("/v1/assistant/answer", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["source_reglementaire_locale"]["text"]
    assert body["warning_no_source"] is not None


def test_assistant_answer_multi_source_sections_present() -> None:
    payload = {
        "question": "plan masse relation site hauteurs",
        "project_id": "demo-project",
        "top_k": 5,
        "locality": "lyon",
    }
    response = client.post("/v1/assistant/answer", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["cours"]["text"]
    assert body["regle_generale"]["text"]
    assert body["source_reglementaire_locale"]["text"]


def test_ingestion_then_retrieval_flow() -> None:
    ingest_payload = {
        "chunks": [
            {
                "text": "Le PLU de Marseille impose des contraintes de hauteur en secteur dense.",
                "metadata": {
                    "source_type": "local_regulation",
                    "source_id": "plu-marseille-hauteur",
                    "project_id": "demo-project",
                    "doc_version": "v1",
                    "locality": "marseille",
                    "ingested_at": "2026-09-28T00:00:00Z",
                },
            }
        ]
    }

    ingest_response = client.post("/v1/ingestion/chunks", json=ingest_payload)
    assert ingest_response.status_code == 200
    assert ingest_response.json()["inserted"] == 1

    retrieval_payload = {
        "question": "hauteur secteur dense",
        "project_id": "demo-project",
        "top_k": 5,
        "locality": "marseille",
    }
    retrieval_response = client.post("/v1/retrieval/search", json=retrieval_payload)
    assert retrieval_response.status_code == 200
    body = retrieval_response.json()
    assert body["total"] >= 1
    assert any(item["metadata"]["locality"] == "marseille" for item in body["items"])
