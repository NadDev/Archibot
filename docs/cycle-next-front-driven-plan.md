# Cycle Next - Front-Driven Delivery

Date: 2026-09-28

## Objectif
Piloter la suite des features a partir des ecrans et parcours utilisateur, avec implementation back strictement alignee sur les besoins front.

## Parcours cibles MVP
1. Ecran Chat: question utilisateur, reponse structuree 3 sections.
2. Bloc Citations: preuves source visibles et compréhensibles.
3. Historique session: retrouver une question/reponse recente.

## Tickets du cycle (ordre d'execution)
1. [UXUI] Spec ecrans Chat + Citations + Historique
- Livrable: wireframes low-fidelity + etats vides/erreur/chargement.
- DoD: flux complet valide PM/PO.

2. [PMPO+ARCHI] Contrat API v1.1 front-aligne
- Livrable: payloads request/response exacts pour les 3 ecrans.
- DoD: contrat versionne et signe PM/PO + ARCHI + DEV.

3. [DEV-FRONT] Shell UI React/Vite
- Livrable: pages/composants fonctionnels relies a mock data.
- DoD: navigation complete et rendu des 3 sections + citations.

4. [DEV-BACK] Endpoints alignes contrat v1.1
- Livrable: adaptation endpoints reponse/citations/historique selon contrat.
- DoD: endpoints conformes + tests integration.

5. [QE+DEVEX] Validation e2e front->back
- Livrable: plan de tests + smoke e2e + preuve CI.
- DoD: Go/No-Go explicite, rollback planifie.

## Regle de cadence
- Aucun dev back additionnel hors contrat front valide.
- Aucun passage Done sans preuve UX + API + tests.
