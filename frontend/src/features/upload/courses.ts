import { supabase } from "../../supabase";

export type ExtractionStatus = "pending" | "extracted" | "failed" | "unsupported";
export type CourseDocument = {
  id: string;
  title: string;
  course: string;
  subject: string;
  studyYear: string;
  meta: string;
  status: string;
  storagePath: string;
  contentType: string;
  extractionStatus: ExtractionStatus;
  extractionError: string | null;
};
export type CourseRow = {
  id: string;
  title: string;
  course: string;
  subject: string;
  study_year: string;
  storage_path: string;
  content_type: string;
  file_size: number;
  created_at: string;
  extraction_status: ExtractionStatus;
  extraction_error: string | null;
};

export const courseColumns = "id, title, course, subject, study_year, storage_path, content_type, file_size, created_at, extraction_status, extraction_error";
export const extractionLabels: Record<ExtractionStatus, string> = {
  pending: "Extraction en attente",
  extracted: "Texte extrait",
  failed: "Extraction en échec",
  unsupported: "Format non pris en charge",
};
const courseMimeTypes: Record<string, string> = {
  pdf: "application/pdf",
  doc: "application/msword",
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  webp: "image/webp",
};

export function mapCourse(row: CourseRow): CourseDocument {
  return {
    id: row.id,
    title: row.title,
    course: row.course,
    subject: row.subject,
    studyYear: row.study_year,
    meta: `${(row.file_size / (1024 * 1024)).toFixed(1)} Mo · Ajouté le ${new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "short" }).format(new Date(row.created_at))}`,
    status: extractionLabels[row.extraction_status],
    storagePath: row.storage_path,
    contentType: row.content_type,
    extractionStatus: row.extraction_status,
    extractionError: row.extraction_error,
  };
}

export async function uploadCourse(file: File, userId: string, subject: string, studyYear: string): Promise<CourseDocument> {
  if (!supabase) throw new Error("Connexion indisponible.");
  const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
  const contentType = courseMimeTypes[extension];
  if (!contentType || file.size <= 0 || file.size > 50 * 1024 * 1024) {
    throw new Error("Format non accepté ou taille hors limite (50 Mo).");
  }
  const storagePath = `${userId}/${crypto.randomUUID()}.${extension}`;
  const { error: uploadError } = await supabase.storage.from("user-courses")
    .upload(storagePath, file, { contentType, upsert: false });
  if (uploadError) throw uploadError;

  const { data, error } = await supabase.from("user_courses").insert({
    title: file.name,
    course: subject,
    subject,
    study_year: studyYear,
    storage_path: storagePath,
    content_type: contentType,
    file_size: file.size,
  }).select(courseColumns).single();
  if (error) {
    await supabase.storage.from("user-courses").remove([storagePath]);
    throw error;
  }
  return mapCourse(data as CourseRow);
}