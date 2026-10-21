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
) -> ChunkMetadata:
    return ChunkMetadata(
        source_type=SourceType.COURSE,
        source_id="course-source",
        project_id=project_id,
        doc_version="v1",
        ingested_at=datetime(2026, 10, 21, tzinfo=UTC),
        visibility=visibility,
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

    def select(self, columns: str) -> FakeQuery:
        return self

    def eq(self, column: str, value: str) -> FakeQuery:
        self.filters.append((column, value))
        return self

    def insert(self, rows: list[dict[str, object]]) -> FakeQuery:
        self.inserted = rows
        return self

    def execute(self) -> SimpleNamespace:
        return SimpleNamespace(data=self.rows)


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
        }

    def table(self, name: str) -> FakeQuery:
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