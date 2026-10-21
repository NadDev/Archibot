# Backend local (B1)

## Objectif
Demarrer en local sans bloquer sur l'hebergement.

## Prerequis
- Python 3.11+

## Installation
1. Creer un environnement virtuel local:
   python -m venv .venv
2. Activer l'environnement virtuel (PowerShell):
   .\.venv\Scripts\Activate.ps1
3. Mettre pip a jour:
   python -m pip install --upgrade pip
4. Installer les dependances:
   python -m pip install -r requirements.txt
5. Copier le fichier d'environnement:
   copy .env.example .env

## Lancement
python -m uvicorn app.main:app --reload --env-file .env

Note:
- Si vous installez hors venv, Windows peut afficher des warnings "script not on PATH".
- Le mode venv evite les conflits de dependances avec les packages globaux.

## Configuration Supabase (D1)
Les endpoints de retrieval, ingestion et assistant exigent un bearer token emis par Supabase Auth. Le backend le valide avec Supabase Auth puis transmet le JWT utilisateur a PostgREST pour que les policies RLS s'appliquent.

 Configurer dans `.env`:
- SUPABASE_URL
 - SUPABASE_PUBLISHABLE_KEY (cle publishable, jamais une cle service dans le frontend)
- ARCHIBOT_CHUNKS_TABLE (optionnel, defaut: chunks)
- ARCHIBOT_CORS_ORIGINS (origines frontend autorisees, separees par des virgules)

 Sans cette configuration, `/health` et `/v1/demo-response` restent disponibles, mais les endpoints proteges repondent 503. Un bearer absent ou invalide est refuse.

Pour le frontend local, autoriser `http://localhost:5173` et `http://127.0.0.1:5173`. En production, remplacer ces valeurs par les origines HTTPS exactes du frontend ; ne pas utiliser `*`.

Dans Supabase Auth, l'email est actif et la confirmation email est actuellement requise. Configurer l'URL du site et les URL de redirection locales/de production. Le formulaire impose 12 caracteres minimum ; aligner aussi la longueur minimale dans les parametres Password d'Auth. Configurer SMTP avant l'ouverture a de vrais utilisateurs pour la delivrabilite des confirmations et des resets.

 ### Perimetres de donnees
 La table privee `chunks` contient au minimum:
- owner_id (uuid, references auth.users.id)
- text (text)
- source_type (text): course | general | local_regulation
- source_id (text)
- project_id (text)
- doc_version (text)
- locality (text, nullable)
- ingested_at (timestamptz)

Exemple SQL:

create table if not exists chunks (
   id bigserial primary key,
   owner_id uuid not null references auth.users(id) on delete cascade,
   text text not null,
   source_type text not null,
   source_id text not null,
   project_id text not null,
   doc_version text not null,
   locality text,
   ingested_at timestamptz not null default now()
);

 Chaque ligne privee est limitee au couple proprietaire/projet par RLS. Les anciennes lignes dont `owner_id` est nul restent inaccessibles jusqu'a ce qu'une attribution explicite et verifiee soit faite ; ne pas les attribuer en masse a un compte arbitraire.

 Le corpus commun de connaissances generales est stocke separement dans `architecture_knowledge_chunks`. Les comptes authentifies peuvent le lire, mais seules les operations d'administration peuvent l'alimenter. L'API utilisateur ne peut pas y inserer de chunks.

## Endpoints initiaux
- GET /health
- GET /v1/demo-response
 - POST /v1/retrieval/search (Bearer Supabase Auth requis)
 - POST /v1/ingestion/chunks (Bearer Supabase Auth requis; chunks prives uniquement)
 - POST /v1/assistant/answer (Bearer Supabase Auth requis)
 - Ce module n'est pas encore expose par l'API et ne persiste ni fichiers ni chunks. Son intégration attend les métadonnées de document et le stockage objet.

## Traitement PDF (incrément initial)
- `app/document_processing.py` extrait le texte des PDF et produit des chunks indépendants par page, avec numéro de page et index du chunk.
- Les limites par défaut sont de 1 200 caractères par chunk avec 160 caractères de recouvrement ; elles sont configurables par appel.
- Les PDF invalides, vides, protégés ou sans texte extractible sont rejetés avec une erreur explicite. Les scans nécessitent une étape OCR, non incluse dans cet incrément.
- Ce module n'est pas encore exposé par l'API et ne persiste ni fichiers ni chunks. Son intégration attend l'authentification, les métadonnées de document et le stockage objet.
- `app/embeddings.py` fournit un adaptateur local FastEmbed, configuré par `FASTEMBED_MODEL`. Le modèle initial est multilingue et produit des vecteurs de 384 dimensions ; il est téléchargé au premier lancement puis exécuté localement, sans clé ni facturation par requête.
- Le fournisseur du LLM de génération reste à choisir et est indépendant du provider d'embeddings.
- Les embeddings ne sont pas encore persistés ni utilisés pour le retrieval. Ne pas activer la lecture anonyme Supabase pour des documents étudiants.
 - Les embeddings ne sont pas encore persistés ni utilisés pour le retrieval. Ne pas réintroduire d'accès anonyme Supabase aux chunks privés.

## Contrats v1
- metadata: app/schemas.py -> ChunkMetadata
- sortie assistant: app/schemas.py -> AssistantResponse
