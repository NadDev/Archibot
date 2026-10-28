alter table public.chunks
  add column if not exists locator_type text,
  add column if not exists locator text,
  add column if not exists source_order integer;

alter table public.architecture_knowledge_chunks
  add column if not exists locator_type text,
  add column if not exists locator text,
  add column if not exists source_order integer;

alter table public.course_chunks
  add column if not exists locator_type text,
  add column if not exists locator text,
  add column if not exists source_order integer,
  add column if not exists document_format text;

update public.course_chunks
set locator_type = 'page',
    locator = 'Page ' || page_number::text,
    source_order = page_number,
    document_format = coalesce(document_format, 'pdf')
where locator_type is null or locator is null or source_order is null or document_format is null;

alter table public.course_chunks
  alter column page_number drop not null,
  alter column locator_type set not null,
  alter column locator set not null,
  alter column source_order set not null,
  alter column document_format set not null;

alter table public.course_chunks
  drop constraint if exists course_chunks_course_id_page_number_chunk_index_key,
  add constraint course_chunks_locator_type_check
    check (locator_type in ('page', 'slide', 'section', 'chapter')),
  add constraint course_chunks_locator_check
    check (length(btrim(locator)) between 1 and 500),
  add constraint course_chunks_source_order_check
    check (source_order >= 1),
  add constraint course_chunks_document_format_check
    check (document_format in ('pdf', 'docx', 'pptx', 'epub')),
  add constraint course_chunks_page_locator_check
    check ((locator_type = 'page' and page_number = source_order)
      or (locator_type <> 'page' and page_number is null)),
  add constraint course_chunks_course_locator_chunk_key
    unique (course_id, locator_type, locator, chunk_index);

create index if not exists course_chunks_owner_order_idx
  on public.course_chunks (owner_id, course_id, source_order, chunk_index);

update storage.buckets
set allowed_mime_types = array[
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'application/epub+zip',
  'image/png',
  'image/jpeg',
  'image/webp'
]::text[]
where id = 'user-courses';

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
  insert into public.course_chunks (
    course_id, owner_id, text, page_number, chunk_index, locator_type, locator, source_order, document_format
  )
    select target_course_id, auth.uid(), chunk.text, chunk.page_number, chunk.chunk_index,
      chunk.locator_type, chunk.locator, chunk.source_order, chunk.document_format
    from jsonb_to_recordset(result_chunks) as chunk(
      text text, page_number integer, chunk_index integer, locator_type text, locator text,
      source_order integer, document_format text
    );
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