from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

import pytest
import httpx
from fastapi import HTTPException

from app.extraction import (
    DocumentProcessingError,
    chunk_text,
    extract_pdf_chunks,
)
from app.auth import AuthenticatedUser
from app.config import Settings
from app.upload import courses as courses_module
from app.upload.courses import CourseExtractionService, get_course_extraction_service


def _pdf_with_text(*page_texts: str) -> bytes:
    page_numbers = range(3, 3 + len(page_texts))
    font_number = 3 + len(page_texts)
    first_content_number = font_number + 1
    page_references = " ".join(f"{number} 0 R" for number in page_numbers)
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{page_references}] /Count {len(page_texts)} >>".encode("ascii"),
    ]
    for index in range(len(page_texts)):
        page_number = 3 + index
        content_number = first_content_number + index
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 {font_number} 0 R >> >> /Contents {content_number} 0 R >>".encode("ascii")
        )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for text in page_texts:
        content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("ascii")
        objects.append(f"<< /Length {len(content)} >>\nstream\n".encode("ascii") + content + b"\nendstream")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for object_number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets:
        pdf.extend(f"{offset:010} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("ascii")
    )
    return bytes(pdf)


def test_extract_pdf_text_preserves_page_and_chunk_references() -> None:
    chunks = extract_pdf_chunks(
        _pdf_with_text("Architecture course reference supports spatial design choices"),
        max_chars=24,
        overlap_chars=6,
    )

    assert len(chunks) > 1
    assert all(chunk.page_number == 1 for chunk in chunks)
    assert [chunk.chunk_index for chunk in chunks] == list(range(1, len(chunks) + 1))
    assert all(chunk.text for chunk in chunks)
    assert all(len(chunk.text) <= 24 for chunk in chunks)


def test_extract_pdf_chunks_keep_their_source_page() -> None:
    chunks = extract_pdf_chunks(
        _pdf_with_text("first page content", "second page content"),
        max_chars=64,
        overlap_chars=0,
    )

    assert [(chunk.page_number, chunk.chunk_index) for chunk in chunks] == [(1, 1), (2, 1)]
    assert [chunk.text for chunk in chunks] == ["first page content", "second page content"]


def test_chunk_text_returns_empty_for_whitespace() -> None:
    assert chunk_text("  \n\t  ") == []


@pytest.mark.parametrize(
    ("max_chars", "overlap_chars"),
    [(0, 0), (10, -1), (10, 10)],
)
def test_chunk_text_rejects_invalid_limits(max_chars: int, overlap_chars: int) -> None:
    with pytest.raises(ValueError):
        chunk_text("some text", max_chars=max_chars, overlap_chars=overlap_chars)


@pytest.mark.parametrize(
    ("pdf_bytes", "message"),
    [
        (b"", "empty"),
        (b"not a pdf", "invalid"),
        (_pdf_with_text(""), "no extractable text"),
    ],
)
def test_extract_pdf_rejects_empty_invalid_or_scanned_documents(pdf_bytes: bytes, message: str) -> None:
    with pytest.raises(DocumentProcessingError, match=message):
        extract_pdf_chunks(pdf_bytes)


class FakeCourseClient:
    def __init__(self, content: bytes, content_type: str = "application/pdf") -> None:
        self.content = content
        self.rows = [{
            "id": "00000000-0000-0000-0000-000000000001",
            "storage_path": "user-a/course.pdf",
            "content_type": content_type,
            "file_size": len(content),
        }]
        self.filters = []
        self.saved = None
        self.downloads = []
        self.storage = self

    def table(self, name):
        assert name == "user_courses"
        return self

    def select(self, columns):
        return self

    def eq(self, column, value):
        self.filters.append((column, value))
        return self

    def execute(self):
        return SimpleNamespace(data=self.rows)

    def from_(self, bucket):
        assert bucket == "user-courses"
        return self

    def download(self, path):
        self.downloads.append(path)
        return self.content

    def rpc(self, name, params):
        assert name == "save_course_extraction"
        self.saved = params
        return self


