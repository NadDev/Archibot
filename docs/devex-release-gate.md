# DevEx Release Gate (MVP)

## Objectif
Standardiser le passage en production avec un gate DevEx/Platform simple, traçable et low-cost.

## Quand l'utiliser
- a la fin de chaque Epic, avant passage final en Done
- apres verdict QE (Go ou Go with conditions)

## Ticket standard a creer
- Titre: [DEVEX] Release readiness - EPIC X.X
- Liste: Review / Validate
- Role owner: DevEx/Platform

## Checklist minimum
- build et tests CI verts
- artefact de release genere
- deploiement staging valide
- monitoring et alerting minimum actifs
- plan rollback teste
- runbook release complete

## Gate de validation
- QE: valide qualite logicielle et fonctionnelle
- DevEx/Platform: valide readiness operationnelle
- PM/PO: valide la valeur metier livree

## Regle de sortie
Un Epic ne passe en Done que si les trois validations sont presentes:
- QE
- DevEx/Platform
- PM/PO

## Format de commentaire de cloture (copier/coller)
- Epic:
- Version/Tag:
- Staging validation:
- Production release window:
- Rollback tested: Yes/No
- Monitoring checks: OK/KO
- QE verdict:
- PM/PO validation:
- Final decision: GO / NO GO