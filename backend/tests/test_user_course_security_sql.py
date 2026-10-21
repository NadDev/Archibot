from pathlib import Path


def test_user_courses_and_files_are_private_to_the_owner() -> None:
    sql = (Path(__file__).parents[1] / "sql" / "user_courses.sql").read_text(encoding="utf-8")

    assert "owner_id uuid not null default auth.uid() references auth.users(id) on delete cascade" in sql
    assert "alter table public.user_courses enable row level security;" in sql
    assert "revoke all privileges on table public.user_courses from anon, authenticated;" in sql
    assert "grant select, insert, update, delete on table public.user_courses to authenticated;" in sql
    assert "using (owner_id = (select auth.uid()))" in sql
    assert "with check (owner_id = (select auth.uid()))" in sql
    assert "'user-courses',\n  'user-courses',\n  false" in sql
    assert "bucket_id = 'user-courses'" in sql
    assert "(storage.foldername(name))[1] = (select auth.uid())::text" in sql
    assert "52428800" in sql