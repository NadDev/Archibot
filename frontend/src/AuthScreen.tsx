import { useState, type FormEvent } from "react";
import {
  ArrowRight,
  Check,
  Eye,
  EyeOff,
  GraduationCap,
  KeyRound,
  LockKeyhole,
  Mail,
  ShieldCheck,
} from "lucide-react";

import { supabase } from "./supabase";

type AuthMode = "sign-in" | "sign-up" | "forgot-password" | "update-password" | "email-sent";

type AuthScreenProps = {
  initialMode?: AuthMode;
  onRecoveryComplete?: () => void;
};

const assistantPortrait = new URL("../../docs/image.png", import.meta.url).href;

function getAuthErrorMessage(error: unknown): string {
  if (!(error instanceof Error)) return "Une erreur est survenue. Réessaie dans un instant.";
  if (error.message.includes("Invalid login credentials")) return "Adresse email ou mot de passe incorrect.";
  if (error.message.includes("Email not confirmed")) return "Confirme ton adresse email avant de te connecter.";
  if (error.message.includes("already registered")) return "Cette adresse possède déjà un compte. Essaie de te connecter.";
  if (error.message.includes("Password should be at least")) return "Choisis un mot de passe d’au moins 12 caractères.";
  return error.message;
}

function AuthScreen({ initialMode = "sign-in", onRecoveryComplete }: AuthScreenProps) {
  const [mode, setMode] = useState<AuthMode>(initialMode);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [school, setSchool] = useState("");
  const [studyYear, setStudyYear] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirmation, setPasswordConfirmation] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const configured = supabase !== null;
  const needsEmail = mode === "sign-in" || mode === "sign-up" || mode === "forgot-password";
  const needsPassword = mode === "sign-in" || mode === "sign-up" || mode === "update-password";
  const needsConfirmation = mode === "sign-up" || mode === "update-password";
  const needsStudentProfile = mode === "sign-up";

  function changeMode(nextMode: AuthMode) {
    setMode(nextMode);
    setErrorMessage("");
    setPassword("");
    setPasswordConfirmation("");
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    if (!supabase) {
      setErrorMessage("La connexion Supabase n’est pas configurée pour cette application.");
      return;
    }
    if (needsConfirmation && password !== passwordConfirmation) {
      setErrorMessage("Les deux mots de passe ne correspondent pas.");
      return;
    }
    if (needsStudentProfile && (!firstName.trim() || !lastName.trim())) {
      setErrorMessage("Le prénom et le nom sont obligatoires.");
      return;
    }

    setBusy(true);
    try {
      if (mode === "sign-in") {
        const { error } = await supabase.auth.signInWithPassword({ email: email.trim(), password });
        if (error) throw error;
      } else if (mode === "sign-up") {
        const { data, error } = await supabase.auth.signUp({
          email: email.trim(),
          password,
          options: {
            emailRedirectTo: window.location.origin,
            data: {
              first_name: firstName.trim(),
              last_name: lastName.trim(),
              school: school.trim() || null,
              study_year: studyYear || null,
            },
          },
        });
        if (error) throw error;
        if (!data.session) changeMode("email-sent");
      } else if (mode === "forgot-password") {
        const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), {
          redirectTo: window.location.origin,
        });
        if (error) throw error;
        changeMode("email-sent");
      } else if (mode === "update-password") {
        const { error } = await supabase.auth.updateUser({ password });
        if (error) throw error;
        onRecoveryComplete?.();
      }
    } catch (error) {
      setErrorMessage(getAuthErrorMessage(error));
    } finally {
      setBusy(false);
    }
  }

  const title = {
    "sign-in": "Content de te revoir.",
    "sign-up": "Crée ton espace.",
    "forgot-password": "Récupère ton accès.",
    "update-password": "Choisis un nouveau mot de passe.",
    "email-sent": "Vérifie ta boîte mail.",
  }[mode];

  return (
    <main className="auth-shell">
      <aside className="auth-aside">
        <a className="auth-brand" href="/" aria-label="ArchiProf, accueil">
          <span className="auth-brand-mark"><GraduationCap size={20} strokeWidth={1.8} /></span>
          <span className="auth-brand-word">archi<span>prof</span><small>ATELIER D’APPRENTISSAGE</small></span>
        </a>
        <div className="auth-aside-content">
          <div className="auth-portrait"><img src={assistantPortrait} alt="ArchiProf, assistant pédagogique en architecture" /></div>
          <div className="auth-aside-copy">
            <span>ESPACE ÉTUDIANT</span>
            <h1>Ton atelier, tes projets, tes repères.</h1>
            <p>Retrouve tes cours et poursuis ta réflexion de projet au même endroit.</p>
          </div>
        </div>
        <div className="auth-aside-foot"><ShieldCheck size={15} /> Un espace personnel, réservé à ton compte</div>
      </aside>

      <section className="auth-main" aria-labelledby="auth-title">
        <div className="auth-form-wrap">
          <div className="auth-heading">
            <span className="auth-kicker">ARCHIPROF · ESPACE ÉTUDIANT</span>
            <h2 id="auth-title">{title}</h2>
            <p>
              {mode === "sign-in" && "Connecte-toi pour retrouver ton espace de travail."}
              {mode === "sign-up" && "Prénom et nom sont requis. École et année restent facultatives."}
              {mode === "forgot-password" && "Nous t’enverrons un lien pour choisir un nouveau mot de passe."}
              {mode === "update-password" && "Utilise au moins 12 caractères pour sécuriser ton compte."}
              {mode === "email-sent" && `Un email vient d’être envoyé à ${email}.`}
            </p>
          </div>

          {!configured && (
            <div className="auth-notice auth-notice-error" role="alert">
              <b>Connexion non configurée</b>
              <span>Définis `VITE_SUPABASE_URL` et `VITE_SUPABASE_PUBLISHABLE_KEY` pour cet environnement.</span>
            </div>
          )}

          {(mode === "sign-in" || mode === "sign-up") && (
            <div className="auth-segment" role="tablist" aria-label="Type d’accès">
              <button type="button" role="tab" aria-selected={mode === "sign-in"} onClick={() => changeMode("sign-in")}>Connexion</button>
              <button type="button" role="tab" aria-selected={mode === "sign-up"} onClick={() => changeMode("sign-up")}>Créer un compte</button>
            </div>
          )}

          {mode === "email-sent" ? (
            <div className="auth-success" role="status">
              <span className="auth-success-icon"><Check size={20} /></span>
              <b>Regarde tes emails</b>
              <p>Ouvre le message de Supabase et suis son lien pour continuer. Pense à vérifier les courriers indésirables.</p>
              <button className="auth-back-link" type="button" onClick={() => changeMode("sign-in")}>Retour à la connexion <ArrowRight size={15} /></button>
            </div>
          ) : (
            <form className="auth-form" onSubmit={submit}>
              {needsStudentProfile && (
                <>
                  <div className="auth-name-grid">
                    <label className="auth-field">
                      <span>Prénom</span>
                      <input className="auth-text-input" type="text" autoComplete="given-name" value={firstName} onChange={(event) => setFirstName(event.target.value)} placeholder="Camille" maxLength={80} required />
                    </label>
                    <label className="auth-field">
                      <span>Nom</span>
                      <input className="auth-text-input" type="text" autoComplete="family-name" value={lastName} onChange={(event) => setLastName(event.target.value)} placeholder="Martin" maxLength={80} required />
                    </label>
                  </div>
                  <label className="auth-field">
                    <span>École <small>Facultatif</small></span>
                    <input className="auth-text-input" type="text" autoComplete="organization" value={school} onChange={(event) => setSchool(event.target.value)} placeholder="Nom de ton école" maxLength={160} />
                  </label>
                  <label className="auth-field">
                    <span>Année d’études <small>Facultatif</small></span>
                    <select className="auth-text-input auth-select" value={studyYear} onChange={(event) => setStudyYear(event.target.value)}>
                      <option value="">Sélectionner</option>
                      <option value="1re année">1re année</option>
                      <option value="2e année">2e année</option>
                      <option value="3e année">3e année</option>
                      <option value="4e année">4e année</option>
                      <option value="5e année">5e année</option>
                      <option value="autre">Autre parcours</option>
                    </select>
                  </label>
                </>
              )}

              {needsEmail && (
                <label className="auth-field">
                  <span>Adresse email</span>
                  <span className="auth-input-wrap"><Mail size={17} /><input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="toi@exemple.fr" required autoFocus /></span>
                </label>
              )}

              {needsPassword && (
                <label className="auth-field">
                  <span>{mode === "update-password" ? "Nouveau mot de passe" : "Mot de passe"}</span>
                  <span className="auth-input-wrap"><LockKeyhole size={17} /><input type={showPassword ? "text" : "password"} autoComplete={mode === "sign-in" ? "current-password" : "new-password"} value={password} onChange={(event) => setPassword(event.target.value)} placeholder={mode === "sign-in" ? "Ton mot de passe" : "12 caractères minimum"} minLength={mode === "sign-in" ? 1 : 12} required /><button className="auth-password-toggle" type="button" onClick={() => setShowPassword((visible) => !visible)} aria-label={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}>{showPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button></span>
                </label>
              )}

              {needsConfirmation && (
                <label className="auth-field">
                  <span>Confirmer le mot de passe</span>
                  <span className="auth-input-wrap"><KeyRound size={17} /><input type={showPassword ? "text" : "password"} autoComplete="new-password" value={passwordConfirmation} onChange={(event) => setPasswordConfirmation(event.target.value)} placeholder="Répète le mot de passe" minLength={12} required /></span>
                </label>
              )}

              {errorMessage && <p className="auth-error" role="alert">{errorMessage}</p>}

              <button className="auth-submit" type="submit" disabled={busy || !configured}>
                {busy ? "Un instant…" : mode === "sign-in" ? "Se connecter" : mode === "sign-up" ? "Créer mon compte" : mode === "forgot-password" ? "Envoyer le lien" : "Enregistrer le mot de passe"}
                {!busy && <ArrowRight size={17} />}
              </button>

              {mode === "sign-in" && <button className="auth-text-link" type="button" onClick={() => changeMode("forgot-password")}>Mot de passe oublié ?</button>}
              {(mode === "forgot-password" || mode === "update-password") && <button className="auth-back-link" type="button" onClick={() => changeMode("sign-in")}>Retour à la connexion <ArrowRight size={15} /></button>}
            </form>
          )}

          <p className="auth-legal">En continuant, tu utilises un espace personnel. Tes projets et tes cours ne sont pas partagés avec d’autres comptes.</p>
        </div>
        <footer className="auth-footer"><span>ARCHIPROF</span><span>•</span><span>APPRENDRE, CONCEVOIR, PROGRESSER</span></footer>
      </section>
    </main>
  );
}

export default AuthScreen;