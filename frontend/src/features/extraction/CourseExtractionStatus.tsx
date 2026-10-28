import { RefreshCw } from "lucide-react";
import { extractableContentTypes, type CourseDocument } from "../upload/courses";

export default function CourseExtractionStatus({ course, busy, onExtract }: {
  course: CourseDocument;
  busy: boolean;
  onExtract: (id: string) => void | Promise<void>;
}) {
  return <div className="course-extraction-status" aria-live="polite">
    <span>{busy ? "Extraction en cours…" : course.status}</span>
    {!busy && extractableContentTypes.has(course.contentType)
      && (course.extractionStatus === "pending" || course.extractionStatus === "failed" || course.extractionStatus === "unsupported")
      && <button className="secondary-button" type="button"
      onClick={() => { void onExtract(course.id); }} title="Réessayer le traitement du document">
      <RefreshCw size={16} /> Réessayer
    </button>}
    {course.extractionError && <p role="alert">{course.extractionError}</p>}
    {course.extractionReport && <p>
      Rapport : {course.extractionReport.duration_ms} ms · {course.extractionReport.source_count} source(s)
      {course.extractionReport.average_ocr_confidence !== null
        && ` · Confiance OCR moyenne : ${Math.round(course.extractionReport.average_ocr_confidence * 100)} %`}
      {course.extractionReport.pages.filter((page) => page.error).map((page) =>
        <span key={`${page.locator_type}-${page.locator}`}> · {page.locator} : {page.error}</span>)}
    </p>}
  </div>;
}