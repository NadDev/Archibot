import { useEffect, useMemo, useRef, useState, type FormEvent, type ReactNode } from "react";
import {
  ArrowDownLeft,
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Clock3,
  Download,
  FileImage,
  FileText,
  FolderKanban,
  GraduationCap,
  HardDriveDownload,
  LayoutGrid,
  LibraryBig,
  LogOut,
  Menu,
  MessageSquareText,
  MoreHorizontal,
  Plus,
  Search,
  Send,
  Settings2,
  Sparkles,
  Trash2,
  Upload,
  X,
} from "lucide-react";
import type { Session } from "@supabase/supabase-js";

import AuthScreen from "./AuthScreen";
import { supabase } from "./supabase";
import { courseColumns, extractionLabels, mapCourse, uploadCourse, type CourseDocument, type CourseRow } from "./features/upload/courses";
import { extractCourse } from "./features/extraction/courses";
import CourseExtractionStatus from "./features/extraction/CourseExtractionStatus";

const assistantPortrait = new URL("../../docs/image.png", import.meta.url).href;

type Section = "chat" | "documents" | "exercises" | "notes";
type ProjectStatus = "En cours" | "À reprendre" | "Terminé";
type ProjectNote = { id: string; label: string; text: string; created: string; tone: "clay" | "sage" | "blue" };
type Project = {
  id: string;
  name: string;
  type: string;
  status: ProjectStatus;
  updated: string;
  progress: number;
  location: string;
  term: string;
  summary: string;
  files: { id: string; name: string; meta: string; state: string; icon: "plan" | "pdf" | "image" }[];
  notes: ProjectNote[];
};
type ProjectRow = {
  id: string;
  name: string;
  project_type: string;
  status: ProjectStatus;
  updated_at: string;
  progress: number;
  location: string;
  term: string;
  summary: string;
};
type ChatItem = { id: number; role: "student" | "assistant"; text: string; time: string };

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === "object" && error !== null && "message" in error && typeof error.message === "string") {
    return error.message;
  }
  return String(error);
}

function getTableSetupMessage(error: unknown, tableLabel: string, sqlFile: string): string {
  const message = getErrorMessage(error);
  if (/PGRST205|could not find the table|schema cache|relation .* does not exist/i.test(message)) {
    return `La configuration ${tableLabel} manque dans Supabase. Exécute backend/sql/${sqlFile} dans le SQL Editor, puis réessaie.`;
  }
  return message;
}

const studyYearOptions = ["1re année", "2e année", "Transversale", "Non précisée"];

const suggestedQuestions = [
  "Comment améliorer la lumière naturelle ?",
  "Aide-moi à clarifier mon concept",
  "Propose un exercice sur les portées",
];

const statusClass: Record<ProjectStatus, string> = {
  "En cours": "status-active",
  "À reprendre": "status-paused",
  Terminé: "status-done",
};

function mapProject(row: ProjectRow): Project {
  return {
    id: row.id,
    name: row.name,
    type: row.project_type,
    status: row.status,
    updated: `Modifié le ${new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "short" }).format(new Date(row.updated_at))}`,
    progress: row.progress,
    location: row.location,
    term: row.term,
    summary: row.summary,
    files: [],
    notes: [],
  };
}

function ProjectArtwork({ variant = "one" }: { variant?: "one" | "two" | "three" }) {
  const shapes = {
    one: <><path d="M23 83 74 46l51 23-51 38z" /><path d="m36 78 38-27v44L36 122z" /><path d="m79 95 38-27v43l-38 27z" /><path d="m74 46 38 17-38 27-38-12z" /><path d="M42 79v21m14-32v42m44-3V82m12-7v30" className="art-line" /></>,
    two: <><path d="m24 96 43-48 64 24-43 49z" /><path d="m40 88 27-31v41l-27 31z" /><path d="m70 99 44-18v39l-44 17z" /><path d="m67 48 65 24-18 9-47-24z" /><path d="M48 82v24m14-39v43m32-8v24m12-41v37" className="art-line" /></>,
    three: <><path d="m20 91 54-42 55 28-53 39z" /><path d="m31 86 43-32v46l-43 34z" /><path d="m77 108 40-30v39l-40 29z" /><path d="m74 49 55 28-11 8-44-22z" /><path d="M42 80v28m15-39v42m45-5v33m11-48v32" className="art-line" /></>,
  };
  return (
    <div className={`project-art art-${variant}`} aria-hidden="true">
      <span className="art-sun" />
      <svg viewBox="0 0 150 160" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path className="art-ground" d="m8 126 61-32 72 30-62 34z" />
        <g className="art-building" strokeLinejoin="round">{shapes[variant]}</g>
        <path className="art-tree" d="M18 120q-8-21 1-30 12 8 9 22 6-15 15-15 4 12-7 27l-7 12z" />
        <path className="art-tree" d="M122 112q-5-17 4-24 10 10 5 22 6-10 14-7 1 10-9 20l-8 6z" />
        <path className="art-shadow" d="m24 132 50-26 55 21-51 28z" />
      </svg>
      <span className="art-tag">{variant === "one" ? "01 / HABITER" : variant === "two" ? "02 / RENCONTRER" : "03 / RÉHABITER"}</span>
    </div>
  );
}

function ProjectIcon({ kind }: { kind: Project["files"][number]["icon"] }) {
  if (kind === "plan") return <LayoutGrid size={18} />;
  if (kind === "image") return <FileImage size={18} />;
  return <FileText size={18} />;
}

