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
- Feature 5.1.4: Espace de cours généraux, indépendant des projets, pour les révisions et le contexte interprojet ([spec](../docs/feature-5.1.4-cours-generaux-transversal.md))

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

## Sequence d'execution du MVP large

Les lots existants sont le decoupage produit. La sequence ci-dessous les rend executables et ajoute les gates de livraison manquants. Le prototype frontend actuel ne compte pas comme une feature terminee tant qu'il n'est pas branche au backend et aux donnees persistantes.

### Etape A - Verrouiller les decisions d'execution
- Confirmer le fournisseur LLM, les modeles generation/embeddings et les limites de cout.
- Confirmer l'authentification, la retention/suppression et les formats/tailles de fichiers.
- Confirmer le perimetre OAuth Drive : dossier autorise, import initial, synchronisation et revocation.
- Sortie : criteres d'acceptation et contrats API versionnes ; aucune cle ou donnee sensible dans le depot.

### Etape B - Socle applicatif et donnees (Lots 2 et 6)
- Implementer authentification et autorisation par compte/projet.
- Persister comptes, projets, documents, conversations et metadonnees dans Supabase ; stocker les fichiers dans Supabase Storage.
- Activer pgvector, migrations, contraintes d'acces/RLS et configuration des environnements.
- Ajouter CI backend/frontend, tests d'integration et environnements dev/staging.
- Sortie : donnees isolees entre comptes, migrations reproductibles et pipeline CI vert.

### Etape C - Ingestion documentaire (Lot 3)
- Upload PDF : validation, extraction texte page par page, chunks avec provenance/page, stockage objet et etat d'indexation.
- Traiter les PDF sans texte ; ajouter OCR aux scans simples et exposer clairement les echecs.
- Integrer Google Drive avec OAuth, choix du dossier, import incremental, suppression/revocation et deduplication.
- Sortie : un document suit upload/import -> extraction -> chunks persistes, avec etat consultable et tests bout-en-bout.

### Etape D - RAG et assistant LLM (Lot 4)
- Generer et persister les embeddings ; implementer recherche vectorielle top-k avec filtres de proprietaire, portee, projet, source et localite.
- Appeler le LLM via une interface fournisseur, avec prompt pedagogique, limites de contexte, timeouts et controle des couts.
- Produire le schema versionne cours / regle generale / source locale, citations vers les chunks et reponse prudente sans source.
- Ajouter un jeu d'evaluation golden pour retrieval, citations, qualite et latence.
- Sortie : un PDF importe peut justifier une reponse du LLM par des citations exactes ; les acces non autorises ne retournent aucun extrait.

### Etape E - Parcours pedagogiques (Lot 5)
- Revisions et syntheses depuis les cours generaux, meme sans projet actif.
- Selection explicite de cours generaux dans un projet et memoire/historique de projet.
- Aide a la problematique, au concept, a la logique spatiale et plan d'amelioration iteratif.
- Generation d'exercices/quiz, correction guidee et progression par niveau.
- Sortie : parcours valides avec etudiants, contenu source affiche et resultats persistes selon le compte.

### Etape F - Integration frontend (Lot 6)
- Remplacer les donnees et actions de demo par les endpoints du contrat.
- Couvrir connexion, projets, bibliotheque, upload/Drive, etats d'indexation, chat/citations, historique et parcours pedagogiques.
- Verifier accessibilite, mobile, erreurs, chargement, etat vide et reauthentification.
- Sortie : tests de parcours front-back automatises et validation UX sur desktop/mobile.

### Etape G - Release MVP (Lots 2 et 6)
- Deployer staging puis production web/API ; configurer domaine HTTPS, secrets, migrations et sauvegardes.
- Ajouter logs, metriques, alertes, suivi cout/latence, runbook et rollback teste.
- Verifier SLO ADR-001, securite, tests QE et validation PM/PO avant ouverture aux etudiants.
- Sortie : gate DevEx/QE/PM-PO validee et release exploitable.

### Etape H - Extensions hors MVP (Lot 7)
- Ingestion des corpus PLU/normes, versioning reglementaire et applicabilite geographique.
- Ne demarre qu'apres validation du MVP et du pipeline de provenance.

### Premier increment technique selectionne
- Lot 3.1.3 : extraction PDF textuelle page par page et decoupage en chunks avec numero de page.
- Cette bibliotheque de traitement est testee avant son exposition par API ; upload public et persistance attendent l'authentification, le stockage et le contrat de document du Lot 2.
- Criteres : PDF texte valide -> chunks non vides rattaches a une page ; PDF invalide, vide ou sans texte -> erreur explicite ; taille et recouvrement des chunks valides.

### Prochaine etape technique a reprendre
 - Modele valide : projets, cours et documents prives a un seul proprietaire, sans partage entre comptes. Le corpus d'architecture generale est une table separee, en lecture pour les comptes authentifies et alimentee par l'administration.
 - Implemente localement : bearer Supabase Auth requis pour retrieval/ingestion/assistant ; le JWT utilisateur est transmis a PostgREST ; `chunks.owner_id` est force cote API et RLS le limite a `auth.uid()` ; l'API ne peut pas ecrire dans le corpus commun.
 - Migration SQL fail-closed : les anciennes lignes sans `owner_id` restent invisibles. Il faut verifier/attribuer explicitement leurs proprietaires avant toute remise en service de donnees existantes.
 - Reste a faire : appliquer la migration au projet Supabase, verifier la configuration des roles/grants, et executer des tests d'integration avec deux comptes Auth reels pour confirmer l'isolation et la lecture du corpus commun.
 - Gate avant le prochain jalon : tests RLS distants verts. Ensuite seulement, poursuivre l'upload persistant, l'indexation pgvector et le retrieval top-k avec embeddings.
