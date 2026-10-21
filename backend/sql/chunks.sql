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

-- Keep public access closed until authenticated owner/project policies exist.
drop policy if exists chunks_select_anon on public.chunks;
revoke all privileges on table public.chunks from anon;
