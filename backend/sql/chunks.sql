create table if not exists public.chunks (
  id bigserial primary key,
  owner_id uuid references auth.users(id) on delete cascade,
  text text not null,
  source_type text not null check (source_type in ('course', 'general', 'local_regulation')),
  source_id text not null,
  project_id text not null,
  doc_version text not null,
  locality text,
  ingested_at timestamptz not null default now()
);

alter table public.chunks
  add column if not exists owner_id uuid references auth.users(id) on delete cascade;

alter table public.chunks enable row level security;

drop policy if exists chunks_select_anon on public.chunks;
drop policy if exists chunks_owner_all on public.chunks;
revoke all privileges on table public.chunks from anon, authenticated;
grant select, insert, update, delete on table public.chunks to authenticated;
grant usage, select on sequence public.chunks_id_seq to authenticated;

create policy chunks_owner_all on public.chunks
for all
to authenticated
using (owner_id = (select auth.uid()))
with check (owner_id = (select auth.uid()));

create table if not exists public.architecture_knowledge_chunks (
  id bigserial primary key,
  text text not null,
  source_id text not null,
  doc_version text not null,
  locality text,
  ingested_at timestamptz not null default now()
);

alter table public.architecture_knowledge_chunks enable row level security;

revoke all privileges on table public.architecture_knowledge_chunks from anon, authenticated;
grant select on table public.architecture_knowledge_chunks to authenticated;

drop policy if exists architecture_knowledge_authenticated_read
  on public.architecture_knowledge_chunks;
create policy architecture_knowledge_authenticated_read
on public.architecture_knowledge_chunks
for select
to authenticated
using ((select auth.uid()) is not null);
