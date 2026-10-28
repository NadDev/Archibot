from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import Client, ClientOptions, create_client

from ..auth import AuthenticatedUser, get_current_user
from ..config import get_settings
from ..extraction import (
    DocumentProcessingError,
    extract_docx_chunks,
    extract_epub_chunks,
    extract_pdf_chunks,
    extract_pptx_chunks,
)


MAX_DOCUMENT_BYTES = 50 * 1024 * 1024
router = APIRouter(prefix="/v1/courses", tags=["courses"])
EXTRACTORS = {
    "application/pdf": ("pdf", extract_pdf_chunks),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ("docx", extract_docx_chunks),
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ("pptx", extract_pptx_chunks),
    "application/epub+zip": ("epub", extract_epub_chunks),
}


class ExtractionResult(BaseModel):
    course_id: UUID
    status: str
    chunk_count: int
    error: str | None = None


class CourseExtractionClient(Protocol):
    @property
    def storage(self) -> Any: ...

    def table(self, table_name: str) -> Any: ...

    def rpc(self, fn: str, params: dict[str, Any] | None = None) -> Any: ...


class CourseExtractionService:
    def __init__(self, client: CourseExtractionClient, owner_id: str) -> None:
        self.client = client
        self.owner_id = owner_id

    def extract(self, course_id: UUID) -> ExtractionResult:
        response = (
            self.client.table("user_courses")
            .select("id,storage_path,content_type,file_size")
            .eq("id", str(course_id))
            .eq("owner_id", self.owner_id)
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Cours introuvable.")
        course = response.data[0]
        path = course["storage_path"]
        if not path.startswith(f"{self.owner_id}/") or ".." in path.split("/"):
            raise HTTPException(status_code=403, detail="Chemin de document non autorise.")

        status = "extracted"
        error = None
        chunks = []
        extraction_format = EXTRACTORS.get(course["content_type"])
        if extraction_format is None:
            status = "unsupported"
            error = "Extraction non disponible pour ce format."
            document_format = "unsupported"
        else:
            document_format, extractor = extraction_format
            try:
                if not 0 < course["file_size"] <= MAX_DOCUMENT_BYTES:
                    raise DocumentProcessingError("Le document doit faire entre 1 octet et 50 Mo.")
                document_bytes = self.client.storage.from_("user-courses").download(path)
                if len(document_bytes) > MAX_DOCUMENT_BYTES:
                    raise DocumentProcessingError("Le document depasse 50 Mo.")
                chunks = extractor(document_bytes)
            except DocumentProcessingError as exc:
                status = "failed"
                error = str(exc)
            except Exception as exc:
                raise HTTPException(status_code=502, detail="Lecture du fichier impossible. Reessayez.") from exc

        self.client.rpc("save_course_extraction", {
            "target_course_id": str(course_id),
            "result_status": status,
            "result_error": error,
            "result_chunks": [
                {"text": chunk.text, "page_number": chunk.page_number, "chunk_index": chunk.chunk_index}
                | {
                    "locator_type": chunk.locator_type,
                    "locator": chunk.locator,
                    "source_order": chunk.source_order,
                    "document_format": document_format,
                }
                for chunk in chunks
            ],
        }).execute()
        return ExtractionResult(course_id=course_id, status=status, chunk_count=len(chunks), error=error)


def get_course_extraction_service(
    user: AuthenticatedUser = Depends(get_current_user),
) -> CourseExtractionService:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_publishable_key:
        raise HTTPException(status_code=503, detail="Stockage documentaire non configure.")
    client = create_client(
        settings.supabase_url,
        settings.supabase_publishable_key,
        options=ClientOptions(headers={"Authorization": f"Bearer {user.access_token}"}),
    )
    return CourseExtractionService(client, owner_id=user.id)


@router.post("/{course_id}/extract", response_model=ExtractionResult)
def extract_course(
    course_id: UUID,
    service: CourseExtractionService = Depends(get_course_extraction_service),
) -> ExtractionResult:
    try:
        return service.extract(course_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Enregistrement de l'extraction impossible. Reessayez.") from exc