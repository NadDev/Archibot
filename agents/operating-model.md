# Operating Model Multi-Agents

## Objectif
Définir une chaîne claire PM/PO -> UX/UI -> Architecte -> Dev -> Quality Engineer -> DevEx/Platform pour accélérer la livraison sans perte de qualité.

## Flux de travail
1. PM/PO formalise besoin, objectif, critères d'acceptation.
2. UX/UI traduit le besoin en parcours, écrans et critères UX.
3. Architecte challenge la solution, valide faisabilité et coût.
4. PM/PO ajuste la priorisation selon arbitrage.
5. Dev implémente et remonte feedback technique.
6. Quality Engineer réalise la revue PR et les tests qualité (unitaire, composant, système).
7. DevEx/Platform industrialise la mise en production (CI/CD, release, rollback, observabilité).
8. PM/PO et Quality Engineer valident ensemble la valeur livrée après mise en production contrôlée.

## Handoffs obligatoires
- PM/PO -> Architecte:
  - user story
  - critères d'acceptation
  - priorité
  - contraintes délais/budget
- PM/PO -> UX/UI:
  - user story
  - objectifs pédagogiques
  - priorités
- UX/UI -> Architecte:
  - parcours validés
  - exigences UI critiques
  - risques UX/complexité
- Architecte -> Dev:
  - design technique
  - contrats d'interface
  - exigences non-fonctionnelles
  - risques connus
- Dev -> Quality Engineer:
  - PR ouverte
  - contexte d'implémentation
  - tests exécutés côté dev
  - points de vigilance
- Quality Engineer -> PM/PO:
  - rapport de qualité
  - verdict de tests
  - écarts vs critères d'acceptation
- Dev -> DevEx/Platform:
  - artefact de build
  - instructions de déploiement
  - variables/env requises
- Quality Engineer -> DevEx/Platform:
  - verdict qualité
  - risques ouverts pour release
- DevEx/Platform -> PM/PO:
  - statut release
  - risques de mise en prod
  - plan de rollback
- Dev -> PM/PO:
  - statut livraison
  - écarts vs scope
  - limites constatées

## Règles de gouvernance
- toute décision structurante est tracée dans le journal des décisions
- un ticket ne passe pas en In Progress sans critères d'acceptation
- un ticket ne passe pas en Done sans validation conjointe PM/PO + Quality Engineer et release contrôlée DevEx/Platform
- les risques critiques doivent avoir un plan de mitigation

## Couplage avec Trello
- PM/PO prépare les cartes
- UX/UI annote les critères d'acceptation front
- Architecte annote les impacts techniques
- Dev met à jour le statut d'exécution
- Quality Engineer annote la revue PR, les résultats de test et le verdict qualité
- DevEx/Platform annote le statut CI/CD, release et rollback
- les checklists servent de mini-definition-of-done
