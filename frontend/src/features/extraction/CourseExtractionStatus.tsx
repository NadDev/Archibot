import { RefreshCw } from "lucide-react";
import type { CourseDocument } from "../upload/courses";

export default function CourseExtractionStatus({ course, busy, onExtract }: {
  course: CourseDocument;
  busy: boolean;
  onExtract: (id: string) => void | Promise<void>;
}) {
  return <div className="course-extraction-status" aria-live="polite">
    <span>{busy ? "Extraction en cours…" : course.status}</span>
    {!busy && course.contentType === "application/pdf"
      && (course.extractionStatus === "pending" || course.extractionStatus === "failed")
      && <button className="secondary-button" type="button"
      onClick={() => { void onExtract(course.id); }} title="Réessayer le traitement du document">
      <RefreshCw size={16} /> Réessayer
    </button>}
    {course.extractionError && <p role="alert">{course.extractionError}</p>}
  </div>;
}