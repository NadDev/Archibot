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

Le prototype utilise des données en mémoire uniquement. Il n’envoie pas de messages, ne téléverse pas de fichiers et ne se connecte pas à Google Drive ou à l’API. Les projets et interactions créés dans l’interface sont perdus au rechargement. Le contrat API front-driven reste à définir avant l’intégration backend.
