alter table public.user_courses
  add column if not exists extraction_report jsonb not null default '{}'::jsonb,
  add constraint user_courses_extraction_report_check
    check (jsonb_typeof(extraction_report) = 'object' and pg_column_size(extraction_report) <= 32768);

create or replace function public.save_course_extraction(
  target_course_id uuid,
  result_status text,
  result_error text,
  result_chunks jsonb,
  result_report jsonb
) returns void
language plpgsql security invoker set search_path = ''
as $$
begin
  if result_report is null
    or jsonb_typeof(result_report) <> 'object'
    or pg_column_size(result_report) > 32768
    or result_report ->> 'error' is distinct from result_error then
    raise exception 'Invalid extraction report' using errcode = '22023';
  end if;
  if coalesce(jsonb_typeof(result_report -> 'pages'), '') <> 'array' then
    raise exception 'Invalid extraction report pages' using errcode = '22023';
  end if;
  if jsonb_array_length(result_report -> 'pages') > 31 then
    raise exception 'Too many extraction report pages' using errcode = '22023';
  end if;

  perform public.save_course_extraction(
    target_course_id, result_status, result_error, result_chunks
  );

  update public.user_courses
    set extraction_report = result_report
    where id = target_course_id and owner_id = auth.uid();
end;
$$;

revoke all on function public.save_course_extraction(uuid, text, text, jsonb, jsonb)
  from public, anon, authenticated;
grant execute on function public.save_course_extraction(uuid, text, text, jsonb, jsonb)
  to authenticated;