# Roadmap

## Phase 0 — Cadrage
- figer la vision
- figer la cible
- figer le MVP
- définir les règles de réponse
- définir la stratégie coût / infra
- définir la structure du workspace

## Phase 1 — Squelette du projet
- créer l'arborescence du repo
- créer le document maître
- créer le backlog initial
- créer le board Trello
- connecter Trello MCP

## Phase 2 — Socle technique
- authentification
- stockage
- base de données
- base vectorielle
- ingestion de fichiers
- ingestion Google Drive

## Phase 3 — RAG et assistant
- indexation documentaire
- retrieval
- génération contextualisée
- citations / provenance
- gestion des réponses par type de source

## Phase 4 — UX et pédagogie
- parcours étudiant
- création d'exercices
- mémoire de projet
- amélioration des prompts
- réduction des réponses génériques

## Phase 5 — Extensions
- sources externes
- PLU
- réglementation locale
- normes
- fonctionnalités avancées de suivi

## Règle de pilotage
Aucune phase suivante ne démarre avant validation du socle précédent.

## État du cycle documentaire (2026-10-28)
- Socle validé : Auth, projets et cours/fichiers privés avec RLS ; l'utilisateur a confirmé l'isolation entre deux comptes.
- Extraction initiale : PDF texte extrait page par page, chunking configurable et provenance `page_number`/`chunk_index` conservée dans les schémas, le store Supabase et le retrieval.
- Migration `chunk_page_provenance.sql` appliquée au projet Supabase ; `chunks.sql` inclut les colonnes pour les nouvelles installations.
- Prochaine feature : relier l'upload privé à l'extraction et à la persistance des chunks, avec vérification de propriété et état d'indexation consultable.
- Ensuite : OCR des scans, puis embeddings persistés et retrieval vectoriel top-k.
- Gate : test bout-en-bout upload -> extraction -> chunks persistés -> retrieval avec citation de page, sans fuite inter-comptes.
