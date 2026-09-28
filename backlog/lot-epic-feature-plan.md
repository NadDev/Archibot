# Plan de structuration backlog

## Hiérarchie officielle
- Niveau 1: Lot/Batch (macro-sujet)
- Niveau 2: Epic (objectif produit cohérent)
- Niveau 3: Feature (fonctionnalité livrable)

## Règles de liaison
- Une Feature appartient a un seul Epic.
- Un Epic appartient a un seul Lot/Batch.
- Toute dépendance doit être documentée entre Epics ou Features.
- Une Feature ne peut pas démarrer sans Epic parent validé.

## Lot/Batch 0 - Gouvernance produit et exécution
### Epic 0.1 - Cadrage produit MVP
- Feature 0.1.1: Vision produit validée (cible 1re/2e année)
- Feature 0.1.2: Périmètre MVP figé
- Feature 0.1.3: Non-objectifs validés
- Feature 0.1.4: Critères de succès/KPI définis

### Epic 0.2 - Gouvernance backlog et agents
- Feature 0.2.1: Modèle PMPO/ARCHI/DEV validé
- Feature 0.2.2: Mapping agent -> type de ticket -> checklist
- Feature 0.2.3: Template standard de ticket

## Lot/Batch 1 - Fondation workspace et delivery
### Epic 1.1 - Documentation maître
- Feature 1.1.1: Document maître à jour
- Feature 1.1.2: Roadmap versionnée
- Feature 1.1.3: Journal des décisions actif

### Epic 1.2 - Pilotage Trello via MCP
- Feature 1.2.1: Connexion MCP Trello validée
- Feature 1.2.2: Board + listes standards créés
- Feature 1.2.3: Convention labels/nommage active

## Lot/Batch 2 - Socle technique low-cost
### Epic 2.1 - Plateforme backend/frontend
- Feature 2.1.1: Structure app initiale
- Feature 2.1.2: Authentification de base
- Feature 2.1.3: Configuration environnement

### Epic 2.2 - Data et stockage
- Feature 2.2.1: Base relationnelle choisie et branchée
- Feature 2.2.2: Stockage objet branché
- Feature 2.2.3: Base vectorielle low-cost branchée

## Lot/Batch 3 - Ingestion documentaire et indexation
### Epic 3.1 - Ingestion locale
- Feature 3.1.1: Upload PDF
- Feature 3.1.2: Upload images/scans
- Feature 3.1.3: Extraction texte initiale

### Epic 3.2 - Ingestion Google Drive
- Feature 3.2.1: OAuth Drive
- Feature 3.2.2: Import de dossier cible
- Feature 3.2.3: Sync incrémentale

### Epic 3.3 - Pipeline d'indexation
- Feature 3.3.1: Chunking configurable
- Feature 3.3.2: Métadonnées minimales
- Feature 3.3.3: Embeddings + indexation

## Lot/Batch 4 - Assistant RAG métier architecture
### Epic 4.1 - Retrieval et génération contextualisée
- Feature 4.1.1: Retrieval top-k avec filtres
- Feature 4.1.2: Prompting anti-générique
- Feature 4.1.3: Routage modèles (premium vs low-cost)

### Epic 4.2 - Provenance et format de réponse
- Feature 4.2.1: Sortie structurée cours / règle générale / source locale
- Feature 4.2.2: Citations des passages de référence
- Feature 4.2.3: Gestion du manque de source (réponse prudente)

## Lot/Batch 5 - Expérience pédagogique
### Epic 5.1 - Aide aux cours
- Feature 5.1.1: Explication de notions
- Feature 5.1.2: Résumés de cours
- Feature 5.1.3: Quiz de révision

### Epic 5.2 - Aide à la production de projet
- Feature 5.2.1: Structuration concept/problématique
- Feature 5.2.2: Feedback sur logique spatiale
- Feature 5.2.3: Plan d'amélioration par itération

### Epic 5.3 - Exercices et correction guidée
- Feature 5.3.1: Génération d'exercices
- Feature 5.3.2: Correction pédagogique
- Feature 5.3.3: Progression par niveau

## Lot/Batch 6 - Front UX/UI MVP
### Epic 6.1 - Parcours et architecture de l'information
- Feature 6.1.1: Définir les parcours critiques étudiant (cours/projet/exercices)
- Feature 6.1.2: Définir l'architecture de navigation MVP
- Feature 6.1.3: Définir les états UX (vide/chargement/erreur/sans source)

### Epic 6.2 - Ecrans et composants critiques
- Feature 6.2.1: Ecran chat pédagogique avec provenance visible
- Feature 6.2.2: Ecran bibliothèque documentaire (upload/Drive/indexation)
- Feature 6.2.3: Ecran exercices/correction guidée

### Epic 6.3 - Qualité UX et accessibilité
- Feature 6.3.1: Microcopy pédagogique et claire
- Feature 6.3.2: Règles d'accessibilité de base
- Feature 6.3.3: Checklist UX de validation avant mise en production

## Lot/Batch 7 - Extensions réglementaires (lot ultérieur)
### Epic 7.1 - Sources externes
- Feature 7.1.1: Intégration corpus PLU
- Feature 7.1.2: Intégration normes locales
- Feature 7.1.3: Versioning et validité des textes

### Epic 7.2 - Applicabilité réglementaire
- Feature 7.2.1: Qualification géographique du besoin
- Feature 7.2.2: Distinction règle générale vs locale
- Feature 7.2.3: Niveau de confiance réglementaire affiché

## Dépendances majeures
- Lot/Batch 1 dépend de Lot/Batch 0.
- Lot/Batch 2 dépend de Lot/Batch 1.
- Lot/Batch 3 dépend de Lot/Batch 2.
- Lot/Batch 4 dépend de Lot/Batch 3.
- Lot/Batch 5 dépend de Lot/Batch 4.
- Lot/Batch 6 dépend de Lot/Batch 4 et 5.
- Lot/Batch 7 dépend de Lot/Batch 4, 5 et 6.