function WorkspaceApp({ displayName, greetingName, userEmail, userId, onSignOut }: { displayName: string; greetingName: string | null; userEmail: string; userId: string; onSignOut: () => void }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState("");
  const [projectsReloadKey, setProjectsReloadKey] = useState(0);
  const [projectSaving, setProjectSaving] = useState(false);
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);
  const [showCourseLibrary, setShowCourseLibrary] = useState(false);
  const [reviewingCourseId, setReviewingCourseId] = useState<string | null>(null);
  const [generalCourses, setGeneralCourses] = useState<CourseDocument[]>([]);
  const [coursesLoading, setCoursesLoading] = useState(true);
  const [coursesError, setCoursesError] = useState("");
  const [coursesReloadKey, setCoursesReloadKey] = useState(0);
  const [courseSaving, setCourseSaving] = useState(false);
  const [extractingCourseIds, setExtractingCourseIds] = useState<string[]>([]);
  const extractionRequests = useRef(new Set<string>());
  const [courseSearch, setCourseSearch] = useState("");
  const [courseSubjectFilter, setCourseSubjectFilter] = useState("all");
  const [courseYearFilter, setCourseYearFilter] = useState("all");
  const [newCourseSubject, setNewCourseSubject] = useState("À classer");
  const [newCourseYear, setNewCourseYear] = useState("Non précisée");
  const [courseContextByProject, setCourseContextByProject] = useState<Record<string, string[]>>({});
  const [newSummary, setNewSummary] = useState("");
  const [newProjectCourseIds, setNewProjectCourseIds] = useState<string[]>([]);
  const [projectCourseSearch, setProjectCourseSearch] = useState("");
  const [section, setSection] = useState<Section>("chat");
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newType, setNewType] = useState("Projet d’architecture");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [toast, setToast] = useState("");
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState<ChatItem[]>([]);
  const [chatByProject, setChatByProject] = useState<Record<string, ChatItem[]>>({});
  const [fileSearch, setFileSearch] = useState("");
  const [showAllHistory, setShowAllHistory] = useState(false);
  const [exerciseAnswer, setExerciseAnswer] = useState("");
  const [exerciseSubmitted, setExerciseSubmitted] = useState(false);

  useEffect(() => {
    let isCurrent = true;
    async function loadProjects() {
      setProjectsLoading(true);
      setProjectsError("");
      try {
        if (!supabase) throw new Error("La connexion à Supabase n’est pas configurée.");
        const { data, error } = await supabase
          .from("projects")
          .select("id, name, project_type, status, updated_at, progress, location, term, summary")
          .order("updated_at", { ascending: false });
        if (error) throw error;
        if (isCurrent) setProjects((data ?? []).map((row) => mapProject(row as ProjectRow)));
      } catch (error) {
        if (isCurrent) {
          setProjectsError(getTableSetupMessage(error, "des projets", "projects.sql"));
        }
      } finally {
        if (isCurrent) setProjectsLoading(false);
      }
    }
    void loadProjects();
    return () => { isCurrent = false; };
  }, [userId, projectsReloadKey]);

  useEffect(() => {
    let isCurrent = true;
    async function loadCourses() {
      setCoursesLoading(true);
      setCoursesError("");
      try {
        if (!supabase) throw new Error("La connexion à Supabase n’est pas configurée.");
        const { data, error } = await supabase
          .from("user_courses")
          .select(courseColumns)
          .order("created_at", { ascending: false });
        if (error) throw error;
        if (isCurrent) setGeneralCourses((data ?? []).map((row) => mapCourse(row as CourseRow)));
      } catch (error) {
        if (isCurrent) {
          setCoursesError(getTableSetupMessage(error, "des cours personnels", "user_courses.sql"));
        }
      } finally {
        if (isCurrent) setCoursesLoading(false);
      }
    }
    void loadCourses();
    return () => { isCurrent = false; };
  }, [userId, coursesReloadKey]);

  useEffect(() => {
    let isCurrent = true;
    async function loadProjectCourses() {
      if (!supabase) return;
      const { data, error } = await supabase.from("project_course_links").select("project_id, course_id");
      if (!isCurrent) return;
      if (error) {
        showToast(getTableSetupMessage(error, "des associations cours-projets", "project_courses.sql"));
        return;
      }
      const links: Record<string, string[]> = {};
      for (const row of data ?? []) {
        const link = row as { project_id: string; course_id: string };
        (links[link.project_id] ??= []).push(link.course_id);
      }
      setCourseContextByProject(links);
    }
    void loadProjectCourses();
    return () => { isCurrent = false; };
  }, [userId]);

  const activeProject = projects.find((project) => project.id === activeProjectId) ?? null;
  const visibleProjects = useMemo(() => projects.filter((project) =>
    `${project.name} ${project.type} ${project.status}`.toLowerCase().includes(search.toLowerCase()),
  ), [projects, search]);
  const visibleFiles = activeProject?.files.filter((file) =>
    `${file.name} ${file.meta} ${file.state}`.toLowerCase().includes(fileSearch.toLowerCase()),
  ) ?? [];
  const visibleGeneralCourses = generalCourses.filter((course) =>
    `${course.title} ${course.course} ${course.subject} ${course.studyYear}`.toLowerCase().includes(courseSearch.toLowerCase())
      && (courseSubjectFilter === "all" || course.subject === courseSubjectFilter)
      && (courseYearFilter === "all" || course.studyYear === courseYearFilter),
  );
  const visibleProjectCourses = useMemo(() => generalCourses.filter((course) =>
    `${course.title} ${course.course} ${course.subject} ${course.studyYear}`.toLowerCase().includes(projectCourseSearch.toLowerCase()),
  ), [generalCourses, projectCourseSearch]);

  function showToast(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 2600);
  }

  function openProject(projectId: string) {
    setActiveProjectId(projectId);
    setShowCourseLibrary(false);
    setReviewingCourseId(null);
    setSection("chat");
    const project = projects.find((item) => item.id === projectId);
    setChat(chatByProject[projectId] ?? [{
      id: Date.now(),
      role: "assistant",
      text: `Bonjour${greetingName ? ` ${greetingName}` : ""} ! Cet espace est dédié à « ${project?.name ?? "ton projet"} ». Ajoute tes documents ou pose une question pour commencer.`,
      time: "—",
    }]);
    setMobileNavOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function openProjects() {
    setActiveProjectId(null);
    setShowCourseLibrary(false);
    setReviewingCourseId(null);
  }

  function openCourseLibrary() {
    setActiveProjectId(null);
    setShowCourseLibrary(true);
    setReviewingCourseId(null);
  }

  async function createProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleanedName = newName.trim();
    if (!cleanedName) return;
    if (!supabase) {
      showToast("La connexion à Supabase n’est pas disponible.");
      return;
    }
    setProjectSaving(true);
    try {
      const selectedCourseIds = newProjectCourseIds.filter((id) => generalCourses.some((course) => course.id === id));
      const { data, error } = await supabase.from("projects").insert({
        name: cleanedName,
        project_type: newType,
        summary: newSummary.trim() || "Ajoute un peu de contexte pour commencer à organiser ton travail et tes références.",
      }).select("id, name, project_type, status, updated_at, progress, location, term, summary").single();
      if (error) throw error;
      if (selectedCourseIds.length) {
        const { error: linksError } = await supabase.from("project_course_links").insert(
          selectedCourseIds.map((courseId) => ({ project_id: data.id, course_id: courseId })),
        );
        if (linksError) {
          const { error: rollbackError } = await supabase.from("projects").delete().eq("id", data.id);
          if (rollbackError) throw new Error(`${linksError.message} Le projet a été créé, mais son nettoyage a échoué : ${rollbackError.message}`);
          throw linksError;
        }
      }
      const project = mapProject(data as ProjectRow);
      setProjects((items) => [project, ...items]);
      setCourseContextByProject((items) => ({ ...items, [project.id]: selectedCourseIds }));
      const welcome: ChatItem[] = [{ id: Date.now(), role: "assistant", text: `Bienvenue dans « ${project.name} ». Les informations du projet sont enregistrées dans ton compte.`, time: "—" }];
      setChatByProject((items) => ({ ...items, [project.id]: welcome }));
      setChat(welcome);
      setNewName("");
      setNewSummary("");
      setNewProjectCourseIds([]);
      setProjectCourseSearch("");
      setShowCreate(false);
      setActiveProjectId(project.id);
      setSection("chat");
      showToast("Projet enregistré.");
    } catch (error) {
      const message = getErrorMessage(error);
      showToast(`Projet non enregistré : ${message}`);
    } finally {
      setProjectSaving(false);
    }
  }

  function addQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = question.trim();
    if (!text) return;
    const time = new Intl.DateTimeFormat("fr-FR", { hour: "2-digit", minute: "2-digit" }).format(new Date());
    const selectedCourseIds = activeProjectId ? courseContextByProject[activeProjectId] ?? [] : [];
    const studentMessage: ChatItem = { id: Date.now(), role: "student", text, time };
    const demoReply: ChatItem = {
      id: Date.now() + 1,
      role: "assistant",
      text: `Réponse de démonstration : ${selectedCourseIds.length ? "les cours généraux sélectionnés seraient ajoutés au contexte du projet." : "aucun cours général n’est ajouté au contexte de ce projet."} Aucune réponse IA n’est générée pour le moment.`,
      time,
    };
    if (!activeProjectId) return;
    const updatedChat = [...chat, studentMessage, demoReply];
    setChat(updatedChat);
    setChatByProject((items) => ({ ...items, [activeProjectId]: updatedChat }));
    setQuestion("");
    window.setTimeout(() => document.getElementById(`message-${demoReply.id}`)?.scrollIntoView({ behavior: "smooth", block: "center" }), 30);
  }

  function addFiles(files: FileList | null) {
    if (!files?.length || !activeProject) return;
    const additions = Array.from(files).map((file, index) => ({
      id: `local-${Date.now()}-${index}`,
      name: file.name,
      meta: `Fichier local · ${(file.size / (1024 * 1024)).toFixed(1)} Mo`,
      state: "Sélectionné · non envoyé",
      icon: file.type.startsWith("image/") ? "image" as const : "pdf" as const,
    }));
    setProjects((items) => items.map((project) => project.id === activeProject.id
      ? { ...project, files: [...additions, ...project.files] }
      : project));
    showToast("Fichier ajouté à la maquette uniquement — aucun envoi effectué");
  }

  async function runCourseExtraction(id: string) {
    if (extractionRequests.current.has(id)) return;
    extractionRequests.current.add(id);
    setExtractingCourseIds((ids) => [...ids, id]);
    setGeneralCourses((items) => items.map((course) => course.id === id
      ? { ...course, status: "Extraction en cours…", extractionError: null } : course));
    try {
      const result = await extractCourse(id);
      setGeneralCourses((items) => items.map((course) => course.id === id
        ? { ...course, status: extractionLabels[result.status], extractionStatus: result.status, extractionError: result.error } : course));
    } catch (error) {
      setGeneralCourses((items) => items.map((course) => course.id === id
        ? { ...course, status: "Extraction à relancer", extractionStatus: "failed", extractionError: getErrorMessage(error) } : course));
    } finally {
      extractionRequests.current.delete(id);
      setExtractingCourseIds((ids) => ids.filter((courseId) => courseId !== id));
    }
  }

  async function addGeneralCourseFiles(files: FileList | null) {
    if (!files?.length) return;
    if (!supabase) {
      showToast("La connexion à Supabase n’est pas disponible.");
      return;
    }
    const subject = newCourseSubject.trim() || "À classer";
    let uploaded = 0;
    let failedUploads = 0;
    setCourseSaving(true);
    try {
      for (const file of Array.from(files)) {
        try {
          const course = await uploadCourse(file, userId, subject, newCourseYear);
          uploaded += 1;
          setGeneralCourses((items) => [course, ...items]);
          await runCourseExtraction(course.id);
        } catch {
          failedUploads += 1;
        }
      }
      showToast(failedUploads ? `${uploaded} cours ajouté(s), ${failedUploads} échec(s) d’envoi.` : `${uploaded} cours ajouté(s).`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erreur inconnue";
      showToast(`Envoi interrompu : ${message}`);
    } finally {
      setCourseSaving(false);
    }
  }

  async function updateGeneralCourseClassification(id: string, subject: string, studyYear: string) {
    const cleanSubject = subject.trim() || "À classer";
    setGeneralCourses((items) => items.map((course) => course.id === id
      ? { ...course, course: cleanSubject, subject: cleanSubject, studyYear }
      : course));
    if (!supabase) return;
    const { error } = await supabase.from("user_courses").update({
      course: cleanSubject,
      subject: cleanSubject,
      study_year: studyYear,
    }).eq("id", id);
    if (error) {
      showToast(`Classement non enregistré : ${error.message}`);
      setCoursesReloadKey((key) => key + 1);
    }
  }

  async function downloadGeneralCourse(id: string) {
    const course = generalCourses.find((item) => item.id === id);
    if (!course || !supabase) return;
    const { data, error } = await supabase.storage.from("user-courses").download(course.storagePath);
    if (error) {
      showToast(`Téléchargement impossible : ${error.message}`);
      return;
    }
    const url = URL.createObjectURL(data);
    const link = document.createElement("a");
    link.href = url;
    link.download = course.title;
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  async function deleteGeneralCourse(id: string) {
    const course = generalCourses.find((item) => item.id === id);
    if (!course || !supabase || !window.confirm(`Supprimer définitivement « ${course.title} » ?`)) return;
    const { error: storageError } = await supabase.storage.from("user-courses").remove([course.storagePath]);
    if (storageError) {
      showToast(`Fichier non supprimé : ${storageError.message}`);
      return;
    }
    const { error } = await supabase.from("user_courses").delete().eq("id", id);
    if (error) {
      showToast(`Fiche non supprimée : ${error.message}`);
      return;
    }
    setGeneralCourses((items) => items.filter((item) => item.id !== id));
    if (reviewingCourseId === id) setReviewingCourseId(null);
    showToast("Cours supprimé.");
  }

  async function toggleCourseContext(projectId: string, courseId: string) {
    const current = courseContextByProject[projectId] ?? [];
    const wasSelected = current.includes(courseId);
    const next = wasSelected ? current.filter((id) => id !== courseId) : [...current, courseId];
    setCourseContextByProject((items) => ({ ...items, [projectId]: next }));
    if (!supabase) return;
    const { error } = wasSelected
      ? await supabase.from("project_course_links").delete().eq("project_id", projectId).eq("course_id", courseId)
      : await supabase.from("project_course_links").insert({ project_id: projectId, course_id: courseId });
    if (error) {
      setCourseContextByProject((items) => ({ ...items, [projectId]: current }));
      showToast(`Association non enregistrée : ${getTableSetupMessage(error, "des associations cours-projets", "project_courses.sql")}`);
    }
  }

  function submitExercise(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!exerciseAnswer.trim()) {
      showToast("Écris quelques lignes avant de demander une correction");
      return;
    }
    setExerciseSubmitted(true);
  }

  function selectSection(next: Section) {
    setSection(next);
    setMobileNavOpen(false);
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand-lockup" type="button" onClick={openProjects} aria-label="Retour à mes projets">
          <span className="brand-mark"><GraduationCap size={19} strokeWidth={1.8} /></span>
          <span className="brand-word">archi<span>prof</span><small>ATELIER D’APPRENTISSAGE</small></span>
        </button>
        <div className="topbar-right">
          <span className="demo-pill"><span /> MODE DÉMONSTRATION</span>
          <button className="help-button" type="button" onClick={() => showToast("Centre d’aide : bientôt disponible")} aria-label="Aide"><CircleHelp size={18} /></button>
          <button className="profile-chip authenticated-profile" type="button" onClick={onSignOut} aria-label={`Se déconnecter de ${displayName}`} title={userEmail}>
            <span className="profile-avatar">{displayName.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase()}</span><span className="profile-name">{displayName}</span><LogOut size={15} />
          </button>
          {activeProject && <button className="mobile-menu-button" type="button" onClick={() => setMobileNavOpen((value) => !value)} aria-label="Ouvrir le menu"><Menu size={20} /></button>}
        </div>
      </header>

      <main className="main-frame">
        {!activeProject ? (
          showCourseLibrary ? (
            <GeneralCoursesView
              courses={visibleGeneralCourses}
              allCourses={generalCourses}
              loading={coursesLoading}
              error={coursesError}
              saving={courseSaving}
              search={courseSearch}
              subjectFilter={courseSubjectFilter}
              yearFilter={courseYearFilter}
              newSubject={newCourseSubject}
              newYear={newCourseYear}
              reviewingCourse={generalCourses.find((course) => course.id === reviewingCourseId) ?? null}
              onSearch={setCourseSearch}
              onSubjectFilter={setCourseSubjectFilter}
              onYearFilter={setCourseYearFilter}
              onNewSubject={setNewCourseSubject}
              onNewYear={setNewCourseYear}
              onFiles={addGeneralCourseFiles}
              onSaveClassification={updateGeneralCourseClassification}
              onDownload={downloadGeneralCourse}
              onDelete={deleteGeneralCourse}
              onReview={setReviewingCourseId}
              onBack={openProjects}
              onExitReview={() => setReviewingCourseId(null)}
              onToast={showToast}
              onRetry={() => setCoursesReloadKey((key) => key + 1)}
              onExtract={runCourseExtraction}
              extractingCourseIds={extractingCourseIds}
            />
          ) : (
            <ProjectsHome
              projects={visibleProjects}
              greetingName={greetingName}
              loading={projectsLoading}
              error={projectsError}
              search={search}
              onSearch={setSearch}
              onOpen={openProject}
              onCreate={() => setShowCreate(true)}
              onOpenCourses={openCourseLibrary}
              onRetry={() => setProjectsReloadKey((key) => key + 1)}
            />
          )
        ) : (
          <div className="workspace-layout">
            <aside className={`workspace-sidebar ${mobileNavOpen ? "is-open" : ""}`}>
              <button className="back-projects" type="button" onClick={openProjects}>
                <ArrowLeft size={15} /> <span>Mes projets</span>
              </button>
              <div className="sidebar-project-switcher">
                <span className="switcher-caption">PROJET ACTIF</span>
                <select value={activeProject.id} onChange={(event) => openProject(event.target.value)} aria-label="Changer de projet">
                  {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
                </select>
                <ChevronDown className="switcher-chevron" size={15} />
              </div>
              <div className="sidebar-label">ESPACE DE TRAVAIL</div>
              <nav className="workspace-nav" aria-label="Sections du projet">
                <NavItem active={section === "chat"} icon={<MessageSquareText size={18} />} label="Assistant" onClick={() => selectSection("chat")} />
                <NavItem active={section === "documents"} icon={<LibraryBig size={18} />} label="Documents" count={activeProject.files.length} onClick={() => selectSection("documents")} />
                <NavItem active={section === "exercises"} icon={<BookOpen size={18} />} label="Exercices" onClick={() => selectSection("exercises")} />
                <NavItem active={section === "notes"} icon={<FileText size={18} />} label="Notes de projet" onClick={() => selectSection("notes")} />
              </nav>
              <div className="sidebar-bottom">
                <div className="side-tip"><Sparkles size={16} /><span>Chaque projet garde son propre contexte et ses documents.</span></div>
                <button className="sidebar-settings" type="button" onClick={() => showToast("Paramètres du projet · bientôt disponibles")}><Settings2 size={17} /> Paramètres du projet</button>
              </div>
            </aside>

            <section className="workspace-content">
              <div className="workspace-heading">
                <div className="breadcrumbs"><button type="button" onClick={openProjects}>Mes projets</button><ChevronRight size={14} /><span>{activeProject.name}</span></div>
                <div className="project-heading-row">
                  <div>
                    <div className="project-kicker"><span className={`status-dot ${statusClass[activeProject.status]}`} />{activeProject.status}<span className="heading-separator">·</span>{activeProject.type}</div>
                    <h1>{activeProject.name}</h1>
                    <p>{activeProject.term} <span>·</span> {activeProject.location}</p>
                  </div>
                  <div className="heading-actions">
                    <button className="icon-button" type="button" onClick={() => showToast("Options du projet · bientôt disponibles")} aria-label="Plus d’options"><MoreHorizontal size={20} /></button>
                  </div>
                </div>
              </div>

              {section === "chat" && <ChatView project={activeProject} chat={chat} question={question} generalCourses={generalCourses} selectedCourseIds={courseContextByProject[activeProject.id] ?? []} onToggleCourse={(courseId) => toggleCourseContext(activeProject.id, courseId)} onQuestion={setQuestion} onSubmit={addQuestion} onNavigate={selectSection} showAllHistory={showAllHistory} onShowHistory={() => setShowAllHistory((value) => !value)} />}
              {section === "documents" && <DocumentsView project={activeProject} files={visibleFiles} search={fileSearch} onSearch={setFileSearch} onFiles={addFiles} onConnectDrive={() => showToast("Google Drive n’est pas connecté dans ce prototype")} />}
              {section === "exercises" && <ExercisesView answer={exerciseAnswer} submitted={exerciseSubmitted} onAnswer={setExerciseAnswer} onSubmit={submitExercise} />}
              {section === "notes" && <NotesView project={activeProject} onToast={showToast} />}
            </section>
          </div>
        )}
      </main>

      <footer className="demo-footer"><span className="demo-footer-dot" /> Projets enregistrés dans ton compte <span>·</span> Documents, notes et conversations encore en démonstration</footer>

      {showCreate && <CreateProjectDialog name={newName} type={newType} description={newSummary} courses={visibleProjectCourses} coursesLoading={coursesLoading} coursesError={coursesError} courseSearch={projectCourseSearch} selectedCourseIds={newProjectCourseIds} saving={projectSaving} onName={setNewName} onType={setNewType} onDescription={setNewSummary} onCourseSearch={setProjectCourseSearch} onToggleCourse={(courseId) => setNewProjectCourseIds((current) => current.includes(courseId) ? current.filter((id) => id !== courseId) : [...current, courseId])} onClose={() => setShowCreate(false)} onSubmit={createProject} />}
      {toast && <div className="toast-message" role="status"><Check size={16} />{toast}</div>}
    </div>
  );
}

function ProjectsHome({
  projects,
  greetingName,
  loading,
  error,
  search,
  onSearch,
  onOpen,
  onCreate,
  onOpenCourses,
  onRetry,
}: {
  projects: Project[];
  greetingName: string | null;
  loading: boolean;
  error: string;
  search: string;
  onSearch: (value: string) => void;
  onOpen: (id: string) => void;
  onCreate: () => void;
  onOpenCourses: () => void;
  onRetry: () => void;
}) {
  return (
    <section className="projects-home">
      <div className="home-intro">
        <div className="eyebrow"><span className="eyebrow-line" /> TON ESPACE DE TRAVAIL</div>
        <div className="home-heading-row">
          <div><h1>{greetingName ? <>Bonjour {greetingName}</> : "Mon espace de travail"}<span className="hello-period">.</span></h1><p>Reprends là où tu en étais, ou ouvre un nouvel atelier.</p></div>
          <div className="home-actions"><button className="primary-button create-project-button" type="button" onClick={onCreate}><Plus size={18} /> Nouveau projet</button><button className="secondary-button" type="button" onClick={onOpenCourses}><BookOpen size={17} /> Cours généraux</button></div>
        </div>
        <div className="home-meta-row"><span><FolderKanban size={16} /> {loading ? "…" : projects.length} projets</span><span className="meta-divider" /><span><Clock3 size={16} /> Tes espaces restent séparés</span></div>
      </div>

      <section className="projects-section" aria-labelledby="projects-title">
        <div className="section-heading-row">
          <div><h2 id="projects-title">Mes projets <span className="muted-count">{loading ? "…" : projects.length}</span></h2><p>Tes projets sont enregistrés; les documents et échanges seront connectés ensuite.</p></div>
          <label className="search-box project-search"><Search size={17} /><input value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Rechercher un projet" aria-label="Rechercher un projet" />{search && <button type="button" onClick={() => onSearch("")} aria-label="Effacer la recherche"><X size={15} /></button>}</label>
        </div>
        {loading ? (
          <div className="empty-projects" role="status"><h3>Chargement de tes projets…</h3></div>
        ) : error ? (
          <div className="empty-projects" role="alert"><h3>Les projets sont indisponibles</h3><p>{error}</p><button type="button" className="text-button" onClick={onRetry}>Réessayer <ArrowRight size={15} /></button></div>
        ) : projects.length ? (
          <div className="project-grid">
            {projects.map((project, index) => <ProjectCard key={project.id} project={project} variant={index % 3 === 0 ? "one" : index % 3 === 1 ? "two" : "three"} onOpen={() => onOpen(project.id)} />)}
            <button className="new-project-card" type="button" onClick={onCreate}><span className="new-project-icon"><Plus size={21} /></span><b>Commencer un nouveau projet</b><span>Un nouvel espace, prêt à prendre forme.</span><span className="new-project-arrow"><ArrowRight size={16} /></span></button>
          </div>
        ) : (
          <div className="empty-projects"><span className="empty-icon"><FolderKanban size={22} /></span><h3>{search ? "Aucun projet trouvé" : "Ton espace commence ici"}</h3><p>{search ? "Essaie un autre nom ou efface ta recherche." : "Clique sur « Nouveau projet », donne-lui un nom et un type. Tu pourras ensuite y organiser ton travail d’architecture; les documents, notes et conversations seront raccordés dans une prochaine étape."}</p><button type="button" className="text-button" onClick={onCreate}>{search ? "Créer un projet" : "Créer mon premier projet"} <ArrowRight size={15} /></button></div>
        )}
      </section>
      <div className="home-bottom-note"><span className="note-sparkle"><Sparkles size={17} /></span><p><b>Un espace par idée.</b> Les documents et échanges seront rattachés à chaque projet dans une prochaine étape.</p><span className="note-illustration" aria-hidden="true">⌁</span></div>
    </section>
  );
}

function GeneralCoursesView({
  courses,
  allCourses,
  search,
  subjectFilter,
  yearFilter,
  newSubject,
  newYear,
  reviewingCourse,
  onSearch,
  onSubjectFilter,
  onYearFilter,
  onNewSubject,
  onNewYear,
  onFiles,
  onSaveClassification,
  onReview,
  onBack,
  onExitReview,
  onToast,
  onRetry,
  loading,
  error,
  saving,
  onDownload,
  onDelete,
  onExtract,
  extractingCourseIds,
}: {
  courses: CourseDocument[];
  allCourses: CourseDocument[];
  loading: boolean;
  error: string;
  saving: boolean;
  search: string;
  subjectFilter: string;
  yearFilter: string;
  newSubject: string;
  newYear: string;
  reviewingCourse: CourseDocument | null;
  onSearch: (value: string) => void;
  onSubjectFilter: (value: string) => void;
  onYearFilter: (value: string) => void;
  onNewSubject: (value: string) => void;
  onNewYear: (value: string) => void;
  onFiles: (files: FileList | null) => void | Promise<void>;
  onSaveClassification: (id: string, subject: string, studyYear: string) => void | Promise<void>;
  onDownload: (id: string) => void | Promise<void>;
  onDelete: (id: string) => void | Promise<void>;
  onReview: (id: string) => void;
  onBack: () => void;
  onExitReview: () => void;
  onToast: (message: string) => void;
  onRetry: () => void;
  onExtract: (id: string) => void | Promise<void>;
  extractingCourseIds: string[];
}) {
  const courseFileInput = useRef<HTMLInputElement>(null);
  const subjectOptions = Array.from(new Set([...allCourses.map((course) => course.subject), "À classer"])).sort((left, right) => left.localeCompare(right, "fr"));

  return (
    <section className="projects-home general-courses-home">
      <button className="back-projects" type="button" onClick={onBack}><ArrowLeft size={15} /> <span>Mes projets</span></button>
      <div className="home-intro general-courses-intro">
        <div className="eyebrow"><span className="eyebrow-line" /> ESPACE PERSONNEL</div>
        <div className="home-heading-row">
          <div><h1>Cours généraux<span className="hello-period">.</span></h1><p>Révise tes cours ici, indépendamment de tes projets.</p></div>
        </div>
        <div className="home-meta-row"><span><BookOpen size={16} /> {loading ? "…" : allCourses.length} cours</span><span className="meta-divider" /><span><FolderKanban size={16} /> Bibliothèque privée à ton compte</span></div>
      </div>
      <div className="course-add-toolbar">
        <label className="course-field"><span>Matière du cours ajouté</span><input list="course-subject-suggestions" value={newSubject} onChange={(event) => onNewSubject(event.target.value)} placeholder="Choisir ou saisir une matière" /><datalist id="course-subject-suggestions">{subjectOptions.map((subject) => <option key={subject} value={subject} />)}</datalist></label>
        <label className="course-field"><span>Année d’étude</span><select value={newYear} onChange={(event) => onNewYear(event.target.value)}>{studyYearOptions.map((year) => <option key={year} value={year}>{year}</option>)}</select></label>
        <label className="primary-button upload-button"><Upload size={17} /> {saving ? "Envoi…" : "Ajouter des cours"}<input ref={courseFileInput} type="file" multiple accept=".pdf,.doc,.docx,.ppt,.pptx,.epub,.png,.jpg,.jpeg,.webp" disabled={saving} onChange={(event) => { void onFiles(event.target.files); event.currentTarget.value = ""; }} /></label>
      </div>
      <div className="general-courses-content">
        {error ? <div className="file-notice" role="alert"><span className="notice-icon"><CircleHelp size={16} /></span><span><b>Bibliothèque indisponible</b> · {error} <button className="text-button" type="button" onClick={onRetry}>Réessayer</button></span></div> : <div className="file-notice"><span className="notice-icon"><CircleHelp size={16} /></span><span><b>Fichiers privés</b> · Les supports sont stockés dans ton espace; leur indexation et leur analyse viendront ensuite.</span></div>}
        {reviewingCourse ? (
          <section className="course-review-panel">
            <button className="text-button" type="button" onClick={onExitReview}><ArrowLeft size={15} /> Tous les cours</button>
            <div className="feature-page-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> {reviewingCourse.course.toUpperCase()}</div><h2>{reviewingCourse.title}</h2><p>Révision indépendante de tes projets · {reviewingCourse.status}</p></div></div>
            <CourseExtractionStatus course={reviewingCourse} busy={extractingCourseIds.includes(reviewingCourse.id)} onExtract={onExtract} />
            <div className="course-review-actions"><button className="secondary-button" type="button" onClick={() => onToast("La synthèse sera disponible après connexion de l’API documentaire")}>Générer une synthèse</button><button className="primary-button" type="button" onClick={() => onToast("Le quiz sera disponible après connexion de l’API pédagogique")}>Lancer un quiz</button></div>
          </section>
        ) : (
          <>
            <div className="section-heading-row course-library-heading"><div><h2>Ma bibliothèque <span className="muted-count">{courses.length}</span></h2><p>Ces supports ne sont rattachés à aucun projet.</p></div></div>
            <div className="course-filter-row">
              <label className="search-box course-search"><Search size={17} /><input value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Rechercher un cours" aria-label="Rechercher un cours" />{search && <button type="button" onClick={() => onSearch("")} aria-label="Effacer la recherche"><X size={15} /></button>}</label>
              <label className="course-filter"><span>Matière</span><select value={subjectFilter} onChange={(event) => onSubjectFilter(event.target.value)}><option value="all">Toutes les matières</option>{subjectOptions.map((subject) => <option key={subject} value={subject}>{subject}</option>)}</select></label>
              <label className="course-filter"><span>Année d’étude</span><select value={yearFilter} onChange={(event) => onYearFilter(event.target.value)}><option value="all">Toutes les années</option>{studyYearOptions.map((year) => <option key={year} value={year}>{year}</option>)}</select></label>
            </div>
            <div className="course-library-list">{loading ? <div className="empty-documents" role="status"><b>Chargement de ta bibliothèque…</b></div> : error ? <div className="empty-documents" role="alert"><b>Les cours sont indisponibles.</b><button className="text-button" type="button" onClick={onRetry}>Réessayer <ArrowRight size={15} /></button></div> : courses.length ? courses.map((course) => <article className="course-library-row" key={course.id}><span className="document-icon document-plan"><BookOpen size={18} /></span><span className="course-library-info"><b>{course.title}</b><small>{course.subject} · {course.studyYear} · {course.meta}</small></span><label className="course-row-field course-row-subject"><span className="visually-hidden">Matière</span><input list="course-subject-suggestions" aria-label={`Matière de ${course.title}`} defaultValue={course.subject} onBlur={(event) => { const subject = event.currentTarget.value.trim(); if (subject && subject !== course.subject) void onSaveClassification(course.id, subject, course.studyYear); }} /></label><label className="course-row-field course-row-year"><span className="visually-hidden">Année d’étude</span><select aria-label={`Année d’étude de ${course.title}`} value={course.studyYear} onChange={(event) => { void onSaveClassification(course.id, course.subject, event.target.value); }}>{studyYearOptions.map((year) => <option key={year} value={year}>{year}</option>)}</select></label><span className="file-state"><i />{course.status}</span><button className="icon-button" type="button" onClick={() => { void onDownload(course.id); }} aria-label={`Télécharger ${course.title}`} title="Télécharger"><Download size={16} /></button><button className="icon-button" type="button" onClick={() => { void onDelete(course.id); }} aria-label={`Supprimer ${course.title}`} title="Supprimer"><Trash2 size={16} /></button><button className="secondary-button" type="button" onClick={() => onReview(course.id)}>Réviser <ArrowRight size={15} /></button></article>) : search ? <div className="empty-documents"><span className="empty-icon"><Search size={21} /></span><b>Aucun cours trouvé</b><p>Essaie avec un autre terme ou efface ta recherche.</p></div> : <div className="empty-documents first-course-empty"><span className="empty-icon"><BookOpen size={21} /></span><b>Ta bibliothèque commence ici</b><p>Ajoute un support PDF, Word ou une image de cours. Il sera stocké dans ton espace privé, classable par matière et année, puis téléchargeable. L’analyse et les fiches de révision viendront dans une prochaine étape. Taille maximale : 50 Mo par fichier.</p><button className="primary-button" type="button" disabled={saving} onClick={() => courseFileInput.current?.click()}><Upload size={16} /> Ajouter mon premier cours</button></div>}</div>
          </>
        )}
      </div>
    </section>
  );
}

function ProjectCard({ project, variant, onOpen }: { project: Project; variant: "one" | "two" | "three"; onOpen: () => void }) {
  return (
    <article className="project-card">
      <button className="project-card-open" type="button" onClick={onOpen} aria-label={`Ouvrir le projet ${project.name}`}>
        <ProjectArtwork variant={variant} />
        <div className="project-card-body">
          <div className="project-card-kicker"><span className={`status-dot ${statusClass[project.status]}`} />{project.status}<span>·</span>{project.type}</div>
          <div className="project-card-title-row"><h3>{project.name}</h3><span className="card-arrow"><ArrowUpRightIcon /></span></div>
          <p className="project-card-summary">{project.summary}</p>
          <div className="project-card-progress"><div className="progress-label"><span>Avancement</span><b>{project.progress}%</b></div><div className="progress-track"><span style={{ width: `${project.progress}%` }} /></div></div>
          <div className="project-card-footer"><span><Clock3 size={14} />{project.updated}</span><span>{project.files.length} documents</span></div>
        </div>
      </button>
    </article>
  );
}

function ArrowUpRightIcon() {
  return <ArrowDownLeft size={16} className="arrow-up-right" />;
}

function NavItem({ active, icon, label, count, onClick }: { active: boolean; icon: ReactNode; label: string; count?: number; onClick: () => void }) {
  return <button className={`workspace-nav-item ${active ? "active" : ""}`} type="button" onClick={onClick}>{icon}<span>{label}</span>{count !== undefined && <small>{count}</small>}</button>;
}

function ChatView({
  project,
  chat,
  question,
  generalCourses,
  selectedCourseIds,
  onToggleCourse,
  onQuestion,
  onSubmit,
  onNavigate,
  showAllHistory,
  onShowHistory,
}: {
  project: Project;
  chat: ChatItem[];
  question: string;
  generalCourses: CourseDocument[];
  selectedCourseIds: string[];
  onToggleCourse: (courseId: string) => void;
  onQuestion: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onNavigate: (section: Section) => void;
  showAllHistory: boolean;
  onShowHistory: () => void;
}) {
  const recentQuestions = ["Comment réduire la portée en zone C ?", "Quelle ambiance pour le séjour ?", "Faire le point sur le concept", "Quelles références pour une façade active ?"];
  const [coursePickerOpen, setCoursePickerOpen] = useState(false);
  const [courseSearch, setCourseSearch] = useState("");
  const selectedCourses = generalCourses.filter((course) => selectedCourseIds.includes(course.id));
  const matchingCourses = generalCourses.filter((course) =>
    `${course.title} ${course.course} ${course.subject} ${course.studyYear}`.toLowerCase().includes(courseSearch.toLowerCase()),
  );
  const visibleMatchingCourses = matchingCourses.slice(0, 40);
  return (
    <div className="chat-layout">
      <section className="chat-panel" aria-label="Conversation avec ArchiProf">
        <div className="chat-session-header"><div className="assistant-identity"><div className="assistant-avatar"><img src={assistantPortrait} alt="" /></div><div><b>ArchiProf</b><span>Assistant pédagogique · {project.name}</span></div><span className="online-status"><i /> Exemple</span></div><button className="session-menu" type="button" aria-label="Options de la conversation"><MoreHorizontal size={19} /></button></div>
        <div className="chat-messages">
          <div className="date-divider"><span>Aujourd’hui</span></div>
          {chat.map((item) => item.role === "student" ? (
            <div className="message-row student-message" id={`message-${item.id}`} key={item.id}><div className="student-bubble">{item.text}</div><span className="message-time">{item.time}</span></div>
          ) : (
            <div className="assistant-message-block" id={`message-${item.id}`} key={item.id}>
              <div className="message-assistant-avatar"><img src={assistantPortrait} alt="" /></div>
              <div className="assistant-message-content"><div className="assistant-message-meta"><b>ArchiProf</b><time>{item.time}</time></div><p className="assistant-intro">{item.text}</p>
                {item.id === 3 && <StructuredAnswer onNavigate={onNavigate} />}
              </div>
            </div>
          ))}
          <div className="prompt-suggestions"><span>POUR CONTINUER</span><div>{suggestedQuestions.map((suggestion) => <button key={suggestion} type="button" onClick={() => onQuestion(suggestion)}>{suggestion}<ArrowRight size={13} /></button>)}</div></div>
        </div>
        <form className="chat-composer" onSubmit={onSubmit}>
          <textarea value={question} onChange={(event) => onQuestion(event.target.value)} placeholder="Pose une question sur ton projet ou tes cours…" rows={2} aria-label="Écrire une question" onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} />
          <div className="composer-footer"><span><Sparkles size={14} /> Réponse simulée · données de démonstration</span><button className="send-button" type="submit" disabled={!question.trim()} aria-label="Envoyer la question"><Send size={16} /></button></div>
        </form>
        <p className="chat-disclaimer">ArchiProf accompagne ta réflexion, mais ne remplace pas les retours de ton enseignant.</p>
      </section>
      <aside className="chat-context-panel">
        <section className="context-card project-context-card"><div className="context-card-heading"><span className="context-icon context-icon-sage"><FolderKanban size={16} /></span><span>CONTEXTE DU PROJET</span><button type="button" aria-label="Plus d’options"><MoreHorizontal size={17} /></button></div><h3>{project.name}</h3><p>{project.summary}</p><div className="context-tags"><span>{project.type}</span><span>{project.location}</span></div><button className="context-link" type="button" onClick={() => onNavigate("notes")}>Voir les notes du projet <ArrowRight size={14} /></button></section>
        <section className="context-card general-course-context"><div className="context-card-heading"><span className="context-icon context-icon-blue"><BookOpen size={16} /></span><span>COURS GÉNÉRAUX</span><span className="context-count">{selectedCourseIds.length}</span></div><p className="context-helper">{selectedCourseIds.length ? "Cours associés à ce projet." : "Aucun cours associé à ce projet."}</p>{selectedCourses.length > 0 && <div className="course-context-list">{selectedCourses.map((course) => <div className="course-context-option" key={course.id}><span><b>{course.course}</b><small>{course.title}</small></span><button className="course-context-remove" type="button" aria-label={`Retirer ${course.title} du projet`} onClick={() => onToggleCourse(course.id)}><X size={14} /></button></div>)}</div>}<button className="context-link" type="button" onClick={() => setCoursePickerOpen((open) => !open)}>{coursePickerOpen ? "Fermer la sélection" : "Ajouter ou retirer des cours"}<ArrowRight size={14} /></button>{coursePickerOpen && <div className="course-context-picker"><input type="search" aria-label="Rechercher un cours général" placeholder="Rechercher un cours…" value={courseSearch} onChange={(event) => setCourseSearch(event.target.value)} /><div className="course-context-list">{visibleMatchingCourses.length ? visibleMatchingCourses.map((course) => <label className="course-context-option" key={course.id}><input type="checkbox" checked={selectedCourseIds.includes(course.id)} onChange={() => onToggleCourse(course.id)} /><span><b>{course.course}</b><small>{course.title} · {course.studyYear}</small></span></label>) : <p className="course-context-empty">{generalCourses.length ? "Aucun cours ne correspond à cette recherche." : "Ajoute d’abord des cours dans ta bibliothèque."}</p>}</div>{matchingCourses.length > visibleMatchingCourses.length && <small className="course-context-note">40 résultats affichés. Précise la recherche pour affiner.</small>}</div>}<p className="context-prototype-note">Association enregistrée · analyse documentaire à venir</p></section>
        <section className="context-card sources-card"><div className="context-card-heading"><span className="context-icon context-icon-clay"><LibraryBig size={16} /></span><span>SOURCES DU PROJET</span><button type="button" aria-label="Voir les documents" onClick={() => onNavigate("documents")}><ArrowRight size={16} /></button></div><div className="source-count"><b>{project.files.length}</b><span>documents associés</span></div><div className="source-mini-list">{project.files.slice(0, 3).map((file) => <div className="source-mini" key={file.id}><span className="mini-file-icon"><ProjectIcon kind={file.icon} /></span><span><b>{file.name}</b><small>{file.state}</small></span></div>)}</div><button className="context-link" type="button" onClick={() => onNavigate("documents")}>Ouvrir la bibliothèque <ArrowRight size={14} /></button></section>
        <section className="context-card history-card"><div className="context-card-heading"><span className="context-icon context-icon-blue"><Clock3 size={16} /></span><span>HISTORIQUE RÉCENT</span></div><div className="history-list">{recentQuestions.slice(0, showAllHistory ? 4 : 3).map((item, index) => <button type="button" className="history-item" key={item} onClick={() => document.getElementById(`message-${chat[Math.min(index * 2 + 1, chat.length - 1)]?.id}`)?.scrollIntoView({ behavior: "smooth", block: "center" })}><span className="history-index">0{index + 1}</span><span><b>{item}</b><small>{index === 0 ? "Aujourd’hui · 10:46" : index === 1 ? "Hier · 16:12" : "Mardi · 09:30"}</small></span><ChevronRight size={15} /></button>)}</div><button className="context-link" type="button" onClick={onShowHistory}>{showAllHistory ? "Réduire l’historique" : "Voir l’historique complet"}<ArrowRight size={14} /></button></section>
      </aside>
    </div>
  );
}

