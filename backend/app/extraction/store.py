from __future__ import annotations

from uuid import UUID

from supabase import Client

from ..schemas import ChunkMetadata, SourceType


def project_course_chunks(client: Client, project_id: str) -> list[tuple[str, ChunkMetadata]]:
    try:
        project_uuid = str(UUID(project_id))
    except ValueError:
        return []

    result: list[tuple[str, ChunkMetadata]] = []
    offset = 0
    batch_size = 500
    while True:
        response = (
            client.rpc("project_course_chunks", {"target_project_id": project_uuid})
            .order("course_id").order("source_order").order("chunk_index")
            .range(offset, offset + batch_size - 1)
            .execute()
        )
        rows = response.data or []
        result.extend(
            (row["text"], ChunkMetadata(
                source_type=SourceType.COURSE,
                source_id=row["course_id"],
                project_id=project_id,
                doc_version=f"{row['document_format']}-v1",
                page_number=row["page_number"],
                chunk_index=row["chunk_index"],
                locator_type=row["locator_type"],
                locator=row["locator"],
                source_order=row["source_order"],
                ingested_at=row["ingested_at"],
            ))
            for row in rows
        )
        if len(rows) < batch_size:
            return result
        offset += batch_size