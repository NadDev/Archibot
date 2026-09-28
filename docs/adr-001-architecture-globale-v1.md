# ADR-001 - Architecture Globale v1

Date: 2026-09-28
Status: Accepted
Owners: ARCHI, PM/PO, DevEx

## 1. Contexte
Archibot doit livrer un MVP RAG-first pour etudiants en architecture (L1/L2), avec separation stricte de provenance:
- cours
- regle generale
- source reglementaire locale

L'architecture doit rester low-cost, observable, et deployable rapidement sans sur-ingenierie.

## 2. Decision drivers
- qualite de reponse et traçabilite des sources
- cout d'exploitation maitrise
- simplicite de delivery
- evolutivite vers sources externes reglementaires
- robustesse minimale (tests, CI, rollback)

## 3. Decisions architecture v1

### 3.1 Macro-architecture
Decision:
- Frontend web
- Backend API
- Pipeline ingestion/indexation async
- Retrieval + generation contextualisee
- Stockage separe: SQL + objet + vecteur

Rationale:
- decouplage clair UX / logique IA / data
- exploitation simple par petites equipes agents

### 3.2 Contrat de provenance
Decision:
Chaque chunk doit porter des metadonnees minimales:
- source_type: course | general | local_regulation
- source_id: identifiant document
- project_id
- doc_version
- locality (nullable)
- ingested_at (UTC)

Rationale:
- filtre retrieval deterministe
- affichage fiable des sections de sortie

### 3.3 Contrat de sortie reponse
Decision:
Le backend retourne un schema versionne contenant:
- cours
- regle_generale
- source_reglementaire_locale
- citations[]
- warning_no_source (optionnel)

Rationale:
- enforce la separation de provenance
- facilite validation QE automatisee

### 3.4 Pipeline documentaire
Decision:
Flux v1:
1) upload/drive import
2) extraction texte
3) chunking
4) validation metadonnees
5) embeddings
6) indexation
7) retrieval top-k filtre

Rationale:
- pipeline mesurable et testable bout-en-bout

### 3.5 NFR minimum (MVP)
Decision:
- latence chat p95 cible: <= 8 s
- erreurs retrieval bloquantes: < 2%
- cout IA cible: plafond mensuel defini par PM/PO
- disponibilite cible MVP: 99.0% (hors maintenance)

Rationale:
- objectifs realistes pour MVP low-cost

### 3.6 Exploitation DevEx
Decision:
- environnements: dev, staging, prod
- CI gate bloquante: tests unitaires + integration retrieval + conformite format de sortie
- release: runbook obligatoire
- rollback: procedure documentee et testee sur staging

Rationale:
- limite les regressions et facilite la mise en prod

## 4. Points a figer maintenant (choix fermes)
A trancher en comite ARCHI/PMPO/DevEx:
1. Stack frontend exacte
2. Stack backend exacte
3. Provider SQL/objet/vecteur
4. Modele embeddings initial
5. Politique retention donnees

## 4.b Choix valides a ce stade
Valides par PM/PO:
- Frontend: F2 (React + Vite + TypeScript + Tailwind)
- Backend: B1 (FastAPI + worker async)
- Data layer: D1 (Supabase: Postgres + Storage + pgvector)
- Embeddings: E1 (OpenAI embedding small)
- Retention: R2 (politique stricte, logs courts)

## 4.c Strategie hebergement backend
Decision:
- Phase dev: execution locale gratuite
- Phase MVP beta: Oracle Cloud Always Free
- Phase croissance: plan payant Oracle (ou migration) selon seuils

Decision operationnelle immediate:
- le projet demarre en local sans bloquer sur l'hebergeur
- la configuration Oracle sera faite ensemble au moment necessaire

Seuils de bascule proposes:
1. indisponibilite > 2 incidents/mois impactant les utilisateurs
2. charge moyenne > 60% CPU sur les plages actives
3. besoin de SLA superieur a ce que le Free peut garantir

Estimation cout backend:
- local: 0 EUR/mois
- Oracle Free: 0 EUR/mois (dans quotas)
- Oracle payant MVP: environ 20-80 EUR/mois selon taille VM, trafic et observabilite

Competitivite Oracle (ordre de grandeur MVP backend):
- Oracle payant est souvent competitif vs cloud generalistes a specs proches
- Le cout final depend surtout du niveau de fiabilite souhaite, du reseau sortant, et des services manages ajoutes
- En phase initiale, Oracle Free + Supabase est un tres bon ratio cout/valeur

## 5. Acceptance criteria ADR-001
- ADR approuve par ARCHI + PM/PO + DevEx
- architecture.md alignee avec decisions ci-dessus
- tests de conformite schema metadata + schema sortie disponibles
- carte Trello [ARCHI] Figer Architecture Globale v1 closee

## 6. Consequences
Positives:
- cadre global explicite avant extension feature
- reduction des ambiguities inter-equipes

Negatives:
- leger cout initial de formalisation
- decisions stack a prendre rapidement pour eviter blocage
- risque d'ecart entre environnement Free et contraintes reelles de production