def test_course_extraction_persists_pages_and_uses_owner_filter() -> None:
    client = FakeCourseClient(_pdf_with_text("first page", "second page"))
    course_id = UUID(client.rows[0]["id"])

    result = CourseExtractionService(client, "user-a").extract(course_id)

    assert result.status == "extracted"
    assert result.chunk_count == 2
    assert client.filters == [("id", str(course_id)), ("owner_id", "user-a")]
    assert client.saved["result_chunks"] == [
        {"text": "first page", "page_number": 1, "chunk_index": 1},
        {"text": "second page", "page_number": 2, "chunk_index": 1},
    ]


@pytest.mark.parametrize("content", [b"invalid pdf", _pdf_with_text("")])
def test_course_extraction_records_parse_failure(content: bytes) -> None:
    client = FakeCourseClient(content)
    result = CourseExtractionService(client, "user-a").extract(UUID(client.rows[0]["id"]))
    assert result.status == "failed"
    assert result.error
    assert client.saved["result_status"] == "failed"
    assert client.saved["result_chunks"] == []


def test_course_extraction_leaves_other_formats_stored_without_parsing() -> None:
    client = FakeCourseClient(b"image content", "image/png")
    result = CourseExtractionService(client, "user-a").extract(UUID(client.rows[0]["id"]))
    assert result.status == "unsupported"
    assert client.downloads == []


def test_course_extraction_rejects_foreign_storage_path() -> None:
    client = FakeCourseClient(b"pdf")
    client.rows[0]["storage_path"] = "other-user/course.pdf"
    with pytest.raises(HTTPException) as raised:
        CourseExtractionService(client, "user-a").extract(UUID(client.rows[0]["id"]))
    assert raised.value.status_code == 403
    assert client.saved is None
    assert client.downloads == []


def test_course_extraction_does_not_download_invisible_course() -> None:
    client = FakeCourseClient(b"pdf")
    client.rows = []
    with pytest.raises(HTTPException) as raised:
        CourseExtractionService(client, "user-b").extract(UUID(int=1))
    assert raised.value.status_code == 404
    assert client.saved is None
    assert client.downloads == []


def test_course_extraction_rejects_oversized_file_before_download() -> None:
    client = FakeCourseClient(b"pdf")
    client.rows[0]["file_size"] = 50 * 1024 * 1024 + 1
    result = CourseExtractionService(client, "user-a").extract(UUID(client.rows[0]["id"]))
    assert result.status == "failed"
    assert client.downloads == []


def test_course_extraction_propagates_jwt_to_storage_and_database(monkeypatch: pytest.MonkeyPatch) -> None:
    course_id = UUID(int=1)
    pdf = _pdf_with_text("private architecture course")
    requests = []

    def send(client, request, **kwargs):
        requests.append(request)
        if request.url.path == "/rest/v1/user_courses":
            return httpx.Response(200, request=request, json=[{
                "id": str(course_id), "storage_path": "user-a/course.pdf",
                "content_type": "application/pdf", "file_size": len(pdf),
            }])
        if request.url.path == "/storage/v1/object/user-courses/user-a/course.pdf":
            return httpx.Response(200, request=request, content=pdf)
        assert request.url.path == "/rest/v1/rpc/save_course_extraction"
        return httpx.Response(200, request=request, json=[])

    monkeypatch.setattr(httpx.Client, "send", send)
    monkeypatch.setattr(courses_module, "get_settings", lambda: Settings(
        "https://example.supabase.co", "test.api.key", "chunks", "test-model",
    ))
    service = get_course_extraction_service(AuthenticatedUser(id="user-a", access_token="user-jwt"))

    result = service.extract(course_id)

    assert result.status == "extracted"
    assert len(requests) == 3
    assert all(request.headers["authorization"] == "Bearer user-jwt" for request in requests)
    assert requests[0].url.params["owner_id"] == "eq.user-a"