function StructuredAnswer({ onNavigate }: { onNavigate: (section: Section) => void }) {
  return (
    <div className="answer-structure">
      <article className="answer-section course-answer"><div className="answer-section-title"><span className="answer-section-mark">01</span><span>Dans tes cours</span><span className="source-tag">COURS</span></div><p>Pour une portée importante, compare plusieurs systèmes porteurs en fonction de l’usage, de la trame et de la hauteur disponible.</p><button className="citation-link" type="button" onClick={() => onNavigate("documents")}><BookOpen size={14} /><span><b>Structures II</b><small>Chapitre 4 · Principes de stabilité · p. 18</small></span><ArrowRight size={14} /></button></article>
      <article className="answer-section general-answer"><div className="answer-section-title"><span className="answer-section-mark">02</span><span>Règle générale</span><span className="source-tag general-tag">GÉNÉRAL</span></div><p>Tu peux étudier une poutre de plus grande portée, une trame intermédiaire ou un changement de matériau. Chaque piste a des conséquences sur l’espace et la mise en œuvre.</p><div className="answer-hint"><Sparkles size={14} /> Pense à comparer aussi l’impact sur les pièces voisines.</div></article>
      <article className="answer-section local-answer"><div className="answer-section-title"><span className="answer-section-mark">03</span><span>Source locale</span><span className="source-tag local-tag">À VÉRIFIER</span></div><p>Aucune source réglementaire locale n’est configurée pour ce projet. Vérifie les règles applicables auprès de ton enseignant ou de la source officielle.</p><button className="small-text-action" type="button" onClick={() => onNavigate("documents")}>Ajouter une source au projet <ArrowRight size={13} /></button></article>
      <div className="answer-followup"><span>Tu veux explorer ces pistes ?</span><button type="button" onClick={() => onNavigate("exercises")}>Comparer les systèmes <ArrowRight size={14} /></button></div>
    </div>
  );
}

