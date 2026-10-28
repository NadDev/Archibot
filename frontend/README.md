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

Le helper `src/api.ts` ajoute le bearer JWT à une requête backend. Pour activer la persistance des projets, des cours personnels et de leurs associations aux projets, exécuter dans cet ordre `backend/sql/projects.sql`, `backend/sql/user_courses.sql` puis `backend/sql/project_courses.sql` dans le SQL Editor du projet Supabase.

Les projets, métadonnées des cours, fichiers de cours et associations cours-projets sont privés au compte connecté via RLS. Les cours généraux se sélectionnent lors de la création d’un projet et restent modifiables depuis son contexte. Une description de projet est conservée comme résumé. Les fichiers sont acceptés jusqu’à 50 Mio, en PDF, Word (DOC/DOCX), PNG, JPEG ou WebP. L’indexation documentaire n’est pas encore activée : les supports sont stockés mais pas analysés, et aucune suggestion de cours par IA n’est disponible. Les documents attachés aux projets, notes et conversations restent des éléments de démonstration non persistés.
