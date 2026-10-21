from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_CORS_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


@dataclass(frozen=True)
class Settings:
    supabase_url: str | None
    supabase_publishable_key: str | None
    chunks_table: str
    embedding_model: str
    cors_origins: tuple[str, ...] = DEFAULT_CORS_ORIGINS



def get_settings() -> Settings:
    return Settings(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_publishable_key=os.getenv("SUPABASE_PUBLISHABLE_KEY"),
        chunks_table=os.getenv("ARCHIBOT_CHUNKS_TABLE", "chunks"),
        embedding_model=os.getenv(
            "FASTEMBED_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        ),
        cors_origins=tuple(
            origin.strip()
            for origin in os.getenv(
                "ARCHIBOT_CORS_ORIGINS",
                ",".join(DEFAULT_CORS_ORIGINS),
            ).split(",")
            if origin.strip()
        ),
    )
