from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    supabase_url: str | None
    supabase_publishable_key: str | None
    chunks_table: str
    embedding_model: str



def get_settings() -> Settings:
    return Settings(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_publishable_key=os.getenv("SUPABASE_PUBLISHABLE_KEY"),
        chunks_table=os.getenv("ARCHIBOT_CHUNKS_TABLE", "chunks"),
        embedding_model=os.getenv(
            "FASTEMBED_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        ),
    )
