# Document maître du projet

## 1. Vision
Créer une application IA pour étudiant en architecture, ciblant principalement la 1re et la 2e année, avec une logique d'aide et de production.

Le produit doit aider l'étudiant à :
- comprendre ses cours
- structurer ses idées de projet
- améliorer ses productions
- s'exercer avec des retours guidés
- retrouver rapidement l'information utile dans ses documents

## 2. Promesse produit
L'application doit agir comme un assistant pédagogique spécialisé architecture, capable de fournir des réponses contextualisées à partir des contenus de l'étudiant plutôt que des réponses générales et vagues.

## 3. Cible
- étudiant en architecture de 1re année
- étudiant en architecture de 2e année
- éventuellement, plus tard, enseignants ou tuteurs

## 4. Périmètre MVP
### Inclus
- chat IA spécialisé architecture
- aide aux cours
- aide à la production de projet
- exercices et corrections guidées
- ingestion de documents via upload
- ingestion de documents via Google Drive
- RAG dès le démarrage
- historique et mémoire documentaire

### Exclu au MVP
- multi-agents complexes
- génération complète de projet
- gros moteur 3D / BIM
- automatisation réglementaire lourde
- fine-tuning initial
- infra coûteuse ou toujours allumée sans nécessité

## 5. Règle de réponse de l'assistant
Chaque réponse doit, quand c'est pertinent, distinguer :
- ce qui vient des cours
- ce qui relève d'une règle générale
- ce qui vient d'une source réglementaire locale

Si la source manque, l'assistant doit le dire clairement.

## 6. Stratégie documentaire
Le projet utilise un RAG dès la V1 afin de :
- réduire les réponses génériques
- exploiter les supports de cours de l'étudiant
- préparer l'ajout futur de documents externes
- garder des sources traçables

### Sources initiales
- PDF de cours
- notes de l'étudiant
- images et scans simples
- fichiers Drive

### Sources externes ultérieures
- PLU
- documents d'urbanisme
- réglementations locales
- normes et textes utiles au projet

## 7. Stratégie infra
Objectif : dépenser le moins possible sur l'infra et réserver le budget à l'IA.

Principes :
- services gratuits ou très peu coûteux en priorité
- stockage séparé des fichiers
- base vectorielle légère
- traitement asynchrone pour l'ingestion
- pas de GPU local obligatoire
- cache et résumé pour limiter les coûts de contexte

## 8. Stratégie produit
Le produit doit rester simple au départ :
- assistant unique
- orchestration simple
- valeur pédagogique claire
- amélioration itérative

## 9. Stratégie Trello
Trello ne doit pas être géré à la main.
Le projet passera par :
- un workspace maître
- un backlog documenté
- un MCP Trello pour créer et maintenir les tickets

## 10. Roadmap
Voir [roadmap](roadmap.md).

## 11. Décisions déjà actées
- RAG dès le départ
- Google Drive + upload comme sources initiales
- infra low-cost
- Trello via MCP
- architecture prévue pour les sources externes dès maintenant
- distinction obligatoire entre cours, règle générale et source locale

## 12. Prochaines étapes
1. figer l'arborescence du workspace
2. définir le MVP en détail
3. créer le board Trello via MCP
4. générer les premiers tickets
5. démarrer l'implémentation du socle technique

## 13. Modèle d'équipe multi-agents
Le projet fonctionne avec trois rôles principaux :
- PM/PO : cadre le produit, maintient le backlog, valide la valeur
- Architecte logiciel : définit l'architecture, challenge la faisabilité et les coûts
- Dev : implémente, teste et livre

Références :
- voir `agents/pm-po.agent.md`
- voir `agents/software-architect.agent.md`
- voir `agents/dev.agent.md`
- voir `agents/operating-model.md`

Règle d'exécution :
- aucun ticket en développement sans critères d'acceptation
- aucune décision structurante sans trace dans le journal des décisions
- aucun passage en Done sans validation fonctionnelle
