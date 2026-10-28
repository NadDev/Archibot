from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from app import chunk_store as chunk_store_module
from app.chunk_store import InMemoryChunkStore, SupabaseChunkStore
from app.config import Settings
from app.schemas import ChunkMetadata, ChunkVisibility, SourceType


def make_metadata(
    project_id: str,
    visibility: ChunkVisibility = ChunkVisibility.PRIVATE,
    page_number: int | None = None,
    chunk_index: int | None = None,
) -> ChunkMetadata:
    return ChunkMetadata(
        source_type=SourceType.COURSE,
        source_id="course-source",
        project_id=project_id,
        doc_version="v1",
        ingested_at=datetime(2026, 10, 21, tzinfo=UTC),
        visibility=visibility,
        page_number=page_number,
        chunk_index=chunk_index,
    )


def test_memory_store_isolates_private_chunks_by_owner_and_project() -> None:
    store = InMemoryChunkStore([])
    store.add_chunks([("contenu de cours privé", make_metadata("project-a"))], "user-a")

    assert len(store.list_chunks("project-a", "user-a")) == 1
    assert store.list_chunks("project-a", "user-b") == []
    assert store.list_chunks("project-b", "user-a") == []


def test_memory_store_shares_only_explicit_shared_chunks() -> None:
    store = InMemoryChunkStore(
        [("connaissance générale", make_metadata("architecture-global", ChunkVisibility.SHARED))]
    )

    assert len(store.list_chunks("project-a", "user-a")) == 1
    assert len(store.list_chunks("project-b", "user-b")) == 1


def test_memory_store_rejects_user_ingestion_into_shared_corpus() -> None:
    store = InMemoryChunkStore([])

    with pytest.raises(ValueError, match="Only private chunks"):
        store.add_chunks(
            [("connaissance générale", make_metadata("architecture-global", ChunkVisibility.SHARED))],
            "user-a",
        )


class FakeQuery:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows
        self.filters: list[tuple[str, str]] = []
        self.inserted: list[dict[str, object]] | None = None
        self.bounds: tuple[int, int] | None = None

    def select(self, columns: str) -> FakeQuery:
        return self

    def eq(self, column: str, value: str) -> FakeQuery:
        self.filters.append((column, value))
        return self

    def insert(self, rows: list[dict[str, object]]) -> FakeQuery:
        self.inserted = rows
        return self

    def execute(self) -> SimpleNamespace:
        rows = self.rows if self.bounds is None else self.rows[self.bounds[0]:self.bounds[1] + 1]
        return SimpleNamespace(data=rows)

    def order(self, column: str) -> FakeQuery:
        return self

    def range(self, start: int, end: int) -> FakeQuery:
        self.bounds = (start, end)
        return self


class FakePostgrest:
    def __init__(self) -> None:
        self.token: str | None = None

    def auth(self, token: str) -> None:
        self.token = token


class FakeSupabaseClient:
    def __init__(self) -> None:
        self.postgrest = FakePostgrest()
        self.queries = {
            "chunks": FakeQuery([]),
            "architecture_knowledge_chunks": FakeQuery([]),
            "project_course_chunks": FakeQuery([]),
        }
        self.rpc_calls = []

    def table(self, name: str) -> FakeQuery:
        return self.queries[name]

    def rpc(self, name, params):
        self.rpc_calls.append((name, params))
        return self.queries[name]


def test_supabase_store_uses_user_jwt_and_owner_scoped_queries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeSupabaseClient()
    monkeypatch.setattr(chunk_store_module, "create_client", lambda url, key: fake_client)
    settings = Settings(
        supabase_url="https://example.supabase.co",
        supabase_publishable_key="test-publishable-key",
        chunks_table="chunks",
        embedding_model="test-model",
    )
    store = SupabaseChunkStore(settings, access_token="user-jwt")

    store.list_chunks(project_id="project-a", owner_id="user-a")

    assert fake_client.postgrest.token == "user-jwt"
    assert fake_client.queries["chunks"].filters == [
        ("project_id", "project-a"),
        ("owner_id", "user-a"),
    ]