function DocumentsView({ project, files, search, onSearch, onFiles, onConnectDrive }: {
  project: Project;
  files: Project["files"];
  search: string;
  onSearch: (value: string) => void;
  onFiles: (files: FileList | null) => void;
  onConnectDrive: () => void;
}) {
  return (
    <section className="feature-page">
      <div className="feature-page-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> ESPACE DOCUMENTAIRE</div><h2>Bibliothèque du projet</h2><p>Retrouve les documents de « {project.name} » et leur état d’indexation.</p></div><label className="primary-button upload-button"><Upload size={17} /> Ajouter des fichiers<input type="file" multiple accept=".pdf,.doc,.docx,.ppt,.pptx,.epub,.png,.jpg,.jpeg,.webp" onChange={(event) => onFiles(event.target.files)} /></label></div>
      <div className="file-notice"><span className="notice-icon"><CircleHelp size={16} /></span><span><b>Prototype front-end</b> · Les fichiers restent sur cet appareil et ne sont pas envoyés ni analysés.</span></div>
      <div className="document-toolbar"><label className="search-box"><Search size={16} /><input value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Rechercher un document" aria-label="Rechercher un document" /></label><button className="secondary-button" type="button" onClick={onConnectDrive}><HardDriveDownload size={16} /> Connecter Google Drive</button></div>
      <div className="document-table"><div className="document-table-header"><span>DOCUMENT</span><span>ÉTAT</span><span>SOURCE</span><span /></div>{files.length ? files.map((file) => <div className="document-row" key={file.id}><div className="document-name"><span className={`document-icon document-${file.icon}`}><ProjectIcon kind={file.icon} /></span><span><b>{file.name}</b><small>{file.meta}</small></span></div><span className={`file-state ${file.state.includes("non envoyé") ? "file-state-pending" : ""}`}><i />{file.state}</span><span className="file-source">{file.id.startsWith("local-") ? "Fichier local" : "Projet"}</span><button className="icon-button" type="button" aria-label={`Options pour ${file.name}`}><MoreHorizontal size={18} /></button></div>) : <div className="empty-documents"><span className="empty-icon"><FileText size={21} /></span><b>Aucun document trouvé</b><p>Ajoute un fichier ou modifie ta recherche.</p></div>}</div>
      <div className="document-footnote"><span><Check size={15} /> {files.length} documents dans cet espace</span><button type="button" onClick={onConnectDrive}>Synchronisation Drive <ArrowRight size={14} /></button></div>
    </section>
  );
}

