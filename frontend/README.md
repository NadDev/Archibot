# ArchiProf Frontend

Premier shell React/Vite du produit, aligné sur le cycle front-driven : liste des projets, vue détaillée d’un projet, chat à provenance, historique récent, bibliothèque documentaire et exercice guidé.

## Démarrer

```powershell
cd frontend
npm install
npm run dev
```

## Construire

```powershell
npm run build
```

## Authentification Supabase

En local, Vite lit `SUPABASE_URL` et `SUPABASE_PUBLISHABLE_KEY` depuis `backend/.env`. En déploiement, définir `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY` et `VITE_API_URL` dans l’environnement frontend. N’exposer aucune clé service ou secret au navigateur.

Le parcours utilise email + mot de passe, confirmation email et récupération par lien. Dans Supabase Auth, configurer l’URL du site et autoriser les URL de redirection de chaque environnement. Une configuration SMTP de production est recommandée pour assurer la délivrabilité des emails.

Le helper `src/api.ts` ajoute le bearer JWT à une requête backend. Pour activer la persistance des projets, des cours personnels, de leurs associations et de leur extraction, appliquer dans cet ordre `backend/sql/projects.sql`, `backend/sql/user_courses.sql`, `backend/sql/project_courses.sql`, `backend/sql/course_extraction.sql` puis `backend/sql/course_document_locations.sql`.

Les projets, métadonnées des cours, fichiers de cours et associations cours-projets sont privés au compte connecté via RLS. Les cours généraux se sélectionnent lors de la création d’un projet et restent modifiables depuis son contexte. Une description de projet est conservée comme résumé. Les fichiers sont acceptés jusqu’à 50 Mio, en PDF, DOC/DOCX, PPTX, EPUB, PNG, JPEG ou WebP.

Après l'envoi d'un cours, l'extraction est déclenchée automatiquement via l'API locale (`http://localhost:8000` par défaut, surchargeable par `VITE_API_URL`). PDF, DOCX, PPTX et EPUB sont découpés et persistés avec des localisateurs adaptés (page, section, diapositive, chapitre). La bibliothèque affiche le statut enregistré ; la vue du cours propose « Réessayer » pour un format pris en charge en attente ou en échec, y compris les anciens enregistrements à relancer. Aucun bouton d'extraction n'est affiché après succès. Une panne API ne supprime pas le fichier envoyé.

La logique documentaire est rangée dans `src/features/upload/` et `src/features/extraction/`. DOC et PPT binaires, images, OCR de scans, notes de présentation et texte dans les images restent non extraits. « Texte extrait » ne signifie pas indexation vectorielle ni analyse IA. Synthèses, quiz et chat restent en démonstration, comme les fichiers propres aux projets, les notes et les conversations.
