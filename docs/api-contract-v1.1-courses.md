# Contrat API v1.1 - Cours généraux transversaux

Statut : proposition de contrat, à valider avant implémentation.

## Principes

- `scope` décrit qui peut accéder à une source ; `source_type` décrit sa nature. Ces champs sont indépendants.
- Portées : `student` (corpus privé d'un étudiant), `project` (corpus d'un projet) et `system` (corpus partagé en lecture seule, par exemple la connaissance générale).
- L'identité de l'étudiant vient de la session authentifiée côté serveur. Aucun `owner_id` envoyé par le client ne fait autorité.
- Toute recherche vérifie l'appartenance au projet et la propriété des cours sélectionnés avant de retourner un extrait.
- Les exemples omettent les en-têtes d'authentification, qui seront définis avec le choix du mécanisme d'authentification.

## Modèles

### Document

```json
{
  "source_id": "doc-structures-ii",
  "title": "Structures II - notes de cours.pdf",
  "subject": "Structures",
  "study_year": "2e année",
  "scope": "student",
  "source_type": "course",
  "project_id": null,
  "status": "indexed",
  "page_count": 24,
  "updated_at": "2026-10-19T10:30:00Z"
}
```

`project_id` est `null` pour `student` et `system`, et obligatoire pour `project`. `owner_id` est conservé côté serveur pour les documents `student`, mais n'est pas exposé dans les requêtes publiques.

### Provenance de citation

```json
{
  "source_id": "doc-structures-ii",
  "title": "Structures II - notes de cours.pdf",
  "scope": "student",
  "source_type": "course",
  "page": 18,
  "excerpt": "La stabilité dépend du système porteur et de son contreventement.",
  "score": 0.91
}
```

`page` est nullable quand la source n'a pas de pagination. Les trois premières propriétés permettent de distinguer un cours personnel d'un document projet ou d'une source système.

## Endpoints

### Lister les documents d'un corpus

`GET /v1/documents?scope=student&subject=Structures&study_year=2e%20ann%C3%A9e`

La portée `student` retourne uniquement les documents de l'utilisateur authentifié. `subject` et `study_year` sont des filtres optionnels combinables ; omettre l'un ou l'autre signifie « toutes les valeurs ». `scope=project` exige aussi `project_id`. Les sources `system` ne sont pas listées dans la bibliothèque personnelle.

Réponse `200` :

```json
{
  "items": [
    {
      "source_id": "doc-structures-ii",
      "title": "Structures II - notes de cours.pdf",
      "subject": "Structures",
      "study_year": "2e année",
      "scope": "student",
      "source_type": "course",
      "project_id": null,
      "status": "indexed",
      "page_count": 24,
      "updated_at": "2026-10-19T10:30:00Z"
    }
  ],
  "total": 1
}
```

### Ajouter un document

`POST /v1/documents` en `multipart/form-data`, avec `file`, `scope`, `subject`, `study_year` et `title` optionnel. `subject` est une chaîne libre normalisée côté serveur ; `study_year` est une valeur de catalogue (`1re année`, `2e année`, `Transversale`, `Non précisée`). Pour `scope=student`, `project_id` est absent. Pour `scope=project`, `project_id` est obligatoire et vérifié côté serveur. Le type de source est `course` pour les cours personnels ; le serveur renvoie un document en état `processing`, puis `indexed` ou `failed`.

Réponse `202` :

```json
{
  "document": {
    "source_id": "doc-structures-ii",
    "title": "Structures II - notes de cours.pdf",
    "subject": "Structures",
    "study_year": "2e année",
    "scope": "student",
    "source_type": "course",
    "project_id": null,
    "status": "processing",
    "page_count": null,
    "updated_at": "2026-10-19T10:30:00Z"
  }
}
```

### Réviser un ou plusieurs cours sans projet

`PATCH /v1/documents/{source_id}` permet de modifier `subject` et/ou `study_year` après import. La propriété du document est vérifiée côté serveur et la bibliothèque reflète ensuite les valeurs modifiées.
`PATCH /v1/documents/{source_id}` permet de modifier `subject` et/ou `study_year` après import. La propriété du document est vérifiée côté serveur et la bibliothèque reflète ensuite les valeurs modifiées.

Corps JSON (au moins un champ) :

```json
{
  "subject": "Structures",
  "study_year": "2e année"
}
```

`POST /v1/assistant/answer`

```json
{
  "question": "Explique le contreventement et interroge-moi sur cette notion.",
  "context": {
    "mode": "course_review",
    "project_id": null,
    "course_source_ids": ["doc-structures-ii"]
  },
  "top_k": 5,
  "locality": null
}
```

Pour `course_review`, au moins un `course_source_id` est requis et chaque document doit appartenir à l'utilisateur authentifié. Une requête sans projet ne recherche aucun document projet.

### Poser une question dans un projet

`POST /v1/assistant/answer`

```json
{
  "question": "Comment le contreventement peut-il guider la trame de mon pavillon ?",
  "context": {
    "mode": "project",
    "project_id": "pavillon-campus",
    "course_source_ids": ["doc-structures-ii"]
  },
  "top_k": 5,
  "locality": "paris"
}
```

Une liste `course_source_ids` vide (ou omise) signifie qu'aucun cours général personnel n'est inclus. Le serveur recherche dans le projet autorisé, les seuls cours personnels explicitement sélectionnés, et les sources `system` applicables.

Pour `mode=project`, `project_id` est obligatoire. Pour `mode=course_review`, il doit être `null`. Toute combinaison incohérente est rejetée avec `422`.

### Réponse assistant

Réponse `200`, compatible avec les trois sections existantes ; `schema_version` devient `v1.1`. Chaque citation inclut la provenance :

```json
{
  "schema_version": "v1.1",
  "cours": {
    "text": "Le contreventement stabilise la structure ; dans ton projet, compare-le à la trame choisie.",
    "citations": [
      {
        "source_id": "doc-structures-ii",
        "title": "Structures II - notes de cours.pdf",
        "scope": "student",
        "source_type": "course",
        "page": 18,
        "excerpt": "La stabilité dépend du système porteur et de son contreventement.",
        "score": 0.91
      },
      {
        "source_id": "pavillon-brief",
        "title": "Programme pavillon.pdf",
        "scope": "project",
        "source_type": "course",
        "page": 2,
        "excerpt": "Le pavillon accueille des espaces de travail partagés.",
        "score": 0.82
      }
    ]
  },
  "regle_generale": {
    "text": "Une trame régulière peut simplifier la coordination entre structure et usages.",
    "citations": []
  },
  "source_reglementaire_locale": {
    "text": "Aucune source réglementaire locale disponible pour cette requête.",
    "citations": []
  },
  "warning_no_source": null
}
```

Les réponses conservent les textes de repli existants quand une section n'a pas de source. La portée des citations reste disponible même si une réponse agrège plusieurs corpus dans une section.

## Ingestion des chunks

`POST /v1/ingestion/chunks` ajoute `scope` aux métadonnées. `owner_id` est déterminé depuis l'identité authentifiée, jamais depuis le corps de la requête.

```json
{
  "chunks": [
    {
      "text": "La stabilité dépend du système porteur.",
      "metadata": {
        "source_type": "course",
        "source_id": "doc-structures-ii",
        "scope": "student",
        "project_id": null,
        "doc_version": "v1",
        "locality": null,
        "ingested_at": "2026-10-19T10:30:00Z"
      }
    }
  ]
}
```

Les contraintes de stockage doivent imposer : `student` => propriétaire authentifié et `project_id IS NULL` ; `project` => projet existant et autorisé ; `system` => ingestion réservée aux opérations d'administration.

## Erreurs attendues

- `401` : session absente ou invalide.
- `403` : projet non accessible ou document étudiant appartenant à un autre utilisateur.
- `404` : document demandé inexistant ou non visible pour l'utilisateur.
- `422` : portée, mode de contexte et identifiants incompatibles.

Pour éviter de révéler l'existence d'un document privé, les références non visibles peuvent être renvoyées comme `404` de façon cohérente.

## Évolution et compatibilité

- Les routes existantes restent sous `/v1`; cette proposition enrichit le contrat, et `schema_version` de réponse passe à `v1.1`.
- Les champs `project_id` actuels ne peuvent pas devenir simplement nullable sans ajouter la validation `scope` et les contrôles d'accès.
- Les données existantes doivent être migrées vers `scope=project` avant de rendre `project_id` nullable ; leur rattachement actuel ne doit pas être deviné.
- L'authentification/autorisation et la migration SQL sont des prérequis au branchement réel. Le frontend peut utiliser ce contrat avec des données fictives en attendant.

## Tests de contrat requis

- Révision sans projet avec un document de l'utilisateur : accepté, citation `scope=student`.
- Révision sans projet avec un document projet : aucun document projet récupéré.
- Projet sans cours sélectionné : aucun cours personnel récupéré.
- Projet avec cours de l'utilisateur sélectionné : cours et documents projet cités avec leurs portées respectives.
- Document étudiant d'un autre utilisateur, projet non autorisé ou document non sélectionné : aucun extrait privé retourné.
- `scope`, `project_id` et `context.mode` incompatibles : `422`.