def test_supabase_store_persists_page_provenance(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = FakeSupabaseClient()
    monkeypatch.setattr(chunk_store_module, "create_client", lambda url, key: fake_client)
    settings = Settings(
        supabase_url="https://example.supabase.co",
        supabase_publishable_key="test-publishable-key",
        chunks_table="chunks",
        embedding_model="test-model",
    )
    store = SupabaseChunkStore(settings, access_token="user-jwt")

    store.add_chunks(
        [("page excerpt", make_metadata("project-a", page_number=3, chunk_index=2))],
        owner_id="user-a",
    )

    inserted = fake_client.queries["chunks"].inserted
    assert inserted is not None
    assert inserted[0]["page_number"] == 3
    assert inserted[0]["chunk_index"] == 2


def test_supabase_store_reads_page_provenance(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = FakeSupabaseClient()
    fake_client.queries["chunks"].rows = [
        {
            "text": "page excerpt",
            "source_type": "course",
            "source_id": "course-source",
            "project_id": "project-a",
            "doc_version": "v1",
            "locality": None,
            "page_number": 3,
            "chunk_index": 2,
            "ingested_at": "2026-10-21T00:00:00+00:00",
        }
    ]
    monkeypatch.setattr(chunk_store_module, "create_client", lambda url, key: fake_client)
    settings = Settings(
        supabase_url="https://example.supabase.co",
        supabase_publishable_key="test-publishable-key",
        chunks_table="chunks",
        embedding_model="test-model",
    )
    store = SupabaseChunkStore(settings, access_token="user-jwt")

    chunks = store.list_chunks(project_id="project-a", owner_id="user-a")

    assert chunks[0][1].page_number == 3
    assert chunks[0][1].chunk_index == 2


def test_supabase_store_reads_all_linked_course_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = FakeSupabaseClient()
    project_id = "00000000-0000-0000-0000-000000000001"
    fake_client.queries["project_course_chunks"].rows = [
        {
            "text": f"page {page}",
            "course_id": "course-source",
            "page_number": page,
            "chunk_index": 1,
            "locator_type": "page",
            "locator": f"Page {page}",
            "source_order": page,
                "document_format": "pdf",
            "ingested_at": "2026-10-28T00:00:00+00:00",
        }
        for page in range(1, 502)
    ]
    monkeypatch.setattr(chunk_store_module, "create_client", lambda url, key: fake_client)
    settings = Settings("https://example.supabase.co", "test-key", "chunks", "test-model")

    chunks = SupabaseChunkStore(settings, "user-jwt").list_chunks(project_id, "user-a")

    assert len(chunks) == 501
    assert chunks[-1][1].page_number == 501
    assert chunks[-1][1].source_id == "course-source"
    assert chunks[-1][1].project_id == project_id
    assert chunks[-1][1].visibility == ChunkVisibility.PRIVATE
    assert chunks[-1][1].locator_type == "page"
    assert chunks[-1][1].locator == "Page 501"
    assert chunks[-1][1].source_order == 501
    assert fake_client.rpc_calls == [("project_course_chunks", {"target_project_id": project_id})] * 2


def test_supabase_store_reads_structural_course_locations(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = FakeSupabaseClient()
    project_id = "00000000-0000-0000-0000-000000000001"
    fake_client.queries["project_course_chunks"].rows = [{
        "text": "ventilation de la diapositive",
        "course_id": "course-source",
        "page_number": None,
        "chunk_index": 1,
        "locator_type": "slide",
        "locator": "Diapositive 2",
        "source_order": 2,
        "document_format": "pptx",
        "ingested_at": "2026-10-28T00:00:00+00:00",
    }]
    monkeypatch.setattr(chunk_store_module, "create_client", lambda url, key: fake_client)
    settings = Settings("https://example.supabase.co", "test-key", "chunks", "test-model")

    chunks = SupabaseChunkStore(settings, "user-jwt").list_chunks(project_id, "user-a")

    assert len(chunks) == 1
    metadata = chunks[0][1]
    assert metadata.page_number is None
    assert metadata.locator_type == "slide"
    assert metadata.locator == "Diapositive 2"
    assert metadata.source_order == 2
    assert metadata.doc_version == "pptx-v1"

    fake_client.queries["project_course_chunks"].rows[0].update({
        "locator_type": "image",
        "locator": "Image",
        "source_order": 1,
        "document_format": "png",
    })
    image_chunks = SupabaseChunkStore(settings, "user-jwt").list_chunks(project_id, "user-a")

    assert image_chunks[0][1].locator_type == "image"
    assert image_chunks[0][1].doc_version == "png-v1"