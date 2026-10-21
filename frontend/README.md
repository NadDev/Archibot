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

Le helper `src/api.ts` ajoute le bearer JWT à une requête backend. Après connexion, les projets et interactions affichés restent toutefois des données de démonstration en mémoire : ils ne sont pas encore persistés et ne sont pas liés au compte Auth.
