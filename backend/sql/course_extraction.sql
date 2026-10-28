alter table public.user_courses
  add column if not exists extraction_status text not null default 'pending'
    check (extraction_status in ('pending', 'extracted', 'failed', 'unsupported')),
  add column if not exists extraction_error text,
  add column if not exists extracted_at timestamptz;

create table if not exists public.course_chunks (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null,
  owner_id uuid not null default auth.uid(),
  text text not null check (length(btrim(text)) between 1 and 1200),
  page_number integer not null check (page_number >= 1),
  chunk_index integer not null check (chunk_index >= 1),
  ingested_at timestamptz not null default now(),
  unique (course_id, page_number, chunk_index),
  foreign key (course_id, owner_id)
    references public.user_courses (id, owner_id) on delete cascade
);

create index if not exists course_chunks_owner_course_idx
  on public.course_chunks (owner_id, course_id);
create index if not exists course_chunks_course_owner_idx
  on public.course_chunks (course_id, owner_id);

alter table public.course_chunks enable row level security;
revoke all privileges on table public.course_chunks from anon, authenticated;
grant select, insert, delete on table public.course_chunks to authenticated;

create policy course_chunks_owner_select on public.course_chunks
for select to authenticated using (owner_id = (select auth.uid()));
create policy course_chunks_owner_insert on public.course_chunks
for insert to authenticated with check (owner_id = (select auth.uid()));
create policy course_chunks_owner_delete on public.course_chunks
for delete to authenticated using (owner_id = (select auth.uid()));

create or replace function public.save_course_extraction(
  target_course_id uuid,
  result_status text,
  result_error text,
  result_chunks jsonb
) returns void
language plpgsql security invoker set search_path = ''
as $$
begin
  if auth.uid() is null then
    raise exception 'Authentication required' using errcode = '42501';
  end if;
  perform 1 from public.user_courses
    where id = target_course_id and owner_id = auth.uid() for update;
  if not found then
    raise exception 'Course not found' using errcode = '42501';
  end if;
  if result_status is null or result_status not in ('extracted', 'failed', 'unsupported')
    or result_chunks is null or jsonb_typeof(result_chunks) <> 'array' then
    raise exception 'Invalid extraction result' using errcode = '22023';
  end if;
  if (result_status = 'extracted' and (jsonb_array_length(result_chunks) = 0 or result_error is not null))
    or (result_status <> 'extracted' and (jsonb_array_length(result_chunks) <> 0 or nullif(btrim(result_error), '') is null)) then
    raise exception 'Inconsistent extraction result' using errcode = '22023';
  end if;

  delete from public.course_chunks
    where course_id = target_course_id and owner_id = auth.uid();
  insert into public.course_chunks (course_id, owner_id, text, page_number, chunk_index)
    select target_course_id, auth.uid(), chunk.text, chunk.page_number, chunk.chunk_index
    from jsonb_to_recordset(result_chunks) as chunk(text text, page_number integer, chunk_index integer);
  update public.user_courses
    set extraction_status = result_status, extraction_error = result_error,
        extracted_at = now()
    where id = target_course_id and owner_id = auth.uid();
end;
$$;

revoke all on function public.save_course_extraction(uuid, text, text, jsonb) from public, anon, authenticated;
grant execute on function public.save_course_extraction(uuid, text, text, jsonb) to authenticated;

create or replace function public.project_course_chunks(target_project_id uuid)
returns setof public.course_chunks
language sql stable security invoker set search_path = ''
as $$
  select chunks.* from public.course_chunks as chunks
  join public.project_course_links as links
    on links.course_id = chunks.course_id and links.owner_id = chunks.owner_id
  where links.project_id = target_project_id and chunks.owner_id = auth.uid();
$$;

revoke all on function public.project_course_chunks(uuid) from public, anon, authenticated;
grant execute on function public.project_course_chunks(uuid) to authenticated;