function ExercisesView({ answer, submitted, onAnswer, onSubmit }: { answer: string; submitted: boolean; onAnswer: (value: string) => void; onSubmit: (event: FormEvent<HTMLFormElement>) => void }) {
  return (
    <section className="feature-page exercise-page">
      <div className="feature-page-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> APPRENTISSAGE ACTIF</div><h2>Exercices &amp; correction</h2><p>Entraîne-toi à argumenter tes choix de conception.</p></div><span className="demo-label"><Sparkles size={14} /> Exemple de parcours</span></div>
      <div className="exercise-layout"><article className="exercise-card"><div className="exercise-card-top"><span className="exercise-number">EXERCICE 01</span><span className="difficulty-pill">Niveau débutant</span></div><h3>Choisir un système porteur</h3><p className="exercise-prompt">Une salle commune de 7 mètres de large doit rester dégagée de poteaux au centre. Cite deux systèmes que tu pourrais étudier et explique brièvement ce que tu comparerais.</p><div className="exercise-objective"><BookOpen size={15} /><span>Objectif : relier portée, structure et usage</span></div><form className="exercise-answer" onSubmit={onSubmit}><label htmlFor="exercise-response">TA RÉPONSE</label><textarea id="exercise-response" rows={5} value={answer} onChange={(event) => { onAnswer(event.target.value); }} placeholder="Décris tes pistes et ton raisonnement…" /><div className="exercise-answer-footer"><span>{answer.length} caractères · réponse non enregistrée</span><button className="primary-button" type="submit">Voir la correction <ArrowRight size={15} /></button></div></form></article><aside className="exercise-aside"><div className="progress-card"><div className="context-card-heading"><span className="context-icon context-icon-sage"><GraduationCap size={16} /></span><span>TA PROGRESSION</span></div><div className="progress-empty"><span>—</span><p>Les exercices terminés apparaîtront ici.</p></div><div className="progress-track"><span style={{ width: "0%" }} /></div><small>0 exercice terminé</small></div><div className="teacher-note"><Sparkles size={16} /><p>La correction t’aide à raisonner. Elle ne remplace pas le retour de ton enseignant.</p></div></aside></div>
      {submitted && <div className="correction-panel" role="status"><div className="correction-heading"><span className="context-icon context-icon-sage"><Check size={16} /></span><div><b>Correction guidée · exemple</b><small>Cette correction n’analyse pas ta réponse.</small></div></div><p>Compare tes pistes selon la portée libre, la hauteur structurelle nécessaire, le matériau, les appuis et l’impact sur l’espace. Tu peux aussi demander à ton enseignant quels critères priment pour l’exercice.</p><div className="answer-hint"><Sparkles size={14} /> Essaie de justifier une piste à partir de l’usage de la salle.</div></div>}
    </section>
  );
}

