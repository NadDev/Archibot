create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  name text not null check (length(btrim(name)) between 1 and 80),
  project_type text not null default 'Projet d’architecture',
  status text not null default 'En cours'
    check (status in ('En cours', 'À reprendre', 'Terminé')),
  progress smallint not null default 0 check (progress between 0 and 100),
  location text not null default 'À préciser',
  term text not null default 'Nouveau projet',
  summary text not null default 'Ajoute un peu de contexte pour commencer à organiser ton travail et tes références.',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists projects_owner_updated_at_idx
  on public.projects (owner_id, updated_at desc);

create or replace function public.set_projects_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists projects_updated_at on public.projects;
create trigger projects_updated_at
before update on public.projects
for each row execute function public.set_projects_updated_at();

alter table public.projects enable row level security;

revoke all privileges on table public.projects from anon, authenticated;
grant select, insert, update, delete on table public.projects to authenticated;

drop policy if exists projects_owner_all on public.projects;
create policy projects_owner_all on public.projects
for all
to authenticated
using (owner_id = (select auth.uid()))
with check (owner_id = (select auth.uid()));