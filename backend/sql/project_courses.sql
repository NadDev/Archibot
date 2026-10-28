create unique index if not exists projects_id_owner_id_uidx
  on public.projects (id, owner_id);

create unique index if not exists user_courses_id_owner_id_uidx
  on public.user_courses (id, owner_id);

create table if not exists public.project_course_links (
  project_id uuid not null,
  course_id uuid not null,
  owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (project_id, course_id),
  constraint project_course_links_project_owner_fk
    foreign key (project_id, owner_id)
    references public.projects (id, owner_id)
    on delete cascade,
  constraint project_course_links_course_owner_fk
    foreign key (course_id, owner_id)
    references public.user_courses (id, owner_id)
    on delete cascade
);

create index if not exists project_course_links_owner_project_idx
  on public.project_course_links (owner_id, project_id);

create index if not exists project_course_links_project_owner_fk_idx
  on public.project_course_links (project_id, owner_id);

create index if not exists project_course_links_course_owner_fk_idx
  on public.project_course_links (course_id, owner_id);

alter table public.project_course_links enable row level security;

revoke all privileges on table public.project_course_links from anon, authenticated;
grant select, insert, delete on table public.project_course_links to authenticated;

drop policy if exists project_course_links_owner_select on public.project_course_links;
create policy project_course_links_owner_select on public.project_course_links
for select to authenticated
using (owner_id = (select auth.uid()));

drop policy if exists project_course_links_owner_insert on public.project_course_links;
create policy project_course_links_owner_insert on public.project_course_links
for insert to authenticated
with check (owner_id = (select auth.uid()));

drop policy if exists project_course_links_owner_delete on public.project_course_links;
create policy project_course_links_owner_delete on public.project_course_links
for delete to authenticated
using (owner_id = (select auth.uid()));