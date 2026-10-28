alter table public.course_chunks
  drop constraint if exists course_chunks_locator_type_check,
  add constraint course_chunks_locator_type_check
    check (locator_type in ('page', 'slide', 'section', 'chapter', 'image')),
  drop constraint if exists course_chunks_document_format_check,
  add constraint course_chunks_document_format_check
    check (document_format in ('pdf', 'doc', 'docx', 'ppt', 'pptx', 'epub', 'png', 'jpeg', 'webp'));

update storage.buckets
set allowed_mime_types = array[
  'application/pdf',
  'application/msword',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'application/epub+zip',
  'image/png',
  'image/jpeg',
  'image/webp'
]::text[]
where id = 'user-courses';