function NotesView({ project, onToast }: { project: Project; onToast: (message: string) => void }) {
  return (
    <section className="feature-page notes-page"><div className="feature-page-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> CARNET DE PROJET</div><h2>Notes de projet</h2><p>Les idées et décisions à garder près de toi pour « {project.name} ».</p></div><button className="secondary-button" type="button" onClick={() => onToast("Création de note à connecter au stockage")}><Plus size={16} /> Ajouter une note</button></div><div className="notes-board">{project.notes.map((note) => <article className={`note-card note-card-${note.tone}`} key={note.id}><span className="note-card-label">{note.label}</span><p>{note.text}</p><small>{note.created}</small></article>)}<button className="new-note-card" type="button" onClick={() => onToast("Création de note à connecter au stockage")}><Plus size={19} /><span>Ajouter une note</span></button></div><div className="file-notice"><span className="notice-icon"><CircleHelp size={16} /></span><span><b>Notes d’exemple</b> · Chaque projet affiche ses propres notes. Elles ne sont pas encore enregistrées.</span></div></section>
  );
}

function CreateProjectDialog({ name, type, description, courses, coursesLoading, coursesError, courseSearch, selectedCourseIds, saving, onName, onType, onDescription, onCourseSearch, onToggleCourse, onClose, onSubmit }: {
  name: string;
  type: string;
  description: string;
  courses: CourseDocument[];
  coursesLoading: boolean;
  coursesError: string;
  courseSearch: string;
  selectedCourseIds: string[];
  saving: boolean;
  onName: (value: string) => void;
  onType: (value: string) => void;
  onDescription: (value: string) => void;
  onCourseSearch: (value: string) => void;
  onToggleCourse: (courseId: string) => void;
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void | Promise<void>;
}) {
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget && !saving) onClose(); }}>
      <section className="create-modal" role="dialog" aria-modal="true" aria-labelledby="create-title">
        <div className="modal-header"><div><span className="modal-eyebrow">NOUVEL ESPACE DE TRAVAIL</span><h2 id="create-title">Donne forme à une idée.</h2></div><button className="icon-button" type="button" onClick={onClose} aria-label="Fermer" disabled={saving}><X size={19} /></button></div>
        <p className="modal-copy">Le projet sera privé à ton compte. Documents, notes et conversations ne sont pas encore sauvegardés.</p>
        <form onSubmit={onSubmit}>
          <label className="form-field"><span>Nom du projet</span><input autoFocus value={name} onChange={(event) => onName(event.target.value)} placeholder="Ex. Maison de quartier" required maxLength={80} disabled={saving} /></label>
          <label className="form-field"><span>Type de projet</span><select value={type} onChange={(event) => onType(event.target.value)} disabled={saving}><option>Projet d’architecture</option><option>Logement collectif</option><option>Équipement public</option><option>Réhabilitation</option><option>Projet libre</option></select></label>
          <label className="form-field"><span>Description / contexte</span><textarea value={description} onChange={(event) => onDescription(event.target.value)} placeholder="Décris brièvement le sujet, le lieu ou les objectifs du projet…" rows={3} maxLength={1000} disabled={saving} /></label>
          <section className="project-course-picker" aria-labelledby="project-course-title">
            <div className="project-course-heading"><b id="project-course-title">Cours généraux associés</b><span>{selectedCourseIds.length} sélectionné{selectedCourseIds.length > 1 ? "s" : ""}</span></div>
            <label className="form-field"><span className="visually-hidden">Rechercher un cours</span><input type="search" value={courseSearch} onChange={(event) => onCourseSearch(event.target.value)} placeholder="Rechercher par titre ou matière" disabled={saving} /></label>
            <div className="project-course-options">
              {coursesLoading ? <p role="status">Chargement des cours…</p> : coursesError ? <p role="alert">La bibliothèque de cours est indisponible.</p> : courses.length ? courses.map((course) => <label className="project-course-option" key={course.id}><input type="checkbox" checked={selectedCourseIds.includes(course.id)} onChange={() => onToggleCourse(course.id)} disabled={saving} /><span><b>{course.title}</b><small>{course.course} · {course.studyYear}</small></span></label>) : <p>{courseSearch ? "Aucun cours ne correspond à cette recherche." : "Aucun cours général disponible. Tu pourras en ajouter depuis la bibliothèque."}</p>}
            </div>
            <small className="project-course-hint">Facultatif. Seuls les cours sélectionnés seront associés à ce projet.</small>
          </section>
          <div className="modal-notice"><Sparkles size={16} /><span>La description sera conservée comme contexte. Les cours sont associés au projet, mais ne sont pas encore analysés par l’assistant.</span></div>
          <div className="modal-actions"><button className="secondary-button" type="button" onClick={onClose} disabled={saving}>Annuler</button><button className="primary-button" type="submit" disabled={!name.trim() || saving}>{saving ? "Enregistrement…" : "Créer le projet"} <ArrowRight size={15} /></button></div>
        </form>
      </section>
    </div>
  );
}

