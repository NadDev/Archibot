# MVP

## Statut du périmètre
Le MVP est défini en mode large : il couvre les parcours d'aide aux cours, de production de projet, d'exercices, de gestion documentaire et d'assistant RAG décrits ci-dessous. Un cycle de livraison peut n'implémenter qu'une partie de ce périmètre, sans réduire le MVP à ce cycle.

## Objectif
Livrer une application web réellement utilisable par un étudiant en architecture de 1re ou 2e année, connectée à un backend, à un LLM et à un RAG fondé sur ses documents.

## Parcours inclus
1. **Espace étudiant et projets** : retrouver ses projets, conserver un historique de conversation et des notes ou décisions utiles par projet.
2. **Cours généraux** : ajouter des cours indépendamment d'un projet, les classer par matière et année, les rechercher, les filtrer et les réviser ; sélectionner explicitement les cours à utiliser dans un projet.
3. **Documents** : importer des PDF et des notes par upload, importer un dossier choisi dans Google Drive, suivre l'indexation et comprendre les erreurs. Les images et scans simples sont inclus sous réserve d'une extraction/OCR adaptée.
4. **Compréhension des cours** : questionner ses supports, demander une explication ou une synthèse et recevoir des citations vers les passages utilisés.
5. **Aide au projet** : structurer un concept et une problématique, obtenir un retour sur la logique spatiale et un plan d'amélioration itératif, avec le contexte du projet et uniquement les cours généraux sélectionnés.
6. **Exercices** : générer des exercices ou quiz adaptés au niveau, soumettre une réponse, recevoir une correction guidée et des pistes de progression.
7. **Historique** : retrouver les échanges récents et le contexte de travail associé au compte et au projet.

## Capacités transversales
- Un assistant LLM spécialisé en pédagogie de l'architecture, utilisé pour les questions de cours, l'aide au projet, les synthèses et les exercices.
- Un RAG opérationnel dès le MVP : extraction, découpage, métadonnées, embeddings, indexation et recherche filtrée par propriétaire, projet, portée et type de source.
- Des réponses fondées sur les passages récupérés, avec citations consultables et indication explicite lorsque les documents ne permettent pas de répondre.
- Une distinction de provenance entre cours, règle générale et source réglementaire locale. L'intégration exhaustive des corpus réglementaires n'est pas requise au MVP ; une source locale indisponible doit être signalée comme telle.
- Des données persistées et isolées par compte ; aucun document privé ne doit être accessible depuis un autre compte ou un projet non autorisé.
- Une interface web déployée, avec états de chargement, d'erreur et d'absence de source.

## Non-objectifs MVP
- rendu final de projet automatisé
- multi-agents avancés
- moteur 3D
- conformité réglementaire exhaustive et ingestion complète des corpus PLU/normes
- espaces collaboratifs, rôles enseignants/tuteurs et gestion multi-utilisateur complexe
- fine-tuning de modèle

## Critères d'acceptation MVP
- Un étudiant peut se connecter, créer ou retrouver ses projets et gérer ses documents sans qu'ils soient exposés à un autre compte.
- Un PDF importé (et un fichier Drive autorisé) passe par le pipeline jusqu'à l'indexation ; l'interface expose les états de traitement et les échecs.
- Une question s'appuie sur les documents accessibles dans le contexte choisi ; chaque affirmation attribuée à un document possède une citation traçable, et l'absence de source n'est pas masquée.
- Une question dans un projet n'utilise aucun cours général sans sélection explicite. Une révision de cours reste possible sans projet ouvert.
- Les parcours de synthèse, d'aide au projet, d'exercice et de correction produisent des résultats utiles, compréhensibles et alignés sur le niveau étudiant.
- Les échanges récents et la mémoire simple du projet restent disponibles après reconnexion.
- Le build, les tests unitaires et d'intégration et les tests de parcours front-back passent en CI ; la version est déployée en staging puis en production avec supervision minimale et procédure de rollback.

## Critères de succès à mesurer
- Qualité du retrieval et exactitude des citations évaluées sur un jeu de questions de référence.
- Latence de réponse p95 cible de 8 secondes, conformément à l'ADR-001.
- Disponibilité MVP cible de 99 % hors maintenance, conformément à l'ADR-001.
- Coût IA par session et plafond mensuel définis avant le lancement public.
- Utilisabilité des parcours principaux validée avec des étudiants débutants.

## Format de réponse attendu
Quand pertinent :
- cours
- règle générale
- source réglementaire locale

## Dépendances
- workspace maître
- stack validée : React/Vite/TypeScript, FastAPI, Supabase Postgres/Storage/pgvector ; hébergement backend prévu sur Oracle Cloud pour la bêta
- choix du fournisseur et du modèle LLM, plafond de coût IA et politique de secrets
- stratégie d'ingestion et de synchronisation Google Drive (OAuth, dossier cible, fréquence, révocation)
- politique de rétention et de suppression des documents et conversations
- backlog de livraison avec critères d'acceptation par fonctionnalité
