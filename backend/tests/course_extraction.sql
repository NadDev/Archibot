begin;
select set_config('test.owner', gen_random_uuid()::text, true);
select set_config('test.other', gen_random_uuid()::text, true);
select set_config('test.course', gen_random_uuid()::text, true);
select set_config('test.project', gen_random_uuid()::text, true);
insert into auth.users (id) values
  (current_setting('test.owner')::uuid), (current_setting('test.other')::uuid);

set local role authenticated;
select set_config('request.jwt.claim.sub', current_setting('test.owner'), true);
insert into public.user_courses (id, title, storage_path, content_type, file_size)
values (current_setting('test.course')::uuid, 'Extraction test',
  current_setting('test.owner') || '/test.pdf', 'application/pdf', 100);
insert into public.projects (id, name) values (current_setting('test.project')::uuid, 'Extraction test');
insert into public.project_course_links (project_id, course_id)
values (current_setting('test.project')::uuid, current_setting('test.course')::uuid);

select public.save_course_extraction(current_setting('test.course')::uuid, 'extracted', null,
  '[{"text":"first page","page_number":1,"chunk_index":1,"locator_type":"page","locator":"Page 1","source_order":1,"document_format":"pdf"},{"text":"second page","page_number":2,"chunk_index":1,"locator_type":"page","locator":"Page 2","source_order":2,"document_format":"pdf"}]');
select public.save_course_extraction(current_setting('test.course')::uuid, 'extracted', null,
  '[{"text":"first page","page_number":1,"chunk_index":1,"locator_type":"page","locator":"Page 1","source_order":1,"document_format":"pdf"},{"text":"second page","page_number":2,"chunk_index":1,"locator_type":"page","locator":"Page 2","source_order":2,"document_format":"pdf"}]');
do $$
begin
  if (select count(*) from public.project_course_chunks(current_setting('test.project')::uuid)) <> 2 then
    raise exception 'Repeated extraction must return exactly two linked chunks';
  end if;
  if (select extraction_status from public.user_courses where id = current_setting('test.course')::uuid) <> 'extracted' then
    raise exception 'Extraction status not saved';
  end if;
  if (select count(*) from public.project_course_chunks(gen_random_uuid())) <> 0 then
    raise exception 'Unlinked project must not retrieve chunks';
  end if;
  begin
    perform public.save_course_extraction(current_setting('test.course')::uuid, 'extracted', null,
      '[{"text":"invalid page","page_number":0,"chunk_index":1,"locator_type":"page","locator":"Page 0","source_order":0,"document_format":"pdf"}]');
    raise exception 'Invalid provenance accepted';
  exception when check_violation then null;
  end;
  if (select count(*) from public.project_course_chunks(current_setting('test.project')::uuid)) <> 2 then
    raise exception 'Failed replacement lost previous chunks';
  end if;
end;
$$;

select set_config('request.jwt.claim.sub', current_setting('test.other'), true);
do $$
begin
  if exists (select 1 from public.course_chunks where course_id = current_setting('test.course')::uuid) then
    raise exception 'Cross-user read allowed';
  end if;
  if exists (select 1 from public.project_course_chunks(current_setting('test.project')::uuid)) then
    raise exception 'Cross-user retrieval allowed';
  end if;
  begin
    perform public.save_course_extraction(current_setting('test.course')::uuid, 'failed', 'forbidden', '[]');
    raise exception 'Cross-user extraction allowed';
  exception when insufficient_privilege then null;
  end;
  begin
    insert into public.course_chunks (
      course_id, owner_id, text, page_number, chunk_index, locator_type, locator, source_order, document_format
    ) values (
      current_setting('test.course')::uuid, current_setting('test.owner')::uuid,
      'forbidden', 3, 1, 'page', 'Page 3', 3, 'pdf'
    );
    raise exception 'Cross-user insert allowed';
  exception when insufficient_privilege then null;
  end;
  begin
    insert into public.course_chunks (
      course_id, text, page_number, chunk_index, locator_type, locator, source_order, document_format
    ) values (
      current_setting('test.course')::uuid, 'forbidden', 3, 1, 'page', 'Page 3', 3, 'pdf'
    );
    raise exception 'Foreign course association allowed';
  exception when foreign_key_violation then null;
  end;
  delete from public.course_chunks where course_id = current_setting('test.course')::uuid;
  if found then raise exception 'Cross-user delete allowed'; end if;
  if has_table_privilege('authenticated', 'public.course_chunks', 'update') then
    raise exception 'Unnecessary update privilege';
  end if;
  if has_table_privilege('anon', 'public.course_chunks', 'select,insert,update,delete')
    or has_function_privilege('anon', 'public.save_course_extraction(uuid,text,text,jsonb)', 'execute')
    or has_function_privilege('anon', 'public.project_course_chunks(uuid)', 'execute') then
    raise exception 'Anonymous privileges exposed';
  end if;
end;
$$;

select set_config('request.jwt.claim.sub', current_setting('test.owner'), true);
do $$
begin
  if (select count(*) from public.course_chunks where course_id = current_setting('test.course')::uuid) <> 2 then
    raise exception 'Cross-user attempts changed owner data';
  end if;
end;
$$;
select public.save_course_extraction(current_setting('test.course')::uuid, 'failed', 'OCR required', '[]');
do $$
begin
  if exists (select 1 from public.course_chunks where course_id = current_setting('test.course')::uuid) then
    raise exception 'Failed extraction retained obsolete chunks';
  end if;
  if (select extraction_error from public.user_courses where id = current_setting('test.course')::uuid) <> 'OCR required' then
    raise exception 'Failure reason not saved';
  end if;
end;
$$;
select public.save_course_extraction(current_setting('test.course')::uuid, 'extracted', null,
  '[{"text":"first page","page_number":1,"chunk_index":1,"locator_type":"page","locator":"Page 1","source_order":1,"document_format":"pdf"}]');
delete from public.user_courses where id = current_setting('test.course')::uuid;
do $$
begin
  if exists (select 1 from public.course_chunks where course_id = current_setting('test.course')::uuid) then
    raise exception 'Course deletion left orphan chunks';
  end if;
end;
$$;
rollback;