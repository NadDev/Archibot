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

Le helper `src/api.ts` ajoute le bearer JWT à une requête backend. Pour activer la persistance des projets et de la bibliothèque personnelle de cours, exécuter `backend/sql/projects.sql` puis `backend/sql/user_courses.sql` dans le SQL Editor du projet Supabase.

Les projets, métadonnées des cours et fichiers de cours sont privés au compte connecté via RLS. Les fichiers sont acceptés jusqu’à 50 Mio, en PDF, Word (DOC/DOCX), PNG, JPEG ou WebP. L’indexation documentaire n’est pas encore activée : les supports sont stockés mais pas analysés. Les documents attachés aux projets, notes et conversations restent des éléments de démonstration non persistés.
