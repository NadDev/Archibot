# Architecture cible

## Principes
- assistant unique au MVP
- orchestration simple
- RAG dès le départ
- séparation des corpus
- infrastructure low-cost

## Composants
### Frontend
Interface web simple pour :
- chat
- dépôt de fichiers
- consultation des documents indexés
- historique de travail

### Backend
API qui gère :
- authentification
- ingestion
- retrieval
- appels LLM
- stockage des métadonnées

### Stockage
- base relationnelle pour utilisateurs, documents, projets, sessions
- stockage objet pour les fichiers
- base vectorielle pour les embeddings

### Pipeline documentaire
1. upload ou import Drive
2. extraction texte
3. découpage en chunks
4. enrichissement en métadonnées
5. embeddings
6. indexation
7. retrieval au moment de la requête

## Sources
### Corpus 1
Cours et documents de l'étudiant

### Corpus 2
Connaissance générale du domaine architecture

### Corpus 3
Sources réglementaires locales et externes, intégrées plus tard

## Règle de réponse
L'agent doit distinguer :
- cours
- règle générale
- source réglementaire locale

## Stratégie coûts
- utiliser les free tiers quand c'est possible
- réserver le modèle le plus cher aux cas complexes
- utiliser un modèle plus léger pour les tâches simples
- limiter le contexte envoyé au modèle
- privilégier le résumé au stockage brut du dialogue
