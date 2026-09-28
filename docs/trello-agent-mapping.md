# Mapping agents vers Trello

## Objectif
Standardiser la création des tickets par rôle pour éviter les ambiguïtés et accélérer l'exécution via MCP.

## Règles globales
- Un ticket = une action vérifiable.
- Aucun ticket en In Progress sans critères d'acceptation.
- Aucun ticket en Done sans validation conjointe PM/PO + Quality Engineer.
- Chaque ticket doit mentionner le rôle propriétaire.

## Mapping par agent

### PM/PO
#### Types de tickets
- Product discovery
- Cadrage MVP
- User story
- Priorisation
- Validation valeur

#### Labels recommandés
- Product
- MVP
- Decision
- Risk

#### Checklist standard
- Problème utilisateur explicite
- Public cible précisé (1re/2e année)
- Objectif métier/pédagogique défini
- Critères d'acceptation listés
- Dépendances identifiées
- Priorité définie

#### Définition de terminé
- Ticket prêt pour revue architecte ou exécution dev.

### Architecte logiciel
#### Types de tickets
- Design architecture
- ADR
- Stratégie RAG
- Stratégie coût/performance
- Risque technique

#### Labels recommandés
- Infra
- RAG
- AI
- Decision
- Risk

#### Checklist standard
- Besoin produit de référence indiqué
- Schéma/contrat technique défini
- Impact coût estimé
- Risques listés + mitigation
- Plan de rollback/alternative si pertinent
- Effets sur provenance des réponses vérifiés

#### Définition de terminé
- Ticket prêt pour implémentation dev avec consignes techniques exploitables.

### Dev
#### Types de tickets
- Implémentation feature
- Intégration connecteur
- Pipeline ingestion
- Tests/qualité
- Correctif

#### Labels recommandés
- AI
- RAG
- UX
- Infra

#### Checklist standard
- Scope de code borné
- Critères d'acceptation recopiés
- Tests ajoutés/exécutés
- Logs minimum en place
- Contrôle provenance (cours/general/local)
- Documentation run/usage mise à jour

#### Définition de terminé
- Feature testée, conforme aux critères, prête à validation PM/PO.

### Quality Engineer
#### Types de tickets
- Revue PR
- Plan de test
- Exécution tests unitaires
- Exécution tests composant
- Exécution tests système
- Non-régression

#### Labels recommandés
- Quality
- Review
- Test
- Risk

#### Checklist standard
- PR relue avec feedback actionnable
- Critères d'acceptation vérifiés
- Tests unitaires exécutés
- Tests composant exécutés
- Tests système exécutés
- Résultats et anomalies tracés
- Verdict qualité explicite (Go / No Go)

#### Définition de terminé
- Rapport qualité prêt pour validation conjointe PM/PO + QE.

### DevEx / Platform
#### Types de tickets
- CI/CD pipeline
- Environnements dev/staging/prod
- Release / rollback
- Observabilité
- Fiabilité plateforme

#### Labels recommandés
- Platform
- DevEx
- Infra
- Release

#### Checklist standard
- Pipeline CI vert (build + tests + quality gate)
- Déploiement staging validé
- Plan de rollback prêt et testé
- Variables/secrets gérés proprement
- Monitoring/alerting minimum actifs
- Runbook mise en prod à jour

#### Définition de terminé
- Livraison déployable, observable et réversible.

## Mapping par liste Trello
- Inbox: idées brutes, demandes non qualifiées.
- Discovery: qualification PM/PO en cours.
- Ready for MVP: ticket prêt (acceptance + dépendances + rôle).
- In Progress: exécution active.
- Review / Validate: contrôle qualité/valeur (QE + PM/PO) + readiness release (DevEx/Platform).
- Done: validé.
- Parking Lot: hors scope actuel.

## Convention de titre
Format conseillé:
- [ROLE] Verbe + résultat attendu

Exemples:
- [PMPO] Figer le périmètre MVP documentaire
- [ARCHI] Définir le contrat d'indexation RAG
- [DEV] Implémenter l'import Google Drive v1

## Template de description (copier/coller)
- Role owner:
- Contexte:
- Objectif:
- Critères d'acceptation:
- Dépendances:
- Risques:
- Définition de terminé:
