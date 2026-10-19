# Feature 5.1.4 - Cours généraux transversaux

## Objectif

Permettre à un étudiant de retrouver et réviser ses cours sans devoir les rattacher à un projet, puis de réutiliser explicitement certains de ces cours comme contexte dans plusieurs projets.

## Concepts

- **Portée** : détermine où un document est disponible (`student` ou `project`).
- **Type de source** : décrit la nature de la source et sa provenance (`course`, `general`, `local_regulation`). Il est indépendant de la portée.
- **Cours général étudiant** : document de portée `student`, appartenant à un seul étudiant, consultable depuis l’espace global et non partagé avec d’autres comptes.
- **Document projet** : document de portée `project`, accessible dans son projet et non dans les autres projets par défaut.

Un cours général n’a pas de projet propriétaire. Son utilisation dans un projet ne le déplace pas et ne le copie pas : il reste dans la bibliothèque de l’étudiant.

## Parcours

### Réviser hors projet

1. Depuis la vue d’ensemble, l’étudiant ouvre **Cours généraux**.
2. Il retrouve ses cours et documents, peut en ajouter et les classer par matière et année d’étude.
3. Il ouvre un cours pour poser une question, demander une synthèse ou lancer une révision/quiz.
4. Les réponses citent les supports consultés et signalent clairement la provenance « Cours généraux ».

### Utiliser des cours dans un projet

1. Dans le chat d’un projet, les documents du projet constituent le contexte projet.
2. L’étudiant active **Ajouter des cours généraux** et choisit les cours à mobiliser.
3. La sélection est visible pendant la conversation et peut être modifiée sans déplacer les documents.
4. Les réponses distinguent les citations des cours généraux de celles des documents du projet.
5. Sans sélection, le corpus de cours généraux n’est pas inclus dans le retrieval de ce projet.

## Règles de contexte et d’accès

- L’espace de cours généraux est disponible même lorsqu’aucun projet n’existe ou n’est ouvert.
- Les cours généraux appartiennent à l’étudiant ; ils ne sont pas visibles par un autre étudiant.
- L’ajout d’un cours au contexte est explicite. Ne jamais inclure implicitement toute la bibliothèque dans un projet.
- La sélection des cours est limitée à la conversation/session, sauf décision produit ultérieure permettant de la mémoriser par projet.
- Le retrieval applique simultanément l’identité du propriétaire, la portée et la sélection de contexte. Un identifiant de projet fourni par le client ne suffit pas à autoriser l’accès.
- Les sources de type `general` (connaissance générale) restent distinctes des cours généraux personnels de l’étudiant.
- La provenance affichée indique la portée (cours général ou document du projet), le document et, si disponible, la page ou le passage cité.

## Exigences UX

- Ajouter un accès **Cours généraux** à la navigation globale, distinct de la liste des projets.
- Permettre de classer les cours par matière et année d’étude, puis de filtrer la bibliothèque par ces deux critères.
- Demander matière et année lors de l’ajout ; autoriser une matière libre et une année « Non précisée ».
- Prévoir les états vide, chargement, erreur d’ingestion et aucun résultat pertinent.
- Dans le chat projet, rendre le contrôle de sélection des cours visible, son état compréhensible et les cours sélectionnés faciles à retirer.
- Conserver un libellé de provenance distinct dans les résultats, citations et documents.
- Garder les parcours de révision utilisables sans projet actif.

## Exigences de contrat/API

Le contrat doit représenter la portée indépendamment de `source_type`, par exemple avec `scope=student|project`, un propriétaire étudiant et un `project_id` nullable/requis selon la portée. Les noms définitifs restent à valider lors du contrat API.

- Ingestion : valider la cohérence entre portée, propriétaire et projet ; un document étudiant ne doit pas avoir de projet propriétaire.
- Bibliothèque : lister les documents étudiants de l’utilisateur authentifié sans exiger de `project_id`.
- Conversation hors projet : permettre une requête de révision sans `project_id`.
- Conversation projet : recevoir la sélection explicite des identifiants de cours généraux autorisés pour cette session.
- Retrieval : récupérer les documents du projet courant et uniquement les cours généraux sélectionnés appartenant à l’utilisateur authentifié ; rejeter les références inconnues ou non autorisées.
- Citations : retourner la provenance et la portée nécessaires à l’affichage distinct dans l’interface.

Le backend actuel exige un `project_id` non vide sur les métadonnées et les requêtes de retrieval ; l’API v1.1 devra donc évoluer avant l’intégration réelle de ce parcours.

Le détail des payloads proposés, de la provenance des citations et des erreurs est défini dans [le contrat API v1.1](api-contract-v1.1-courses.md).

## Critères d’acceptation

- Un cours peut être ajouté, listé et révisé sans projet.
- Un cours général n’apparaît pas dans un projet tant que l’étudiant ne l’a pas sélectionné.
- Une réponse de projet peut citer à la fois un document projet et un cours général sélectionné, avec leur provenance clairement séparée.
- Un cours appartenant à un autre étudiant, un autre projet ou absent de la sélection ne peut pas être récupéré, même si son identifiant est fourni dans la requête.
- Les états vide, erreur et absence de source sont compréhensibles et n’impliquent pas silencieusement un changement de corpus.

## Vérifications à prévoir

- Révision avec un cours général sans projet actif.
- Question projet sans cours général sélectionné : seuls les documents du projet sont recherchés.
- Question projet avec un cours général sélectionné : les deux provenances sont rendues distinctement.
- Tentative d’utiliser un cours d’un autre utilisateur ou non sélectionné : accès refusé et aucun extrait retourné.