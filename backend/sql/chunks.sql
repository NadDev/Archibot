create table if not exists public.chunks (
  id bigserial primary key,
  text text not null,
  source_type text not null check (source_type in ('course', 'general', 'local_regulation')),
  source_id text not null,
  project_id text not null,
  doc_version text not null,
  locality text,
  ingested_at timestamptz not null default now()
);

alter table public.chunks enable row level security;

-- Temporary policy for Sprint 1 smoke tests with publishable key.
drop policy if exists chunks_select_anon on public.chunks;
create policy chunks_select_anon on public.chunks
for select
to anon
using (true);
