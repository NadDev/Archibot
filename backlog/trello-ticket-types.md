# Types de tickets Trello

## PM/PO
- Discovery
- User Story
- Scope Decision
- KPI Definition
- Prioritization

## Architecte logiciel
- Architecture Design
- ADR
- RAG Strategy
- Cost Strategy
- Tech Risk

## Dev
- Feature
- Integration
- Ingestion Pipeline
- Test/QA
- Bugfix

## Règle de propriété
Chaque ticket doit avoir un owner role explicite:
- PMPO
- ARCHI
- DEV

## Règle de passage entre listes
- Inbox -> Discovery: qualification PM/PO faite
- Discovery -> Ready for MVP: critères d'acceptation + dépendances complètes
- Ready for MVP -> In Progress: owner assigné et scope figé
- In Progress -> Review / Validate: implémentation terminée
- Review / Validate -> Done: validation finale effectuée
