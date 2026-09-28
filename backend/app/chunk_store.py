from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from supabase import Client, create_client

from .config import Settings
from .schemas import ChunkMetadata, SourceType


class ChunkStore:
    def list_chunks(self, project_id: str, locality: str | None = None) -> List[tuple[str, ChunkMetadata]]:
        raise NotImplementedError

    def add_chunks(self, chunks: List[tuple[str, ChunkMetadata]]) -> int:
        raise NotImplementedError


class InMemoryChunkStore(ChunkStore):
    def __init__(self, chunks: Iterable[tuple[str, ChunkMetadata]]) -> None:
        self._chunks = list(chunks)

    def list_chunks(self, project_id: str, locality: str | None = None) -> List[tuple[str, ChunkMetadata]]:
        result: list[tuple[str, ChunkMetadata]] = []
        for text, metadata in self._chunks:
            if metadata.project_id != project_id:
                continue
            if (
                locality
                and metadata.source_type == SourceType.LOCAL_REGULATION
                and metadata.locality
                and metadata.locality.lower() != locality.lower()
            ):
                continue
            result.append((text, metadata))
        return result

    def add_chunks(self, chunks: List[tuple[str, ChunkMetadata]]) -> int:
        self._chunks.extend(chunks)
        return len(chunks)


class SupabaseChunkStore(ChunkStore):
    def __init__(self, settings: Settings) -> None:
        self._table = settings.chunks_table
        self._client: Client = create_client(
            settings.supabase_url or "",
            settings.supabase_publishable_key or "",
        )

    def list_chunks(self, project_id: str, locality: str | None = None) -> List[tuple[str, ChunkMetadata]]:
        try:
            response = (
                self._client.table(self._table)
                .select("text,source_type,source_id,project_id,doc_version,locality,ingested_at")
                .eq("project_id", project_id)
                .execute()
            )
            rows = response.data or []
        except Exception:
            # Early Sprint 1 fallback when table/RLS is not fully configured yet.
            return []

        result: list[tuple[str, ChunkMetadata]] = []
        for row in rows:
            source_type = SourceType(row["source_type"])
            row_locality = row.get("locality")
            if source_type == SourceType.LOCAL_REGULATION and locality and row_locality:
                if row_locality.lower() != locality.lower():
                    continue

            ingested_at_raw = row.get("ingested_at")
            if isinstance(ingested_at_raw, str):
                ingested_at = datetime.fromisoformat(ingested_at_raw.replace("Z", "+00:00"))
            else:
                ingested_at = datetime.now()

            metadata = ChunkMetadata(
                source_type=source_type,
                source_id=row["source_id"],
                project_id=row["project_id"],
                doc_version=row["doc_version"],
                locality=row_locality,
                ingested_at=ingested_at,
            )
            result.append((row["text"], metadata))
        return result

    def add_chunks(self, chunks: List[tuple[str, ChunkMetadata]]) -> int:
        payload = []
        for text, metadata in chunks:
            payload.append(
                {
                    "text": text,
                    "source_type": metadata.source_type.value,
                    "source_id": metadata.source_id,
                    "project_id": metadata.project_id,
                    "doc_version": metadata.doc_version,
                    "locality": metadata.locality,
                    "ingested_at": metadata.ingested_at.isoformat(),
                }
            )

        self._client.table(self._table).insert(payload).execute()
        return len(payload)



def build_chunk_store(settings: Settings, demo_chunks: Iterable[tuple[str, ChunkMetadata]]) -> ChunkStore:
    if settings.supabase_url and settings.supabase_publishable_key:
        try:
            return SupabaseChunkStore(settings)
        except Exception:
            # Keep local development unblocked if Supabase credentials are not API-compatible.
            return InMemoryChunkStore(demo_chunks)
    return InMemoryChunkStore(demo_chunks)
