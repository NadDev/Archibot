from pathlib import Path


def test_projects_are_private_to_the_authenticated_owner() -> None:
    sql = (Path(__file__).parents[1] / "sql" / "projects.sql").read_text(encoding="utf-8")

    assert "owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade" in sql
    assert "alter table public.projects enable row level security;" in sql
    assert "revoke all privileges on table public.projects from anon, authenticated;" in sql
    assert "grant select, insert, update, delete on table public.projects to authenticated;" in sql
    assert "create policy projects_owner_all on public.projects" in sql
    assert "using (owner_id = (select auth.uid()))" in sql
    assert "with check (owner_id = (select auth.uid()))" in sql


def test_project_course_links_require_the_same_owner() -> None:
    sql = (Path(__file__).parents[1] / "sql" / "project_courses.sql").read_text(encoding="utf-8")

    assert "foreign key (project_id, owner_id)" in sql
    assert "references public.projects (id, owner_id)" in sql
    assert "foreign key (course_id, owner_id)" in sql
    assert "references public.user_courses (id, owner_id)" in sql
    assert "alter table public.project_course_links enable row level security;" in sql
    assert "grant select, insert, delete on table public.project_course_links to authenticated;" in sql
    assert "owner_id = (select auth.uid())" in sql
    assert "on public.project_course_links (project_id, owner_id)" in sql
    assert "on public.project_course_links (course_id, owner_id)" in sql