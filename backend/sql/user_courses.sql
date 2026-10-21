create table if not exists public.user_courses (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  title text not null check (length(btrim(title)) between 1 and 255),
  course text not null default 'À classer',
  subject text not null default 'À classer',
  study_year text not null default 'Non précisée',
  storage_path text not null unique,
  content_type text not null,
  file_size bigint not null check (file_size > 0),
  created_at timestamptz not null default now()
);

create index if not exists user_courses_owner_created_at_idx
  on public.user_courses (owner_id, created_at desc);

alter table public.user_courses enable row level security;

revoke all privileges on table public.user_courses from anon, authenticated;
grant select, insert, update, delete on table public.user_courses to authenticated;

drop policy if exists user_courses_owner_all on public.user_courses;
create policy user_courses_owner_all on public.user_courses
for all
to authenticated
using (owner_id = (select auth.uid()))
with check (owner_id = (select auth.uid()));

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'user-courses',
  'user-courses',
  false,
  52428800,
  array[
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/png',
    'image/jpeg',
    'image/webp'
  ]::text[]
)
on conflict (id) do update
set public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists user_courses_storage_select on storage.objects;
create policy user_courses_storage_select on storage.objects
for select to authenticated
using (
  bucket_id = 'user-courses'
  and (storage.foldername(name))[1] = (select auth.uid())::text
);

drop policy if exists user_courses_storage_insert on storage.objects;
create policy user_courses_storage_insert on storage.objects
for insert to authenticated
with check (
  bucket_id = 'user-courses'
  and (storage.foldername(name))[1] = (select auth.uid())::text
);

drop policy if exists user_courses_storage_update on storage.objects;
create policy user_courses_storage_update on storage.objects
for update to authenticated
using (
  bucket_id = 'user-courses'
  and (storage.foldername(name))[1] = (select auth.uid())::text
)
with check (
  bucket_id = 'user-courses'
  and (storage.foldername(name))[1] = (select auth.uid())::text
);

drop policy if exists user_courses_storage_delete on storage.objects;
create policy user_courses_storage_delete on storage.objects
for delete to authenticated
using (
  bucket_id = 'user-courses'
  and (storage.foldername(name))[1] = (select auth.uid())::text
);