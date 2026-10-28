from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Literal, cast

from supabase import Client, create_client

from .config import Settings
from .extraction.store import project_course_chunks
from .schemas import ChunkMetadata, ChunkVisibility, SourceType


LocatorType = Literal["page", "slide", "section", "chapter"]


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) else None


def _optional_locator_type(value: object) -> LocatorType | None:
    if value in {"page", "slide", "section", "chapter"}:
        return cast(LocatorType, value)
    return None


class ChunkStore:
    def list_chunks(
        self,
        project_id: str,
        owner_id: str,
        locality: str | None = None,
    ) -> List[tuple[str, ChunkMetadata]]:
        raise NotImplementedError

    def add_chunks(self, chunks: List[tuple[str, ChunkMetadata]], owner_id: str) -> int:
        raise NotImplementedError


class InMemoryChunkStore(ChunkStore):
    def __init__(
        self,
        chunks: Iterable[tuple[str, ChunkMetadata]],
        default_owner_id: str = "demo-user",
    ) -> None:
        self._chunks = [
            (text, metadata, None if metadata.visibility == ChunkVisibility.SHARED else default_owner_id)
            for text, metadata in chunks
        ]

    def list_chunks(
        self,
        project_id: str,
        owner_id: str,
        locality: str | None = None,
    ) -> List[tuple[str, ChunkMetadata]]:
        result: list[tuple[str, ChunkMetadata]] = []
        for text, metadata, chunk_owner_id in self._chunks:
            if metadata.visibility == ChunkVisibility.SHARED:
                pass
            elif chunk_owner_id != owner_id or metadata.project_id != project_id:
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

    def add_chunks(self, chunks: List[tuple[str, ChunkMetadata]], owner_id: str) -> int:
        if any(metadata.visibility != ChunkVisibility.PRIVATE for _, metadata in chunks):
            raise ValueError("Only private chunks can be ingested through the user API.")
        self._chunks.extend((text, metadata, owner_id) for text, metadata in chunks)
        return len(chunks)


class SupabaseChunkStore(ChunkStore):
    def __init__(self, settings: Settings, access_token: str) -> None:
        self._table = settings.chunks_table
        self._client: Client = create_client(
            settings.supabase_url or "",
            settings.supabase_publishable_key or "",
        )
        self._client.postgrest.auth(access_token)

    def list_chunks(
        self,
        project_id: str,
        owner_id: str,
        locality: str | None = None,
    ) -> List[tuple[str, ChunkMetadata]]:
        private_response = (
            self._client.table(self._table)
            .select("text,source_type,source_id,project_id,doc_version,locality,page_number,chunk_index,locator_type,locator,source_order,ingested_at")
            .eq("project_id", project_id)
            .eq("owner_id", owner_id)
            .execute()
        )
        shared_response = (
            self._client.table("architecture_knowledge_chunks")
            .select("text,source_id,doc_version,locality,page_number,chunk_index,locator_type,locator,source_order,ingested_at")
            .execute()
        )

        result = [
            (row["text"], self._metadata(row, ChunkVisibility.PRIVATE))
            for row in (private_response.data or [])
        ]
        result.extend(
            (row["text"], self._metadata(row, ChunkVisibility.SHARED))
            for row in (shared_response.data or [])
        )
        result.extend(project_course_chunks(self._client, project_id))
        return [
            (text, metadata)
            for text, metadata in result
            if not (
                locality
                and metadata.source_type == SourceType.LOCAL_REGULATION
                and metadata.locality
                and metadata.locality.lower() != locality.lower()
            )
        ]

    @staticmethod
    def _metadata(row: dict[str, object], visibility: ChunkVisibility) -> ChunkMetadata:
        if visibility == ChunkVisibility.SHARED:
            source_type = SourceType.GENERAL
            project_id = "architecture-global"
        else:
            source_type = SourceType(str(row["source_type"]))
            project_id = str(row["project_id"])

        ingested_at_raw = row.get("ingested_at")
        if isinstance(ingested_at_raw, str):
            ingested_at = datetime.fromisoformat(ingested_at_raw.replace("Z", "+00:00"))
        else:
            ingested_at = datetime.now()

        return ChunkMetadata(
            source_type=source_type,
            source_id=str(row["source_id"]),
            project_id=project_id,
            doc_version=str(row["doc_version"]),
            locality=str(row["locality"]) if row.get("locality") is not None else None,
            page_number=_optional_int(row.get("page_number")),
            chunk_index=_optional_int(row.get("chunk_index")),
            locator_type=_optional_locator_type(row.get("locator_type")),
            locator=str(row["locator"]) if row.get("locator") is not None else None,
            source_order=_optional_int(row.get("source_order")),
            ingested_at=ingested_at,
            visibility=visibility,
        )

    def add_chunks(self, chunks: List[tuple[str, ChunkMetadata]], owner_id: str) -> int:
        if any(metadata.visibility != ChunkVisibility.PRIVATE for _, metadata in chunks):
            raise ValueError("Only private chunks can be ingested through the user API.")
        payload = []
        for text, metadata in chunks:
            payload.append(
                {
                    "text": text,
                    "source_type": metadata.source_type.value,
                    "source_id": metadata.source_id,
                    "owner_id": owner_id,
                    "project_id": metadata.project_id,
                    "doc_version": metadata.doc_version,
                    "locality": metadata.locality,
                    "page_number": metadata.page_number,
                    "chunk_index": metadata.chunk_index,
                    "locator_type": metadata.locator_type,
                    "locator": metadata.locator,
                    "source_order": metadata.source_order,
                    "ingested_at": metadata.ingested_at.isoformat(),
                }
            )

        self._client.table(self._table).insert(payload).execute()
        return len(payload)
