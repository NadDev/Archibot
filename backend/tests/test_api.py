from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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
