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


def test_course_extraction_uses_owner_rls_and_atomic_replacement() -> None:
    sql = (Path(__file__).parents[1] / "sql" / "course_extraction.sql").read_text(encoding="utf-8")
    assert "alter table public.course_chunks enable row level security;" in sql
    assert "references public.user_courses (id, owner_id) on delete cascade" in sql
    assert "revoke all privileges on table public.course_chunks from anon, authenticated;" in sql
    assert "security definer" not in sql
    assert sql.count("security invoker set search_path = ''") == 2
    assert "owner_id = auth.uid() for update" in sql
    assert "delete from public.course_chunks" in sql
    assert "join public.project_course_links" in sql


def test_course_document_locations_preserve_pages_and_support_structural_formats() -> None:
    sql = (Path(__file__).parents[1] / "sql" / "course_document_locations.sql").read_text(encoding="utf-8")
    assert "set locator_type = 'page'" in sql
    assert "alter column page_number drop not null" in sql
    assert "check (locator_type in ('page', 'slide', 'section', 'chapter'))" in sql
    assert "unique (course_id, locator_type, locator, chunk_index)" in sql
    assert "chunk.document_format" in sql
    assert "security invoker set search_path = ''" in sql
    assert "application/vnd.openxmlformats-officedocument.presentationml.presentation" in sql
    assert "application/epub+zip" in sql