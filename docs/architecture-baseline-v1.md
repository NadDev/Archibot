# Architecture Baseline v1

Date: 2026-09-28
Statut: Valide par ARCHI + PM/PO + DEVEX

## 1. Ce qui est deja defini (OK)
- Vision produit, cible et perimetre MVP.
- RAG-first avec separation de provenance (cours, regle generale, source reglementaire locale).
- Pipeline documentaire global (ingestion -> extraction -> chunking -> metadata -> embeddings -> indexation -> retrieval).
- Strategie low-cost et gouvernance d'execution multi-agents.
- Mapping de responsabilites via Trello (PM/PO, UX/UI, ARCHI, DEV, QE, DevEx).

## 2. Ce qui manque pour une architecture globale executable

### 2.1 Choix technologiques fermes
- Frontend: valide (F2 React + Vite + TypeScript + Tailwind).
- Backend: valide (B1 FastAPI + worker async).
- Hebergement backend: valide (local dev -> Oracle Free beta -> Oracle payant si seuils).
- Vector DB / SQL / objet: valide via D1 (Supabase Postgres + Storage + pgvector).

### 2.2 Contrats techniques
- Contrat schema metadata minimal (types, champs obligatoires, version).
- Contrat format de sortie 3 sections (schema versionne).
- Contrat API (endpoints, erreurs, pagination, limits).

### 2.3 NFR / SLO minimaux
- SLO latence chat p50/p95.
- Budget cout IA par session/utilisateur.
- Disponibilite cible MVP.
- Politique retry/idempotence pour ingestion/indexation.

### 2.4 Securite et conformite
- Politique secrets/env.
- Regles de retention des donnees et documents.
- Droits d'acces par utilisateur/projet.

### 2.5 Exploitation
- Environnements dev/staging/prod.
- CI gates minimales.
- Runbook release/rollback.
- Observabilite minimale (logs, metriques, alertes).

## 3. Gate de demarrage dev
Le dev applicatif avance seulement si:
1. Les choix technos ci-dessus sont valides.
2. Les contrats metadata + sortie sont versionnes.
3. Les SLO/couts cibles sont explicites.
4. Le workflow release/rollback est praticable en staging.

## 4. Decisions a prendre cette semaine
1. Schema metadata v1.
2. Schema sortie reponse v1.
3. SLO latence + budget cout IA.
4. Seuils explicites de bascule Oracle Free -> Oracle payant.

## 5. Output attendu
- ADR-001 Architecture globale v1 (decision log).
- Mise a jour de architecture.md avec versions et choix fermes.
- Ticket Trello de validation ferme (Go sprint execution).