function App() {
  const [session, setSession] = useState<Session | null | undefined>(undefined);
  const [passwordRecovery, setPasswordRecovery] = useState(false);

  useEffect(() => {
    const client = supabase;
    if (!client) {
      setSession(null);
      return;
    }

    const { data } = client.auth.onAuthStateChange((event, nextSession) => {
      setSession(nextSession);
      if (event === "PASSWORD_RECOVERY") setPasswordRecovery(true);
    });
    void client.auth.getSession().then(({ data: result, error }) => {
      if (error) {
        setSession(null);
        return;
      }
      setSession(result.session);
    });

    return () => data.subscription.unsubscribe();
  }, []);

  if (!supabase) return <AuthScreen />;
  if (session === undefined) return <main className="auth-loading" role="status">Chargement de ton espace…</main>;
  if (!session) return <AuthScreen />;
  if (passwordRecovery) {
    return <AuthScreen initialMode="update-password" onRecoveryComplete={() => setPasswordRecovery(false)} />;
  }

  const firstName = typeof session.user.user_metadata.first_name === "string"
    ? session.user.user_metadata.first_name.trim()
    : "";
  const lastName = typeof session.user.user_metadata.last_name === "string"
    ? session.user.user_metadata.last_name.trim()
    : "";
  const displayName = [firstName, lastName].filter(Boolean).join(" ") || session.user.email || "Compte étudiant";

  async function signOut() {
    if (!supabase) return;
    const { error } = await supabase.auth.signOut();
    if (!error) setSession(null);
  }

  return (
    <WorkspaceApp
      displayName={displayName}
      greetingName={firstName || null}
      userEmail={session.user.email ?? "Compte étudiant"}
      userId={session.user.id}
      onSignOut={signOut}
    />
  );
}

export default App;
