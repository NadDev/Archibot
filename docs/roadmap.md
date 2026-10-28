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
- Incrément livré : upload de cours privé -> extraction PDF automatique -> chunks persistés -> retrieval des cours associés au projet, avec pages conservées. Statut et erreur consultables ; reprise uniquement en attente ou après échec.
- Migration `course_extraction.sql` appliquée à Supabase après validation sur PostgreSQL 18 local : sauvegarde atomique, RLS propriétaire, relance sans doublons et suppression en cascade.
- Parcours réel testé dans le navigateur avec un compte dédié, sur desktop/mobile : succès multipage, PDF invalide, image non prise en charge, rechargement, reprise, association à un projet et suppression.
- Organisation du nouveau code par fonctionnalité : `app/extraction/`, `app/upload/`, `frontend/src/features/extraction/` et `frontend/src/features/upload/`.
- La feature 3.1.3 reste en cours : OCR des scans et rapports complets de qualité/durée restent à livrer. Le chat, les synthèses et les embeddings ne sont pas branchés par cet incrément.

## Proposition de lots multi-format
1. Finir 3.1.3 : OCR des photos/scans et pages PDF sans texte, orientation/langues, qualité et erreurs par page ; limiter les ressources et préparer le traitement asynchrone.
2. Word : DOCX natif (paragraphes, titres, tableaux, provenance par section), puis conversion isolée des anciens DOC. Ne pas inventer de numéros de page pour un document reformatable.
3. EPUB : extraction par chapitre/section avec liens de provenance ; validation ZIP, limites de décompression, fichiers protégés explicitement refusés. Étendre l'upload et les MIME autorisés à cette étape.
4. Données structurées : tableaux et éléments métier avec schéma, provenance et tests propres ; ne pas assimiler extraction de texte et compréhension d'image.
5. Indexation : embeddings persistés et retrieval vectoriel sur le contrat documentaire commun.
