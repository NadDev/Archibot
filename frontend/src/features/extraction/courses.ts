import { apiFetch } from "../../api";
import type { ExtractionStatus } from "../upload/courses";

type ExtractionResult = {
  course_id: string;
  status: Exclude<ExtractionStatus, "pending">;
  chunk_count: number;
  error: string | null;
};

export async function extractCourse(courseId: string): Promise<ExtractionResult> {
  const response = await apiFetch(`/v1/courses/${encodeURIComponent(courseId)}/extract`, {
    method: "POST",
    signal: AbortSignal.timeout(120_000),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(typeof body?.detail === "string" ? body.detail : "Extraction indisponible. Réessaie.");
  }
  return response.json() as Promise<ExtractionResult>;
}