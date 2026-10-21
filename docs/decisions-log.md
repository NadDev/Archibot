# Journal des décisions

## Décisions actées
- 2026-10-19 : retenir un périmètre MVP large couvrant les parcours cours, projets, exercices, documents, Google Drive, RAG, LLM et mise en production ; le cycle front-driven est un incrément, pas le périmètre complet. Référence : `docs/mvp.md`.
- 2026-10-19 : embeddings exécutés localement via FastEmbed ; modèle multilingue initial `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions), à évaluer sur nos documents français. Le fournisseur du LLM de génération reste à choisir.
 - 2026-10-21 : séparer les chunks privés (cours, documents et réglementation de l'utilisateur, limités au propriétaire/projet) du corpus d'architecture générale commun, lisible par tout compte authentifié et alimenté par l'administration uniquement. Les projets restent privés, sans partage entre comptes.
- RAG dès le départ
- cible : étudiant 1re / 2e année
- aide aux cours et à la production
- import via upload et Google Drive
- infra low-cost
- Trello piloté via MCP
- architecture prête à accueillir les sources externes
- réponse structurée : cours / règle générale / source réglementaire locale
- démarrage immédiat en local; configuration hébergeur Oracle reportée au moment utile

## Décisions à confirmer
- stack frontend
- stack backend
- base vectorielle
- fournisseur d'hébergement
- format exact des exports
- politique de mémoire long terme
- stratégie de versioning des documents
