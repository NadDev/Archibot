# Trello MCP

## Statut actuel du workspace
La configuration MCP Trello est déjà ajoutée dans :
- `.vscode/mcp.json` (format VS Code)
- `.mcp.json` (format portable)

Serveur configuré :
- nom : `trello`
- type : `http`
- URL : `https://mcp.trello.com/v1`

## Connexion au compte Trello (step by step)
1. Ouvrir le projet dans VS Code.
2. Vérifier que le workspace est en mode Trusted.
3. Ouvrir la Command Palette.
4. Lancer `MCP: List Servers`.
5. Sélectionner le serveur `trello`.
6. Lancer l'action de connexion / démarrage du serveur.
7. Suivre le flux OAuth dans le navigateur.
8. Choisir le workspace Trello à autoriser.
9. Donner les permissions nécessaires (lecture + écriture + recherche).
10. Revenir dans VS Code et vérifier que le serveur est en état actif.

## Vérification
- Dans `MCP: List Servers`, `trello` doit apparaître comme prêt.
- Dans le chat, les outils Trello doivent être disponibles.
- Si besoin, ouvrir la sortie MCP pour vérifier l'absence d'erreur.

## En cas de blocage
- Si le domaine MCP est bloqué par politique d'organisation, autoriser `mcp.trello.com` côté admin.
- Si permissions insuffisantes, déconnecter puis reconnecter avec droits élargis.
- Si mauvais compte Atlassian, relancer la connexion avec le bon compte Trello.

## Décision
Le projet n'utilise pas Trello à la main pour créer les tickets.
Les tickets seront créés et mis à jour via Trello MCP.

## Rôle de Trello
- suivi opérationnel
- tickets actionnables
- priorisation
- avancement
- validation

## Rôle du workspace
- mémoire du projet
- contexte produit
- décisions
- roadmap
- spécifications
- backlog maître

## Chaîne de fonctionnement
1. le workspace contient le contexte
2. l'agent lit ce contexte
3. l'agent génère des tickets structurés
4. Trello MCP crée les cartes
5. Trello sert à suivre l'exécution

## Pourquoi Trello MCP
- automatisation propre
- pas de saisie manuelle
- compatible avec les agents modernes
- création et mise à jour des cartes
- gestion de boards, listes, cartes, checklists et recherche

## Règles
- une carte = une action claire
- une carte = un livrable ou une décision
- les questions ouvertes restent visibles sur la carte
- les cartes doivent rester courtes et actionnables

## Board recommandé
- Inbox
- Discovery
- Ready for MVP
- In Progress
- Review / Validate
- Done
- Parking Lot

## Labels recommandés
- Product
- UX
- AI
- RAG
- Infra
- Trello
- Risk
- Decision
- Later
- MVP

## Format de carte
- titre orienté action
- objectif
- contexte
- dépendances
- définition de terminé
- critères de validation

## Références d'exécution
- mapping rôles -> tickets -> checklists: `docs/trello-agent-mapping.md`
- catalogue des types de tickets: `backlog/trello-ticket-types.md`
- hiérarchie de planification officielle: `backlog/lot-epic-feature-plan.md`
