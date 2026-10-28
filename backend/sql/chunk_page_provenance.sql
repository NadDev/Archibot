alter table public.chunks
  add column if not exists page_number integer check (page_number is null or page_number >= 1),
  add column if not exists chunk_index integer check (chunk_index is null or chunk_index >= 1);

alter table public.architecture_knowledge_chunks
  add column if not exists page_number integer check (page_number is null or page_number >= 1),
  add column if not exists chunk_index integer check (chunk_index is null or chunk_index >= 1);