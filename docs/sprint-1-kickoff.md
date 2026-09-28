# Sprint 1 Kickoff (Agent Mode)

Date: 2026-09-28

## Pre-flight obligatoire
Avant execution technique continue, valider la baseline globale:
- voir architecture-baseline-v1.md
- produire ADR-001 Architecture globale v1
- accord explicite ARCHI + PM/PO + DevEx

## Objectif sprint
Livrer un premier flux RAG fiable avec provenance exploitable pour Archibot:
- metadata minimales sur les chunks
- retrieval top-k filtre
- sortie structuree en 3 sections (cours, regle generale, source reglementaire locale)

## Scope active (3 features)
1. [FEAT 3.3.2] Metadonnees minimales
2. [FEAT 4.1.1] Retrieval top-k avec filtres
3. [FEAT 4.2.1] Sortie structuree cours/general/local

## Ordre d'execution par role
1. PM/PO
- valider wording metier de la sortie 3 sections
- valider acceptance criteria metier des 3 features

2. ARCHI
- figer contrat metadata minimal
- figer schema de sortie versionne
- valider strategie retrieval top-k + filtres

3. DEV
- implementer metadata validation + persistance
- implementer retrieval + fallback no-context
- implementer validateur de sortie 3 sections

4. QE
- tests unitaires de schema metadata
- tests integration ingestion->retrieval->sortie
- tests golden outputs sur structure de sortie

5. DevEx/Platform
- CI gate: tests metadata/retrieval/format
- artifacts de tests et rapport de run

## Gate de fin de sprint
Une feature passe en Review / Validate uniquement si:
- acceptance criteria feature atteints
- evidence de tests QE jointe
- gate CI verte

Fermeture sprint si tri-validation:
- PM/PO
- QE
- DevEx/Platform
