import { useEffect, useState } from "react";
import { Download, ExternalLink, FileText } from "lucide-react";

import { supabase } from "../../supabase";
import type { CourseDocument } from "../upload/courses";

export default function CourseDocumentPreview({ course }: { course: CourseDocument }) {
  const [url, setUrl] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setUrl(null);
    setError("");
    setLoading(true);

    if (!supabase) {
      setError("Connexion au stockage indisponible.");
      setLoading(false);
      return () => { active = false; };
    }

    void supabase.storage.from("user-courses").createSignedUrl(course.storagePath, 600)
      .then(({ data, error: signedUrlError }) => {
        if (!active) return;
        if (signedUrlError) {
          setError("Aperçu indisponible. Vérifie l’accès au fichier ou télécharge-le depuis la bibliothèque.");
        } else {
          setUrl(data.signedUrl);
        }
        setLoading(false);
      })
      .catch(() => {
        if (!active) return;
        setError("Aperçu indisponible. Vérifie ta connexion puis réessaie.");
        setLoading(false);
      });

    return () => { active = false; };
  }, [course.id, course.storagePath]);

  return <section className="course-document-preview" aria-label="Document original">
    <div className="course-document-preview-head">
      <span><FileText size={16} /> Document original</span>
      {url && <a href={url} download={course.title}>
        <Download size={15} /> Télécharger
      </a>}
    </div>
    {loading ? <p className="course-document-preview-message" role="status">Chargement du document…</p>
      : error ? <p className="course-document-preview-message" role="alert">{error}</p>
        : url && course.contentType.startsWith("image/")
          ? <div className="course-document-image-wrap"><img src={url} alt={course.title} /></div>
          : url && course.contentType === "application/pdf"
            ? <iframe className="course-document-pdf" src={url} title={`Aperçu de ${course.title}`} />
            : url && <div className="course-document-preview-message">
              <p>L’aperçu intégré n’est pas disponible pour ce format.</p>
              <a href={url} target="_blank" rel="noreferrer">
                <ExternalLink size={15} /> Ouvrir {course.title}
              </a>
            </div>}
  </section>;
}
