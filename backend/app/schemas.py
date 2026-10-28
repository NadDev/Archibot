from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    COURSE = "course"
    GENERAL = "general"
    LOCAL_REGULATION = "local_regulation"


class ChunkVisibility(str, Enum):
    PRIVATE = "private"
    SHARED = "shared"


class ChunkMetadata(BaseModel):
    source_type: SourceType
    source_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    doc_version: str = Field(min_length=1)
    locality: Optional[str] = None
    page_number: Optional[int] = Field(default=None, ge=1)
    chunk_index: Optional[int] = Field(default=None, ge=1)
    locator_type: Optional[Literal["page", "slide", "section", "chapter", "image"]] = None
    locator: Optional[str] = Field(default=None, min_length=1, max_length=500)
    source_order: Optional[int] = Field(default=None, ge=1)
    ingested_at: datetime
    visibility: ChunkVisibility = ChunkVisibility.PRIVATE


class Citation(BaseModel):
    source_id: str = Field(min_length=1)
    excerpt: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)


class ResponseSection(BaseModel):
    text: str = Field(min_length=1)
    citations: List[Citation] = Field(default_factory=list)


class AssistantResponse(BaseModel):
    schema_version: str = Field(default="v1")
    cours: ResponseSection
    regle_generale: ResponseSection
    source_reglementaire_locale: ResponseSection
    warning_no_source: Optional[str] = None


class RetrievalQuery(BaseModel):
    question: str = Field(min_length=3)
    project_id: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    locality: Optional[str] = None
    min_score: float = Field(default=0.05, ge=0.0, le=1.0)


class RetrievedChunk(BaseModel):
    text: str = Field(min_length=1)
    metadata: ChunkMetadata
    score: float = Field(ge=0.0, le=1.0)


class RetrievalResponse(BaseModel):
    total: int = Field(ge=0)
    items: List[RetrievedChunk] = Field(default_factory=list)


class AskRequest(BaseModel):
    question: str = Field(min_length=3)
    project_id: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    locality: Optional[str] = None


class IngestChunk(BaseModel):
    text: str = Field(min_length=1)
    metadata: ChunkMetadata


class IngestRequest(BaseModel):
    chunks: List[IngestChunk] = Field(min_length=1)


class IngestResponse(BaseModel):
    inserted: int = Field(ge=0)
