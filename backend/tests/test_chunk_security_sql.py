from pathlib import Path


def test_private_chunks_are_restricted_to_authenticated_owner() -> None:
    sql = (Path(__file__).parents[1] / "sql" / "chunks.sql").read_text(encoding="utf-8")

    assert "alter table public.chunks enable row level security;" in sql
    assert "owner_id uuid not null references auth.users(id) on delete cascade" in sql
    assert "revoke all privileges on table public.chunks from anon, authenticated;" in sql
    assert "grant select, insert, update, delete on table public.chunks to authenticated;" in sql
    assert "using (owner_id = (select auth.uid()))" in sql
    assert "with check (owner_id = (select auth.uid()))" in sql
    assert "create policy chunks_select_anon" not in sql


def test_global_architecture_corpus_is_authenticated_read_only() -> None:
    sql = (Path(__file__).parents[1] / "sql" / "chunks.sql").read_text(encoding="utf-8")

    assert "create table if not exists public.architecture_knowledge_chunks" in sql
    assert "alter table public.architecture_knowledge_chunks enable row level security;" in sql
    assert "grant select on table public.architecture_knowledge_chunks to authenticated;" in sql
    assert "create policy architecture_knowledge_authenticated_read" in sql
    assert "to authenticated\nusing ((select auth.uid()) is not null);" in sql


def test_chunk_page_provenance_is_migrated_for_private_and_shared_corpora() -> None:
    sql = (Path(__file__).parents[1] / "sql" / "chunk_page_provenance.sql").read_text(encoding="utf-8")
    initial_sql = (Path(__file__).parents[1] / "sql" / "chunks.sql").read_text(encoding="utf-8")

    assert "alter table public.chunks" in sql
    assert "add column if not exists page_number integer" in sql
    assert "add column if not exists chunk_index integer" in sql
    assert "alter table public.architecture_knowledge_chunks" in sql
    assert initial_sql.count("page_number integer") == 2
    assert initial_sql.count("chunk_index integer") == 2